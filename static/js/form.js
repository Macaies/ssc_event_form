// ------- multi-step form wiring -------
const form = document.querySelector("#multiStepForm");
const formSteps = document.querySelectorAll(".form-step");
const btnNext = document.querySelectorAll(".btn-next");
const btnPrev = document.querySelectorAll(".btn-prev");
let formStepIndex = 0;

function showStep(i) {
  formSteps.forEach((s, idx) => {
    s.style.display = idx === i ? "block" : "none";
    if (idx === i) s.classList.add("active"); else s.classList.remove("active");

    // remove required from hidden steps to avoid blocking validation
    Array.from(s.querySelectorAll("[required]")).forEach(el => {
      if (idx !== i) { el.dataset._req = "1"; el.removeAttribute("required"); }
    });
  });
  // restore required on visible step
  Array.from(formSteps[i].querySelectorAll("[data-_req='1']")).forEach(el => {
    el.setAttribute("required", "required");
    delete el.dataset._req;
  });

  // progress bar
  const pips = document.querySelectorAll(".progress-step");
  pips.forEach((p, idx) => p.classList.toggle("active", idx <= i));

  // if we just showed Step 2 (index 1), ensure the map is initialized and sized
  if (i === 1) {
    initMapOnce();
    // give the browser a tick to lay out, then fix tile sizing
    setTimeout(invalidateMapSize, 50);
    setTimeout(invalidateMapSize, 300);
  }

  // if we showed the summary, refresh it
  if (i === formSteps.length - 1) {
    buildSummary();
    updateClassificationPreview();
  }
}

function validateStep(i) {
  const step = formSteps[i];
  if (!step) return true;
  const required = step.querySelectorAll("[required]");
  for (const el of required) {
    if (!el.value || (el.type === "checkbox" && !el.checked)) {
      el.focus();
      return false;
    }
  }
  return true;
}

btnNext.forEach(b => b.addEventListener("click", e => {
  e.preventDefault();
  if (!validateStep(formStepIndex)) return;
  if (formStepIndex < formSteps.length - 1) {
    formStepIndex++;
    showStep(formStepIndex);
  }
}));

btnPrev.forEach(b => b.addEventListener("click", e => {
  e.preventDefault();
  if (formStepIndex > 0) {
    formStepIndex--;
    showStep(formStepIndex);
  }
}));

// Enter key → next step (except last step where it submits)
form.addEventListener("keydown", (e) => {
  if (e.key !== "Enter") return;
  const tag = (e.target.tagName || "").toLowerCase();
  const type = (e.target.type || "").toLowerCase();
  if (tag === "textarea" || type === "file") return;

  if (formStepIndex < formSteps.length - 1) {
    e.preventDefault();
    if (!validateStep(formStepIndex)) return;
    formStepIndex++;
    showStep(formStepIndex);
  } else {
    if (!validateStep(formStepIndex)) e.preventDefault();
  }
});

function buildSummary() {
  const out = document.getElementById("checklist-summary");
  if (!out) return;
  const v = id => document.getElementById(id)?.value || "";
  const rows = [
    ["Event Name", v("event_name")],
    ["Venue", v("venue")],
    ["Start", `${v("start_date")} ${v("start_time")}`.trim()],
    ["End", `${v("end_date")} ${v("end_time")}`.trim()],
    ["Attendance", v("attendance")],
  ];
  out.innerHTML = rows.map(([k,val]) => `<li><strong>${k}:</strong> ${val || "-"}</li>`).join("");
}

function getClassificationFromForm() {
  const attendance = parseInt(document.getElementById("attendance")?.value || "0", 10);
  const alcohol = (document.querySelector("select[name='alcohol']")?.value || "No");
  const high_risk = (document.querySelector("select[name='high_risk']")?.value || "No");
  const traffic = (document.querySelector("select[name='traffic_mgmt']")?.value || "No");
  const vehicle_access = (document.querySelector("select[name='vehicle_access']")?.value || "No");
  const amplified = (document.querySelector("select[name='amplified_sound']")?.value || "No");
  const noise_level = parseInt(document.getElementById("noise_level")?.value || "0", 10);
  const total_days = parseInt(document.getElementById("total_days")?.value || "1", 10);

  let classification = "Self-assessable";
  if (attendance >= 200) classification = "Assessable";
  if (alcohol === "Yes") classification = "Assessable";
  if (high_risk === "Yes") classification = "Assessable";
  if (traffic === "Yes") classification = "Assessable";
  if (vehicle_access === "Yes") classification = "Assessable";
  if (amplified === "Yes" && noise_level > 95) classification = "Assessable";
  if (total_days > 2) classification = "Assessable";
  return classification;
}

function updateClassificationPreview() {
  const el = document.getElementById("classification-result");
  if (!el) return;
  el.textContent = getClassificationFromForm();
}

// init first step
showStep(0);

// ---------- Conflict check helper ----------
async function checkConflict() {
  const v = id => document.getElementById(id)?.value || "";
  const body = {
    start_date: v("start_date"),
    end_date:   v("end_date") || v("start_date"),
    start_time: v("start_time"),
    end_time:   v("end_time"),
    venue:      v("venue"),
    location:   v("venue"),
    arcgis_feature_id: v("arcgis_feature_id")
  };
  if (!body.start_date || !body.start_time || !body.end_time || (!body.venue && !body.arcgis_feature_id)) {
    showConflict(null);
    return;
  }
  try {
    const resp = await fetch("/api/check_conflict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const data = await resp.json();
    showConflict(!!data.conflict);
  } catch {
    showConflict(null);
  }
}

function showConflict(conflict) {
  const banner = document.getElementById("conflict-banner");
  if (!banner) return;
  if (conflict === null) { banner.textContent = ""; banner.style = ""; return; }

  if (conflict) {
    banner.textContent = "⚠️ A booking already exists at this place & time. Your submission will be marked Pending.";
    banner.style.background = "#fff3cd";
    banner.style.border = "1px solid #ffeeba";
    banner.style.color = "#7c5b00";
    banner.style.padding = "10px";
    banner.style.borderRadius = "8px";
  } else {
    banner.textContent = "✓ This slot looks available.";
    banner.style.background = "#e8f5e9";
    banner.style.border = "1px solid #c8e6c9";
    banner.style.color = "#1b5e20";
    banner.style.padding = "10px";
    banner.style.borderRadius = "8px";
  }
}

// re-check conflict when these change
["start_date","end_date","start_time","end_time","venue","arcgis_feature_id"].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener("change", checkConflict);
});

// ------- Map: lazy init on Step 2 -------
let mapInitialized = false;
let leafletMap = null, leafletMarker = null;

function initMapOnce() {
  if (mapInitialized) return;
  mapInitialized = true;

  const mapEl = document.getElementById("map");
  if (!mapEl) return;

  const venueInput = document.getElementById("venue");
  const latInput   = document.getElementById("latitude");
  const lonInput   = document.getElementById("longitude");
  const fidInput   = document.getElementById("arcgis_feature_id");
  const fnameInput = document.getElementById("arcgis_feature_name");
  const layerInput = document.getElementById("arcgis_layer");

  // Try Google first
  const gkeyMeta = document.querySelector("meta[name='gmaps-api-key']");
  const gmapsKey = gkeyMeta ? gkeyMeta.content : "";

  if (gmapsKey) {
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${gmapsKey}&libraries=places`;
    script.async = true;
    script.onload = () => initGoogle();
    document.head.appendChild(script);

    function initGoogle() {
      const center = { lat: -26.65, lng: 153.06 };
      const gmap = new google.maps.Map(mapEl, { center, zoom: 10, mapTypeControl: false, streetViewControl: false });
      const marker = new google.maps.Marker({ map: gmap, draggable: false });
      const geocoder = new google.maps.Geocoder();

      const ac = new google.maps.places.Autocomplete(venueInput, { fields: ["geometry","formatted_address","name"] });
      ac.addListener("place_changed", () => {
        const place = ac.getPlace();
        if (place.geometry && place.geometry.location) {
          const loc = place.geometry.location;
          setPoint(loc.lat(), loc.lng(), place.formatted_address || place.name || venueInput.value);
          gmap.setCenter(loc); gmap.setZoom(16);
        }
      });

      async function setPoint(lat, lng, maybeAddress) {
        marker.setPosition({ lat, lng });
        latInput.value = (+lat).toFixed(6);
        lonInput.value = (+lng).toFixed(6);
        fidInput.value = ""; fnameInput.value = ""; layerInput.value = "";

        if (!venueInput.value && maybeAddress) {
          venueInput.value = maybeAddress;
        }
        checkConflict();
      }

      gmap.addListener("click", (e) => setPoint(e.latLng.lat(), e.latLng.lng()));

      // Find on map button
      document.getElementById("btnFindOnMap")?.addEventListener("click", () => {
        const q = venueInput.value.trim();
        if (!q) return;
        geocoder.geocode({ address: q }, (results, status) => {
          if (status === "OK" && results[0]) {
            const loc = results[0].geometry.location;
            setPoint(loc.lat(), loc.lng(), results[0].formatted_address);
            gmap.setCenter(loc); gmap.setZoom(16);
          }
        });
      });
    }
    return;
  }

  // Leaflet fallback
  if (window.L) {
    const center = [-26.65, 153.06];
    leafletMap = L.map(mapEl).setView(center, 10);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19, attribution: "&copy; OpenStreetMap contributors"
    }).addTo(leafletMap);

    leafletMap.on("click", async (e) => {
      setPoint(e.latlng.lat, e.latlng.lng);
    });

    document.getElementById("btnFindOnMap")?.addEventListener("click", async () => {
      const q = venueInput.value.trim();
      if (!q) return;
      const res = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(q)}&format=json&limit=1`);
      const data = await res.json();
      if (data && data[0]) {
        const lat = parseFloat(data[0].lat), lon = parseFloat(data[0].lon);
        setPoint(lat, lon);
        leafletMap.setView([lat, lon], 16);
      }
    });

    async function reverseGeocode(lat, lon) {
      try {
        const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}&zoom=18&addressdetails=1`;
        const res = await fetch(url, { headers: { "Accept": "application/json" } });
        if (!res.ok) return null;
        const data = await res.json();
        return data.display_name || null;
      } catch { return null; }
    }

    async function setPoint(lat, lon) {
      if (leafletMarker) leafletMap.removeLayer(leafletMarker);
      leafletMarker = L.marker([lat, lon]).addTo(leafletMap);
      latInput.value = (+lat).toFixed(6);
      lonInput.value = (+lon).toFixed(6);
      fidInput.value = ""; fnameInput.value = ""; layerInput.value = "";

      if (!venueInput.value) {
        const addr = await reverseGeocode(lat, lon);
        if (addr) venueInput.value = addr;
      }
      checkConflict();
    }
  }
}

function invalidateMapSize() {
  if (window.google && document.getElementById("map")) {
    // Google adjusts on its own when container changes; nothing required.
    return;
  }
  if (leafletMap) leafletMap.invalidateSize();
}
