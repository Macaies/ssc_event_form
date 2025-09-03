# eligibility.py
def _is_yes(v): return str(v).strip().lower() in ("yes","true","1","y")

def check(form):
    rules = []; add=lambda ok,txt: rules.append({"check":bool(ok),"text":txt})

    attendance   = int(form.get("attendance") or 0)
    alcohol      = form.get("alcohol","No")
    high_risk    = form.get("high_risk","No")
    traffic      = form.get("traffic_mgmt","No")
    vehicle      = form.get("vehicle_access","No")
    amplified    = form.get("amplified_sound","No")
    noise_level  = int(form.get("noise_level") or 0)
    duration_tag = (form.get("duration") or "").strip()  # optional alt to total_days
    total_days   = int(form.get("total_days") or 0)
    start_time   = (form.get("start_time") or "")
    finish_time  = (form.get("end_time") or form.get("finish_time") or "")
    ground_p     = form.get("ground_piercing","No")
    building_appr= form.get("building_approval","No")
    verge_trav   = form.get("verge_traverse","No")

    add(attendance < 200, "Expects <200 attendees at any one time")
    add(building_appr == "No" and ground_p == "No",
        "No infrastructure needing building approval and no ground piercing devices")
    add(traffic == "No", "No traffic management or road/carpark closures")
    add((duration_tag in ("<=2 days","<=12 days")) or (total_days and total_days <= 2),
        "Runs ≤2 consecutive days OR ≤12 non-consecutive days in 12 months")
    add(high_risk == "No", "No firearms, fireworks, or other high-risk activities")
    # time windows (amplified needs ≥07:00)
    add(start_time and (start_time >= ("07:00" if amplified=="Yes" else "05:30")),
        "Does not start before 5:30 am (or 7:00 am if amplified)")
    add(not finish_time or finish_time <= "22:00", "Does not finish after 10:00 pm")
    add(alcohol == "No", "No service or consumption of alcohol")
    add(amplified == "No" or noise_level <= 95, "No amplified noise >95 dBC @ 15 m")
    add(vehicle == "No", "No vehicle/machinery access to public place")
    add(verge_trav == "No", "No traversing over verge/kerb/pathway with vehicles")

    return all(r["check"] for r in rules), rules
