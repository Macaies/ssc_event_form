document.addEventListener("DOMContentLoaded", () => {
  const locationInput = document.getElementById("eventLocation");
  const statusMsg = document.getElementById("locationStatus");
  if (!locationInput || !statusMsg) return;

  const civicKeywords = [
    "park","reserve","hall","community centre","foreshore",
    "beach","oval","plaza","square","green","public","garden"
  ];

  locationInput.addEventListener("input", () => {
    const v = locationInput.value.toLowerCase();
    const matched = civicKeywords.some(k => v.includes(k));
    statusMsg.textContent = !v
      ? ""
      : matched ? "Looks like a civic/public place ✅" : "May not be a civic place ⚠️";
    statusMsg.className = "status-msg " + (matched ? "success" : "warning");
  });
});
