import re
from pathlib import Path


def clean_line(line: str) -> str:
    line = line.upper()

    # Normalize currency
    line = line.replace("₹", "")
    line = line.replace("RS.", "")
    line = line.replace("RS", "")

    # Remove decorative junk
    line = re.sub(r"[|=_]{2,}", " ", line)

    # Normalize spacing
    line = re.sub(r"\s+", " ", line)

    # Normalize GST variants
    line = re.sub(r"GST\s*@\s*\d+%", "GST", line)

    return line.strip()


def normalize_motor_line(line: str) -> str:
    """
    Motor policies often have financial labels mid-line.
    This function rewrites them into canonical 'LABEL VALUE' form.
    """
    patterns = {
        "VEHICLE IDV": r"(VEHICLE\s+IDV).*?(\d{3,}(?:,\d{3})*(?:\.\d+)?)",
        "BASIC PREMIUM": r"(BASIC\s+PREMIUM).*?(\d{3,}(?:,\d{3})*(?:\.\d+)?)",
        "GST": r"\b(GST)\b.*?(\d{3,}(?:,\d{3})*(?:\.\d+)?)",
        "TOTAL PREMIUM": r"(NET\s+PAYABLE|TOTAL\s+PREMIUM).*?(\d{3,}(?:,\d{3})*(?:\.\d+)?)",
        "COMPULSORY EXCESS": r"(COMPULSORY\s+EXCESS).*?(\d{2,})"
    }

    for label, pattern in patterns.items():
        m = re.search(pattern, line)
        if m:
            return f"{label} {m.group(2)}"

    return line


def preprocess(raw_path: str, clean_path: str):
    raw_text = Path(raw_path).read_text(encoding="utf-8", errors="ignore")
    raw_lines = raw_text.splitlines()

    cleaned_lines = []
    insurance_type = None

    # Detect insurance type once
    for line in raw_lines:
        u = line.upper()
        if "HEALTH" in u:
            insurance_type = "HEALTH"
            break
        if "MOTOR" in u or "TWO WHEELER" in u:
            insurance_type = "MOTOR"
            break

    for line in raw_lines:
        if not line.strip():
            cleaned_lines.append("")
            continue

        line = clean_line(line)

        # Motor-specific normalization ONLY here
        if insurance_type == "MOTOR":
            line = normalize_motor_line(line)

        cleaned_lines.append(line)

    Path(clean_path).write_text("\n".join(cleaned_lines), encoding="utf-8")


if __name__ == "__main__":
    preprocess("samples/motor_raw.txt", "samples/motor_clean.txt")
    preprocess("samples/health_raw.txt", "samples/health_clean.txt")
    print("Full-document preprocessing complete.")
