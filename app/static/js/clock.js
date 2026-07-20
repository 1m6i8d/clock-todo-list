/*
  Clock — circular day view.
  Renders a 24-hour clock chart into an <svg id="clock-svg"> and a
  legend into <div id="clock-legend">. Non-overlapping tasks draw as
  full-radius wedges; overlapping tasks nest as smaller wedges layered
  on top of the same angular span.

  Hands (hour + minute) and the "current task" glow update every
  second via a separate lightweight loop — the wedges/legend are only
  drawn once, so they don't replay their entrance animation on a timer.

  Hovering a wedge shows a custom tooltip (#clock-tooltip) with the
  task's title, time range, and category.

  Usage: renderClock(tasks) where tasks is an array of
  { title, category, start, end, color? } with start/end as decimal
  hours (0-24). `color` is optional — omit it to use the category map.
*/

const SVG_NS = "http://www.w3.org/2000/svg";
let _wedgeRefs = [];   // [{ path, task }]
let _legendRefs = [];  // [{ el, task }]
let _tickStarted = false;

const CATEGORY_COLORS = {
  Health: "#2F5A45",
  Work: "#5B7FB5",
  Home: "#D98A3D",
  Personal: "#7B6A9C",
};
const DEFAULT_COLOR = "#8A8778";

function colorFor(task) {
  return task.color || CATEGORY_COLORS[task.category] || DEFAULT_COLOR;
}

function hourToAngle(h) {
  return (h / 24) * 360 - 90;
}

function polar(cx, cy, r, angleDeg) {
  const rad = (angleDeg * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function wedgePath(cx, cy, r, startAngle, endAngle) {
  const start = polar(cx, cy, r, startAngle);
  const end = polar(cx, cy, r, endAngle);
  const largeArc = endAngle - startAngle > 180 ? 1 : 0;
  return `M ${cx} ${cy} L ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y} Z`;
}

function assignLayers(tasks) {
  const sorted = [...tasks].sort(
    (a, b) => a.start - b.start || (b.end - b.start) - (a.end - a.start)
  );
  const active = [];
  return sorted.map(task => {
    for (let i = active.length - 1; i >= 0; i--) {
      if (active[i].end <= task.start) active.splice(i, 1);
    }
    const usedLayers = active.map(t => t.layer);
    let layer = 0;
    while (usedLayers.includes(layer)) layer++;
    const withLayer = { ...task, layer };
    active.push(withLayer);
    return withLayer;
  });
}

function fmtTime(h) {
  const hh = Math.floor(h).toString().padStart(2, "0");
  const mm = Math.round((h % 1) * 60).toString().padStart(2, "0");
  return `${hh}:${mm}`;
}

function nowDecimalHours() {
  const d = new Date();
  return d.getHours() + d.getMinutes() / 60 + d.getSeconds() / 3600;
}

// ---------- tooltip ----------

function showTooltip(task, clientX, clientY) {
  const tooltip = document.getElementById("clock-tooltip");
  const wrap = document.getElementById("clock-wrap");
  if (!tooltip || !wrap) return;

  tooltip.innerHTML = `
    <div class="tooltip-title">${task.title}</div>
    <div class="tooltip-time">${fmtTime(task.start)} – ${fmtTime(task.end)}</div>
    ${task.category ? `<div class="tooltip-category">${task.category}</div>` : ""}
  `;
  tooltip.style.display = "block";
  moveTooltip(clientX, clientY);
}

function moveTooltip(clientX, clientY) {
  const tooltip = document.getElementById("clock-tooltip");
  const wrap = document.getElementById("clock-wrap");
  if (!tooltip || !wrap) return;
  const rect = wrap.getBoundingClientRect();
  const x = clientX - rect.left;
  const y = clientY - rect.top;
  tooltip.style.left = `${x + 14}px`;
  tooltip.style.top = `${y + 14}px`;
}

function hideTooltip() {
  const tooltip = document.getElementById("clock-tooltip");
  if (tooltip) tooltip.style.display = "none";
}

// ---------- static render (runs once per data change) ----------

function renderClock(tasks) {
  const svg = document.getElementById("clock-svg");
  const legend = document.getElementById("clock-legend");
  if (!svg) return;
  svg.setAttribute("viewBox", "0 0 320 320");
  svg.innerHTML = "";
  if (legend) legend.innerHTML = "";
  _wedgeRefs = [];
  _legendRefs = [];

  const cx = 160, cy = 160, rOuter = 136;
  const layered = assignLayers(tasks || []);
  const maxLayer = Math.max(0, ...layered.map(t => t.layer));
  const layerStep = maxLayer > 0 ? (rOuter * 0.32) / maxLayer : 0;

  // glow filter, used by whichever wedge is "current"
  const defs = document.createElementNS(SVG_NS, "defs");
  const filter = document.createElementNS(SVG_NS, "filter");
  filter.setAttribute("id", "current-glow");
  filter.setAttribute("x", "-60%"); filter.setAttribute("y", "-60%");
  filter.setAttribute("width", "220%"); filter.setAttribute("height", "220%");
  const blur = document.createElementNS(SVG_NS, "feGaussianBlur");
  blur.setAttribute("in", "SourceGraphic");
  blur.setAttribute("stdDeviation", "6");
  blur.setAttribute("result", "blurred");
  const merge = document.createElementNS(SVG_NS, "feMerge");
  const mergeNode1 = document.createElementNS(SVG_NS, "feMergeNode");
  mergeNode1.setAttribute("in", "blurred");
  const mergeNode2 = document.createElementNS(SVG_NS, "feMergeNode");
  mergeNode2.setAttribute("in", "SourceGraphic");
  merge.appendChild(mergeNode1);
  merge.appendChild(mergeNode2);
  filter.appendChild(blur);
  filter.appendChild(merge);
  defs.appendChild(filter);
  svg.appendChild(defs);

  // background ring
  const bg = document.createElementNS(SVG_NS, "circle");
  bg.setAttribute("cx", cx); bg.setAttribute("cy", cy); bg.setAttribute("r", rOuter);
  bg.setAttribute("fill", "#EDEAE0");
  svg.appendChild(bg);

  // empty state
  if (!tasks || tasks.length === 0) {
    const text = document.createElementNS(SVG_NS, "text");
    text.setAttribute("x", cx);
    text.setAttribute("y", cy);
    text.setAttribute("font-size", "13");
    text.setAttribute("font-family", "Inter, sans-serif");
    text.setAttribute("fill", "#8A8778");
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("dominant-baseline", "central");
    text.textContent = "No tasks yet";
    svg.appendChild(text);
  }

  // hour ticks + labels
  for (let h = 0; h < 24; h++) {
    const angle = hourToAngle(h);
    const inner = polar(cx, cy, rOuter - 5, angle);
    const outer = polar(cx, cy, rOuter, angle);
    const line = document.createElementNS(SVG_NS, "line");
    line.setAttribute("x1", inner.x); line.setAttribute("y1", inner.y);
    line.setAttribute("x2", outer.x); line.setAttribute("y2", outer.y);
    line.setAttribute("stroke", "#C9C5B6");
    line.setAttribute("stroke-width", "1");
    svg.appendChild(line);

    if (h % 6 === 0) {
      const labelPos = polar(cx, cy, rOuter + 14, angle);
      const text = document.createElementNS(SVG_NS, "text");
      text.setAttribute("x", labelPos.x);
      text.setAttribute("y", labelPos.y);
      text.setAttribute("font-size", "10");
      text.setAttribute("font-family", "IBM Plex Mono, monospace");
      text.setAttribute("fill", "#8A8778");
      text.setAttribute("text-anchor", "middle");
      text.setAttribute("dominant-baseline", "central");
      text.textContent = String(h).padStart(2, "0") + ":00";
      svg.appendChild(text);
    }
  }

  // task wedges — layer 0 first, overlaps drawn on top, animated in once
  const sortedByLayerAsc = [...layered].sort((a, b) => a.layer - b.layer);
  sortedByLayerAsc.forEach((task, i) => {
    const r = rOuter - task.layer * layerStep;
    const path = document.createElementNS(SVG_NS, "path");
    path.setAttribute("d", wedgePath(cx, cy, r, hourToAngle(task.start), hourToAngle(task.end)));
    path.setAttribute("fill", colorFor(task));
    path.setAttribute("stroke", "#fff");
    path.setAttribute("stroke-width", "1.5");
    path.setAttribute("opacity", "0.92");
    path.setAttribute("class", "clock-svg-wedge");
    path.style.animationDelay = `${i * 0.05}s`;
    path.style.cursor = "pointer";

    path.addEventListener("mouseenter", e => showTooltip(task, e.clientX, e.clientY));
    path.addEventListener("mousemove", e => moveTooltip(e.clientX, e.clientY));
    path.addEventListener("mouseleave", hideTooltip);

    svg.appendChild(path);
    _wedgeRefs.push({ path, task });
  });

  // center hub
  const centerHole = document.createElementNS(SVG_NS, "circle");
  centerHole.setAttribute("cx", cx); centerHole.setAttribute("cy", cy); centerHole.setAttribute("r", 4);
  centerHole.setAttribute("fill", "#fff");
  centerHole.setAttribute("stroke", "#2F5A45");
  centerHole.setAttribute("stroke-width", "1.5");
  svg.appendChild(centerHole);

  // hour + minute hands (positioned immediately, then kept live by updateHands)
  const hourHand = document.createElementNS(SVG_NS, "line");
  hourHand.setAttribute("id", "hour-hand");
  hourHand.setAttribute("x1", cx); hourHand.setAttribute("y1", cy);
  hourHand.setAttribute("stroke", "#23261F");
  hourHand.setAttribute("stroke-width", "3");
  hourHand.setAttribute("stroke-linecap", "round");
  svg.appendChild(hourHand);

  const minuteHand = document.createElementNS(SVG_NS, "line");
  minuteHand.setAttribute("id", "minute-hand");
  minuteHand.setAttribute("x1", cx); minuteHand.setAttribute("y1", cy);
  minuteHand.setAttribute("stroke", "#23261F");
  minuteHand.setAttribute("stroke-width", "1.8");
  minuteHand.setAttribute("stroke-linecap", "round");
  minuteHand.setAttribute("opacity", "0.7");
  svg.appendChild(minuteHand);

  // legend
  if (legend) {
    layered.forEach(task => {
      const item = document.createElement("div");
      item.className = "legend-item";
      item.innerHTML = `<span class="swatch" style="background:${colorFor(task)}"></span>${task.title} (${fmtTime(task.start)}-${fmtTime(task.end)})`;
      legend.appendChild(item);
      _legendRefs.push({ el: item, task });
    });
  }

  updateHands(); // position hands immediately, don't wait for the first tick

  if (!_tickStarted) {
    _tickStarted = true;
    setInterval(updateHands, 1000); // true per-second movement
  }
}

// ---------- live updater (runs every second, touches only hands + glow) ----------

function updateHands() {
  const svg = document.getElementById("clock-svg");
  if (!svg) return;
  const cx = 160, cy = 160, rOuter = 136;
  const now = nowDecimalHours();

  const hourAngle = hourToAngle(now); // one full rotation per 24h, matches wedge scale
  const minutes = (now % 1) * 60;
  const minuteAngle = (minutes / 60) * 360 - 90; // one full rotation per hour

  const hourHand = document.getElementById("hour-hand");
  if (hourHand) {
    const end = polar(cx, cy, rOuter * 0.5, hourAngle);
    hourHand.setAttribute("x2", end.x);
    hourHand.setAttribute("y2", end.y);
  }

  const minuteHand = document.getElementById("minute-hand");
  if (minuteHand) {
    const end = polar(cx, cy, rOuter * 0.74, minuteAngle);
    minuteHand.setAttribute("x2", end.x);
    minuteHand.setAttribute("y2", end.y);
  }

  // toggle the "current task" glow/emphasis without touching wedge geometry
  _wedgeRefs.forEach(({ path, task }) => {
    const isCurrent = now >= task.start && now < task.end;
    path.setAttribute("stroke-width", isCurrent ? "2.5" : "1.5");
    path.setAttribute("opacity", isCurrent ? "1" : "0.92");
    if (isCurrent) {
      path.setAttribute("filter", "url(#current-glow)");
    } else {
      path.removeAttribute("filter");
    }
  });

  _legendRefs.forEach(({ el, task }) => {
    const isCurrent = now >= task.start && now < task.end;
    el.classList.toggle("current", isCurrent);
  });
}