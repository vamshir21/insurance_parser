import re
import json
from pathlib import Path

# -------------------------
# Regex for money values
# -------------------------
MONEY_RE = re.compile(r"\b(\d{3,}(?:,\d{3})*(?:\.\d+)?)\b")


def extract_money(text: str):
    """
    Extracts the first reasonable money value from text.
    """
    m = MONEY_RE.search(text)
    if not m:
        return None
    return int(float(m.group(1).replace(",", "")))


# -------------------------
# Main parser
# -------------------------
def parse(clean_path: str):
    text = Path(clean_path).read_text(encoding="utf-8", errors="ignore")
    lines = [l.strip().upper() for l in text.splitlines() if l.strip()]

    result = {
        "metadata": {},
        "financials": {},
        "policy": {
            "policy_term": "1 year"
        }
    }

    insurance_type = None

    # ==================================================
    # PASS 1: Detect insurance type + metadata
    # ==================================================
    for i, line in enumerate(lines):

        # Insurance type
        if "HEALTH" in line:
            insurance_type = "HEALTH"
            result["metadata"]["insurance_type"] = "HEALTH"

        if "TWO WHEELER" in line or "TWO-WHEELER" in line or "MOTOR" in line:
            insurance_type = "MOTOR"
            result["metadata"]["insurance_type"] = "MOTOR"

        # Insurer name
        if "INSURANCE COMPANY LIMITED" in line and "insurer_name" not in result["metadata"]:
            result["metadata"]["insurer_name"] = line.title()

        # Insured name (two common patterns)
        if line == "NAME" and i + 1 < len(lines):
            result["metadata"]["insured_name"] = lines[i + 1].title()

        if line.startswith("NAME :"):
            result["metadata"]["insured_name"] = line.replace("NAME :", "").strip().title()

    # ==================================================
    # PASS 2: Financial extraction
    # ==================================================
    gst_total = 0
    health_sum_insured_candidates = []

    for i, line in enumerate(lines):

        next_line = lines[i + 1] if i + 1 < len(lines) else ""

        # ----------------------
        # MOTOR RULES
        # ----------------------
        if insurance_type == "MOTOR":

            if "VEHICLE IDV" in line:
                val = extract_money(line) or extract_money(next_line)
                if val:
                    result["financials"]["vehicle_idv"] = val

            if "BASIC" in line and "PREMIUM" in line:
                val = extract_money(line) or extract_money(next_line)
                if val:
                    result["financials"]["base_premium"] = val

            if "CGST" in line or "SGST" in line or line.startswith("GST"):
                val = extract_money(line)
                if val:
                    gst_total += val

            if "FINAL PREMIUM" in line or "NET PAYABLE" in line or "TOTAL PREMIUM" in line:
                val = extract_money(line) or extract_money(next_line)
                if val:
                    result["financials"]["total_premium"] = val

            if "COMPULSORY EXCESS" in line or "DEDUCTIBLE" in line:
                val = extract_money(line) or extract_money(next_line)
                if val:
                    result["financials"]["deductible"] = val

        # ----------------------
        # HEALTH RULES
        # ----------------------
        if insurance_type == "HEALTH":

            if "SUM INSURED" in line:
                val = extract_money(line) or extract_money(next_line)
                if val:
                    health_sum_insured_candidates.append(val)

            if "BASIC PREMIUM" in line:
                val = extract_money(line)
                if val:
                    result["financials"]["base_premium"] = val

            if "GST" in line or "SERVICE TAX" in line:
                val = extract_money(line)
                if val:
                    gst_total += val

            if "TOTAL PREMIUM" in line or "NET PAYABLE" in line:
                val = extract_money(line)
                if val:
                    result["financials"]["total_premium"] = val

    # ==================================================
    # Post-processing
    # ==================================================

    # Tax aggregation (CGST + SGST)
    if gst_total > 0:
        result["financials"]["tax"] = gst_total

    # Health sum insured = maximum candidate
    if insurance_type == "HEALTH" and health_sum_insured_candidates:
        result["financials"]["sum_insured"] = max(health_sum_insured_candidates)

    return result


# -------------------------
# Runner
# -------------------------
if __name__ == "__main__":
    print("MOTOR JSON")
    motor_result = print(json.dumps(parse("samples/motor_clean.txt"), indent=2))

    print("\nHEALTH JSON")
    health_result=print(json.dumps(parse("samples/health_clean.txt"), indent=2))
    
    with open("samples/motor_output.json", "w", encoding="utf-8") as f:
        json.dump(motor_result, f, indent=2)

    with open("samples/health_output.json", "w", encoding="utf-8") as f:
        json.dump(health_result, f, indent=2)