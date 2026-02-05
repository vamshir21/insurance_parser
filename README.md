# Insurance Document Parser

This project is a small prototype built as part of a technical assignment.
The goal is to parse insurance policy documents (PDF → text) and extract key financial and policy-related fields in a structured JSON format.

The focus is **not on perfect accuracy**, but on building a **robust and explainable parsing pipeline** that works on noisy, real-world insurance documents.

---

## What this project does

The system takes insurance documents converted to `.txt` format and:

1. **Cleans and normalizes the entire document**
   (removes PDF noise, normalizes spacing, currency symbols, etc.)
2. **Parses important fields** like:

   * Insurance type (Motor / Health)
   * Insurer name
   * Insured name
   * Sum insured / IDV
   * Premium details (base premium, tax, total premium)
   * Deductibles (for motor policies)
3. Outputs a **structured JSON** that can be consumed by downstream systems.

---

## Why this approach

Insurance PDFs are messy:

* Tables break across lines
* Labels and values are inconsistent
* Numbers appear everywhere (policy numbers, dates, IDs)

Instead of directly parsing raw text, the pipeline is split into **two clear stages**.

### 1. Preprocessing (`preprocess.py`)

* Operates on the **entire document**
* Does **not extract fields**
* Only normalizes text:

  * Uppercases content
  * Normalizes currency (`Rs.`, `₹`)
  * Removes decorative junk
  * Keeps all content intact

This makes the parsing stage simpler and more reliable.

### 2. Parsing (`parser.py`)

* Applies **domain-specific rules**
* Separate logic for:

  * Motor insurance
  * Health insurance
* Handles:

  * Labels appearing anywhere in a line
  * Values appearing on the next line
  * GST split into CGST / SGST
  * Multiple “Sum Insured” values in health policies (selects the maximum)

This separation makes the logic easier to understand, explain, and maintain.

---

## Project structure

```
insurance_parser/
│
├── preprocess.py        # Cleans full document text
├── parser.py            # Extracts structured fields
│
├── samples/
│   ├── motor_raw.txt    # Raw motor policy text (PDF dump)
│   ├── motor_clean.txt  # Cleaned motor text
│   ├── health_raw.txt   # Raw health policy text
│   └── health_clean.txt # Cleaned health text
│
└── README.md
```

---

## How to run

### Step 1: Preprocess documents

This cleans the raw text files.

```
python preprocess.py
```

This generates:

* `motor_clean.txt`
* `health_clean.txt`

---

### Step 2: Parse documents

This extracts structured data into JSON.

```
python parser.py
```

The parsed JSON output for both motor and health policies is printed to the console.

---

## Example output (simplified)

### Motor policy

```json
{
  "metadata": {
    "insurance_type": "MOTOR",
    "insurer_name": "GO DIGIT GENERAL INSURANCE LTD",
    "insured_name": "VANESHWARI L"
  },
  "financials": {
    "vehicle_idv": 31707,
    "base_premium": 3273,
    "tax": 589,
    "total_premium": 3862,
    "deductible": 100
  },
  "policy": {
    "policy_term": "1 year"
  }
}
```

### Health policy

```json
{
  "metadata": {
    "insurance_type": "HEALTH",
    "insurer_name": "HDFC ERGO GENERAL INSURANCE COMPANY LIMITED"
  },
  "financials": {
    "sum_insured": 300000,
    "base_premium": 44304,
    "tax": 7819,
    "total_premium": 51123
  },
  "policy": {
    "policy_term": "1 year"
  }
}
```

---

## Limitations

* This is a **rule-based** parser, not ML-based
* It is tuned for common Indian motor and health insurance formats
* Some edge cases may still exist due to document variability

These trade-offs were intentional to keep the solution **simple, transparent, and explainable**.

---

## Final note

This project demonstrates:

* Handling of noisy real-world data
* Clean separation between preprocessing and parsing
* Practical, domain-aware engineering decisions

It is designed as a **foundation** that can be extended further if needed.
