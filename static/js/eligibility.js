// Client-side mirror of server rules (Option B)
(function () {
  const $ = (sel) => document.querySelector(sel);

  window.renderEligibilitySummary = function () {
    const rules = [];

    // collect values
    const attendance = parseInt($("input[name='attendance']")?.value || "0", 10);
    const building  = $("select[name='building_approval']")?.value || "No";
    const piercing  = $("select[name='ground_piercing']")?.value || "No";
    const traffic   = $("select[name='traffic_mgmt']")?.value || "No";
    const duration  = $("select[name='duration']")?.value || "";
    const highrisk  = $("select[name='high_risk']")?.value || "No";
    const stime     = $("input[name='start_time']")?.value || "";
    const ftime     = $("input[name='finish_time']")?.value || "";
    const alcohol   = $("select[name='alcohol']")?.value || "No";
    const noise     = $("select[name='noise']")?.value || "No";
    const vehicle   = $("select[name='vehicle_access']")?.value || "No";
    const verge     = $("select[name='verge_traverse']")?.value || "No";

    function add(ok, text) { rules.push({ ok, text }); }

    add(attendance < 200, "Less than 200 attendees");
    add(building === "No" && piercing === "No", "No building approval/ground piercing");
    add(traffic === "No", "No traffic management / road closures");
    add(duration === "<=2 days" || duration === "<=12 days",
        "≤2 consecutive days OR ≤12 non-consecutive days in 12 months");
    add(highrisk === "No", "No firearms, fireworks or other high-risk activities");
    add(stime >= "05:30", "Starts after 5:30am (or 7:00am if amplified)");
    add(!ftime || ftime <= "22:00", "Finishes by 10:00pm");
    add(alcohol === "No", "No alcohol service or consumption");
    add(noise === "No", "No amplified noise above 95dBC @ 15m");
    add(vehicle === "No", "No vehicle/machinery access to public space");
    add(verge === "No", "No traversing over verge/kerb/path with vehicles");

    const list = document.getElementById("summary-list");
    const badge = document.getElementById("eligibility-badge");
    list.innerHTML = "";

    let allOk = true;
    rules.forEach(r => {
      const li = document.createElement("li");
      li.textContent = r.text;
      li.className = r.ok ? "ok" : "fail";
      if (!r.ok) allOk = false;
      list.appendChild(li);
    });

    badge.textContent = allOk ? "Self-assessable ✅" : "Assessable by SCC 🟡";
    badge.className = "badge " + (allOk ? "ok" : "warn");
  };
})();
