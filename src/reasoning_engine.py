def detect_patterns(data):
    patterns = {
        "dampness": 0,
        "leakage": 0,
        "cracks": 0,
        "plumbing": 0
    }

    for area in data.get("areas", []):
        for obs in area.get("inspection_findings", []):
            text = obs.lower()

            if "damp" in text:
                patterns["dampness"] += 1
            if "leak" in text:
                patterns["leakage"] += 1
            if "crack" in text:
                patterns["cracks"] += 1
            if "plumbing" in text or "wc" in text:
                patterns["plumbing"] += 1
                
        for obs in area.get("thermal_findings", []):
            text = obs.lower()
            if "damp" in text:
                patterns["dampness"] += 1
            if "leak" in text:
                patterns["leakage"] += 1
            if "crack" in text:
                patterns["cracks"] += 1
            if "plumbing" in text or "wc" in text:
                patterns["plumbing"] += 1

    return patterns

def generate_summary(patterns):
    issues = []

    if patterns["dampness"] > 0:
        issues.append("dampness")
    if patterns["leakage"] > 0:
        issues.append("leakage")
    if patterns["cracks"] > 0:
        issues.append("structural cracks")

    if issues:
        return f"The property shows multiple issues including {', '.join(issues)}, observed across different areas, indicating ongoing moisture and structural concerns."
    else:
        return "The property does not show major signs of active dampness, leakage, or significant structural cracks based on the current findings."

def infer_root_cause(patterns):
    causes = []

    if patterns["leakage"] > 0:
        causes.append("concealed plumbing leakage")

    if patterns["dampness"] > 0:
        causes.append("waterproofing failure")

    if patterns["cracks"] > 0:
        causes.append("external wall damage allowing water ingress")

    if causes:
        return "The issues are likely caused by " + ", ".join(causes) + "."
    else:
        return "No major root causes identified from the available patterns."

def infer_severity(patterns):
    total = sum(patterns.values())

    if total > 5:
        return "High", "Multiple areas are affected, indicating significant structural concern."
    elif total > 2:
        return "Medium", "Moderate issues observed across areas."
    else:
        return "Low", "Limited issues detected."

def generate_recommendations(patterns):
    recs = []
    if patterns["plumbing"] > 0 or patterns["leakage"] > 0:
        recs.append("Inspect and repair plumbing systems")
    if patterns["dampness"] > 0 or patterns["leakage"] > 0:
        recs.append("Apply waterproofing treatment in affected areas")
        recs.append("Seal tile joints and drainage points")
    if patterns["cracks"] > 0:
        recs.append("Repair cracks and repaint with waterproof coating")
        
    if not recs:
        recs.append("Monitor areas for any future signs of damage")
        
    return recs

def build_deterministic_report(data):
    patterns = detect_patterns(data)
    
    summary = generate_summary(patterns)
    root = infer_root_cause(patterns)
    severity_level, severity_reason = infer_severity(patterns)
    recommendations = generate_recommendations(patterns)
    
    lines = ["# Detailed Diagnostic Report\n"]
    
    lines.append("### 1. Property Issue Summary")
    lines.append(summary + "\n")
    
    lines.append("### 2. Area-wise Observations")
    for area in data.get("areas", []):
        area_name = area.get("name", "General")
        lines.append(f"**Area: {area_name}**")
        
        insp = area.get("inspection_findings", [])
        for f in insp:
            if f.strip():
                lines.append(f"* {f.strip()}")
        if not insp:
            lines.append("* No significant visible findings reported.")
            
        lines.append("\n**Thermal Insights:**")
        therm = area.get("thermal_findings", [])
        for f in therm:
            if f.strip():
                lines.append(f"* {f.strip()}")
        if not therm:
            lines.append("* Thermal data not available for this area.")
            
        lines.append("\n**Images:**")
        imgs = area.get("images", [])
        if not imgs or all(img == "Image Not Available" for img in imgs):
            lines.append('"Image Not Available"')
        else:
            for img in imgs:
                if img and img != "Image Not Available":
                    lines.append(f"![{area_name}]({img})")
        lines.append("")
        
    lines.append("### 3. Probable Root Cause")
    lines.append(root + "\n")
    
    lines.append("### 4. Severity Assessment")
    lines.append(f"* Severity Level: {severity_level}")
    lines.append(f"* Reason: {severity_reason}\n")
    
    lines.append("### 5. Recommended Actions")
    for r in recommendations:
        lines.append(f"* {r}")
    lines.append("")
    
    lines.append("### 6. Additional Notes")
    lines.append("Generated via deterministic rule-engine correlation.\n")
    
    lines.append("### 7. Missing or Unclear Information")
    missing_info = data.get("missing_info", [])
    if missing_info:
        for m in missing_info:
            lines.append(f"* {m}")
    else:
        lines.append("* None reported.")
        
    return "\n".join(lines)
