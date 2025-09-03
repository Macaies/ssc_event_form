// Simple floating tooltip element we reuse
let tipEl;
function getTip() {
  if (!tipEl) {
    tipEl = document.createElement("div");
    tipEl.className = "fc-mini-tip";
    document.body.appendChild(tipEl);
  }
  return tipEl;
}
function showTip(html, x, y) {
  const tip = getTip();
  tip.innerHTML = html;
  // position near cursor (with small offset)
  const pad = 12;
  tip.style.left = `${x + pad}px`;
  tip.style.top  = `${y + pad}px`;
  tip.classList.add("show");
}
function moveTip(x, y) {
  if (!tipEl) return;
  const pad = 12;
  tipEl.style.left = `${x + pad}px`;
  tipEl.style.top  = `${y + pad}px`;
}
function hideTip() {
  if (!tipEl) return;
  tipEl.classList.remove("show");
}

document.addEventListener("DOMContentLoaded", function() {
  const calendarEl = document.getElementById("calendar");
  if (!calendarEl || !window.FullCalendar) return;

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    height: "auto",
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "dayGridMonth,timeGridWeek,timeGridDay,listWeek"
    },
    navLinks: true,
    nowIndicator: true,
    displayEventTime: true,
    eventTimeFormat: { hour: "2-digit", minute: "2-digit", hour12: false },

    // Pull events from backend
    events: "/api/events",

    // Add richer hover tooltip
    eventMouseEnter(info) {
      const ev = info.event;
      const p  = ev.extendedProps || {};
      const location = (p.location || "").toString();
      const status = (p.status || "").toString();
      const classification = (p.classification || "").toString();

      const start = ev.start ? ev.start.toLocaleString([], { dateStyle: "medium", timeStyle: "short" }) : "";
      const end   = ev.end   ? ev.end.toLocaleString([], { dateStyle: "medium", timeStyle: "short" })   : "";

      const html = `
        <span class="tip-title">${ev.title}</span>
        <div class="tip-meta">
          <div><strong>Status:</strong> ${status}</div>
          <div><strong>Classification:</strong> ${classification}</div>
          ${location ? `<div><strong>Location:</strong> ${location}</div>` : ""}
          <div><strong>Start:</strong> ${start}</div>
          <div><strong>End:</strong> ${end}</div>
        </div>
      `;
      // mouse position from the native event (fallback to element)
      const x = info.jsEvent?.clientX ?? (info.el.getBoundingClientRect().left + 10);
      const y = info.jsEvent?.clientY ?? (info.el.getBoundingClientRect().top + 10);
      showTip(html, x, y);
    },
    eventMouseLeave() {
      hideTip();
    },
    eventMouseMove(info) {
      // follow cursor
      const x = info.jsEvent?.clientX;
      const y = info.jsEvent?.clientY;
      if (typeof x === "number" && typeof y === "number") moveTip(x, y);
    },

    // Optional: click to show a simple alert with full details
    eventClick(info) {
      const ev = info.event;
      const p  = ev.extendedProps || {};
      const details = [
        `Title: ${ev.title}`,
        `Status: ${p.status || ""}`,
        `Classification: ${p.classification || ""}`,
        `Location: ${p.location || ""}`,
        `Start: ${ev.start ? ev.start.toLocaleString() : ""}`,
        `End: ${ev.end ? ev.end.toLocaleString() : ""}`
      ].join("\n");
      alert(details);
    },

    // Improve colors: we already pass className (fc-approved / fc-pending / fc-rejected)
    eventClassNames(arg) {
      // arg.event.classNames already has the server-provided class
      return arg.event.classNames;
    }
  });

  calendar.render();

  // Ensure tooltip hides on scroll or when clicking elsewhere
  ['scroll', 'wheel'].forEach(evt =>
    window.addEventListener(evt, hideTip, { passive: true })
  );
  document.addEventListener('click', hideTip);
});
