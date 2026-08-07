#!/usr/bin/env python3

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from html import escape


ROOT = Path(__file__).resolve().parents[1]

AUTHORITY_FILE = (
    ROOT
    / "data"
    / "authority"
    / "earths-pharmacy-claims-v1-REVISION-2I-DRAFT-PENDING-VALIDATION-201.jsonl"
)

OUTPUT_DIR = (
    ROOT
    / "content"
    / "internal"
    / "monographs"
)

REPORT_DIR = (
    ROOT
    / "data"
    / "library"
)

REPORT_FILE = (
    REPORT_DIR
    / "full-ingest-report.json"
)

EXPECTED_SHA256 = (
    "e692b022f99895db7acfa6c5b9d7427103a929ce042be1bb0d769c0be7a2087d"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def slugify(value: str) -> str:
    value = str(value or "").strip().lower()

    value = (
        value
        .replace("&", " and ")
        .replace("’", "")
        .replace("'", "")
    )

    value = re.sub(
        r"[^a-z0-9]+",
        "-",
        value
    )

    value = value.strip("-")

    return value or "record"


def first_present(record, keys, default=""):
    for key in keys:
        value = record.get(key)

        if value not in (
            None,
            "",
            [],
            {}
        ):
            return value

    return default


def normalize_parent_id(record):
    value = first_present(
        record,
        [
            "parent_record_id",
            "parent_id",
            "record_id",
            "monograph_id",
            "botanical_id",
            "entry_id"
        ]
    )

    if value:
        return str(value).strip()

    claim_id = str(
        record.get("claim_id", "")
    ).strip()

    if "-" in claim_id:
        return claim_id.split("-", 1)[0]

    return claim_id or "UNKNOWN"


def normalize_common_name(record):
    return str(
        first_present(
            record,
            [
                "common_name",
                "plant_name",
                "botanical_name",
                "record_name",
                "title",
                "parent_name"
            ],
            "Unnamed Record"
        )
    ).strip()


def normalize_scientific_name(record):
    return str(
        first_present(
            record,
            [
                "scientific_name",
                "latin_name",
                "botanical_scientific_name"
            ],
            ""
        )
    ).strip()


def normalize_record_type(record):
    common_name = normalize_common_name(
        record
    ).lower()

    parent_id = normalize_parent_id(
        record
    ).upper()

    if parent_id == "34B":
        return "Animal-Derived Natural Product"

    if "honey" == common_name:
        return "Animal-Derived Natural Product"

    if any(
        term in common_name
        for term in [
            "sea moss",
            "bladderwrack",
            "kelp",
            "algae",
            "seaweed"
        ]
    ):
        return "Seaweed / Algae"

    return "Botanical"


def extract_claim_text(record):
    return str(
        first_present(
            record,
            [
                "claim_text",
                "claim",
                "therapeutic_claim",
                "claim_statement",
                "statement"
            ],
            ""
        )
    ).strip()


def extract_tier(record):
    return str(
        first_present(
            record,
            [
                "evidence_tier",
                "tier",
                "evidence_level"
            ],
            "Unclassified"
        )
    ).strip()


def extract_safety(record):
    return str(
        first_present(
            record,
            [
                "safety",
                "safety_flag",
                "cautions",
                "safety_notes",
                "warning"
            ],
            ""
        )
    ).strip()


def extract_citation(record):
    value = first_present(
        record,
        [
            "citation",
            "citation_text",
            "reference",
            "source"
        ],
        ""
    )

    if isinstance(value, list):
        return "; ".join(
            str(item)
            for item in value
        )

    return str(value).strip()


def unique_slug(
    base_slug,
    parent_id,
    used_slugs
):
    slug = base_slug

    if slug not in used_slugs:
        used_slugs.add(slug)
        return slug

    slug = f"{base_slug}-{slugify(parent_id)}"

    counter = 2

    while slug in used_slugs:
        slug = (
            f"{base_slug}-"
            f"{slugify(parent_id)}-"
            f"{counter}"
        )
        counter += 1

    used_slugs.add(slug)

    return slug


def render_claim_rows(records):
    rows = []

    for record in records:
        claim_id = escape(
            str(
                record.get(
                    "claim_id",
                    ""
                )
            )
        )

        claim_text = escape(
            extract_claim_text(record)
        )

        tier = escape(
            extract_tier(record)
        )

        citation = escape(
            extract_citation(record)
        )

        if not citation:
            citation = (
                "Citation mapping pending "
                "internal review"
            )

        rows.append(
            f"""
            <tr>
              <td>{claim_id}</td>
              <td>{claim_text}</td>
              <td>{tier}</td>
              <td>{citation}</td>
            </tr>
            """
        )

    return "\n".join(rows)


def render_safety(records):
    notes = []

    for record in records:
        value = extract_safety(record)

        if value and value not in notes:
            notes.append(value)

    if not notes:
        return (
            "Safety review pending. "
            "This internal DRAFT must not "
            "be publicly released."
        )

    return " ".join(
        escape(item)
        for item in notes
    )


def render_identity(
    record_type,
    common_name,
    scientific_name
):
    if (
        record_type
        == "Animal-Derived Natural Product"
    ):
        return """
        <p>
          <strong>Record Type:</strong>
          Animal-Derived Natural Product
        </p>
        <p>
          <strong>Botanical Scientific Name:</strong>
          Not applicable
        </p>
        """

    if record_type == "Seaweed / Algae":
        return f"""
        <p>
          <strong>Record Type:</strong>
          Seaweed / Algae
        </p>
        <p>
          <strong>Scientific Identity:</strong>
          <em>{escape(scientific_name or "Pending verification")}</em>
        </p>
        """

    return f"""
    <p>
      <strong>Record Type:</strong>
      Botanical
    </p>
    <p>
      <strong>Scientific Name:</strong>
      <em>{escape(scientific_name or "Pending verification")}</em>
    </p>
    """


def render_monograph(
    parent_id,
    common_name,
    scientific_name,
    record_type,
    records
):
    identity = render_identity(
        record_type,
        common_name,
        scientific_name
    )

    claim_rows = render_claim_rows(
        records
    )

    safety = render_safety(
        records
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta
    name="viewport"
    content="width=device-width,initial-scale=1"
  />

  <meta
    name="robots"
    content="noindex,nofollow,noarchive"
  />

  <title>
    {escape(common_name)} —
    Internal DRAFT —
    The Earth’s Pharmacy
  </title>

  <style>
    body {{
      max-width: 960px;
      margin: 40px auto;
      padding: 0 20px 60px;
      font-family:
        Georgia,
        "Times New Roman",
        serif;
      line-height: 1.6;
      background: #07130f;
      color: #f3efe3;
    }}

    h1,
    h2 {{
      color: #d4a84f;
    }}

    .draft-banner {{
      padding: 16px;
      margin-bottom: 24px;
      border: 2px solid #b84040;
      background:
        rgba(184, 64, 64, 0.12);
      font-weight: bold;
    }}

    .identity,
    .safety {{
      padding: 18px;
      margin: 20px 0;
      border:
        1px solid
        rgba(212, 168, 79, 0.25);
      border-radius: 6px;
    }}

    .safety {{
      border-color:
        rgba(255, 100, 100, 0.3);
      background:
        rgba(255, 80, 80, 0.05);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 18px;
    }}

    th,
    td {{
      border:
        1px solid
        rgba(212, 168, 79, 0.18);
      padding: 10px;
      vertical-align: top;
      text-align: left;
    }}

    th {{
      color: #d4a84f;
    }}

    footer {{
      margin-top: 36px;
      font-size: 13px;
      opacity: 0.75;
    }}
  </style>
</head>

<body>

  <div class="draft-banner">
    INTERNAL DRAFT — NOT APPROVED FOR PUBLICATION —
    NOT PART OF THE PUBLIC DEPLOYMENT
  </div>

  <h1>{escape(common_name)}</h1>

  <div class="identity">

    <p>
      <strong>Parent Record:</strong>
      {escape(str(parent_id))}
    </p>

    {identity}

    <p>
      <strong>Lifecycle Status:</strong>
      DRAFT
    </p>

  </div>

  <section>

    <h2>Claim-Level Evidence</h2>

    <table>

      <thead>
        <tr>
          <th>Claim ID</th>
          <th>Claim</th>
          <th>Evidence Tier</th>
          <th>Citation / Mapping Status</th>
        </tr>
      </thead>

      <tbody>
        {claim_rows}
      </tbody>

    </table>

  </section>

  <section class="safety">

    <h2>Safety Review</h2>

    <p>
      {safety}
    </p>

  </section>

  <footer>
    Generated from the immutable Revision 2I
    authority dataset for internal production use.
    Generation does not constitute Founder approval,
    Founder Frozen status, publication, release,
    medical endorsement, or public activation.
  </footer>

</body>
</html>
"""


def main():
    if not AUTHORITY_FILE.exists():
        raise SystemExit(
            "ERROR: Authority dataset not found: "
            + str(AUTHORITY_FILE)
        )

    actual_hash = sha256_file(
        AUTHORITY_FILE
    )

    if actual_hash != EXPECTED_SHA256:
        raise SystemExit(
            "ERROR: Authority SHA-256 mismatch.\n"
            f"Expected: {EXPECTED_SHA256}\n"
            f"Actual:   {actual_hash}"
        )

    grouped = defaultdict(list)

    row_count = 0

    with AUTHORITY_FILE.open(
        "r",
        encoding="utf-8"
    ) as handle:

        for line_number, line in enumerate(
            handle,
            start=1
        ):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(
                    "ERROR: Invalid JSONL on "
                    f"line {line_number}: {exc}"
                )

            row_count += 1

            parent_id = normalize_parent_id(
                record
            )

            grouped[parent_id].append(
                record
            )

    if row_count != 1273:
        raise SystemExit(
            "ERROR: Authority row count mismatch. "
            f"Expected 1273, found {row_count}."
        )

    if len(grouped) != 201:
        raise SystemExit(
            "ERROR: Parent-record count mismatch. "
            f"Expected 201, found {len(grouped)}."
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    used_slugs = set()

    generated = []

    for parent_id in sorted(
        grouped.keys(),
        key=str
    ):
        records = grouped[parent_id]

        first = records[0]

        common_name = normalize_common_name(
            first
        )

        scientific_name = (
            normalize_scientific_name(
                first
            )
        )

        record_type = normalize_record_type(
            first
        )

        slug = unique_slug(
            slugify(common_name),
            parent_id,
            used_slugs
        )

        filename = (
            f"{slug}.html"
        )

        path = OUTPUT_DIR / filename

        html = render_monograph(
            parent_id=parent_id,
            common_name=common_name,
            scientific_name=scientific_name,
            record_type=record_type,
            records=records
        )

        path.write_text(
            html,
            encoding="utf-8"
        )

        generated.append(
            {
                "parent_record_id":
                    parent_id,
                "common_name":
                    common_name,
                "scientific_name":
                    scientific_name,
                "record_type":
                    record_type,
                "claim_count":
                    len(records),
                "lifecycle_status":
                    "DRAFT",
                "internal_path":
                    str(
                        path.relative_to(
                            ROOT
                        )
                    ),
                "slug":
                    slug
            }
        )

    report = {
        "status":
            "INTERNAL_DRAFT_GENERATION_COMPLETE",
        "authority_file":
            AUTHORITY_FILE.name,
        "authority_sha256":
            actual_hash,
        "authority_rows":
            row_count,
        "parent_records":
            len(grouped),
        "generated_files":
            len(generated),
        "public_release":
            False,
        "records":
            generated
    }

    REPORT_FILE.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False
        )
        + "\n",
        encoding="utf-8"
    )

    print(
        "PASS: Internal monograph generation complete."
    )

    print(
        f"Authority rows: {row_count}"
    )

    print(
        f"Parent records: {len(grouped)}"
    )

    print(
        f"Generated internal DRAFT files: {len(generated)}"
    )

    print(
        "Public release: NO"
    )

    print(
        f"Report: {REPORT_FILE.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
