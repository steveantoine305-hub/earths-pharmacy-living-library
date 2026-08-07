import json
import os
import sys
from pathlib import Path


def _normalize(path):
    normalized = str(path).replace("\\", "/")

    while normalized.startswith("./"):
        normalized = normalized[2:]

    return normalized.lstrip("/")


def _is_allowlisted(rel_path, approved_paths):
    rel_path = _normalize(rel_path).rstrip("/")

    for raw_approved in approved_paths:
        approved = _normalize(raw_approved)
        is_directory = approved.endswith("/")
        approved = approved.rstrip("/")

        if is_directory:
            if (
                rel_path == approved
                or rel_path.startswith(approved + "/")
            ):
                return True
        elif rel_path == approved:
            return True

    return False


def validate(deploy_dir=None):
    repo_root = Path(__file__).resolve().parent.parent
    manifest_path = (
        repo_root / "config" / "public-content-manifest.json"
    )

    if deploy_dir:
        deploy_root = Path(deploy_dir).resolve()
    else:
        deploy_root = repo_root / "deploy_output"

    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    approved_paths = manifest.get(
        "approved_public_paths",
        [],
    )

    excluded_paths = [
        _normalize(path).rstrip("/")
        for path in manifest.get("excluded_paths", [])
    ]

    known_drafts = {
        "ginger.html",
        "bladderwrack.html",
        "honey-the-oldest-medicine.html",
        "soursop-graviola.html",
        "moringa.html",
        "template.html",
    }

    errors = []

    if not deploy_root.exists() or not deploy_root.is_dir():
        errors.append(
            "CRITICAL ERROR: Deployment output not found: "
            f"{deploy_root}"
        )
    else:
        for root, dirs, files in os.walk(deploy_root):
            root_path = Path(root)

            for name in list(dirs) + list(files):
                candidate = root_path / name

                if candidate.is_symlink():
                    rel_path = candidate.relative_to(
                        deploy_root
                    ).as_posix()

                    errors.append(
                        "CRITICAL ERROR: Symlink found in deployment "
                        f"output: {rel_path}"
                    )

            for filename in files:
                full_path = root_path / filename

                rel_path = full_path.relative_to(
                    deploy_root
                ).as_posix()

                normalized = _normalize(rel_path)

                if not _is_allowlisted(
                    normalized,
                    approved_paths,
                ):
                    errors.append(
                        "CRITICAL ERROR: Non-allowlisted file in "
                        f"deployment output: {normalized}"
                    )

                for excluded in excluded_paths:
                    if (
                        normalized == excluded
                        or normalized.startswith(
                            excluded + "/"
                        )
                    ):
                        errors.append(
                            "CRITICAL ERROR: Excluded path leaked "
                            "into deployment output: "
                            f"{normalized}"
                        )
                        break

                if filename in known_drafts:
                    errors.append(
                        "CRITICAL ERROR: DRAFT/internal monograph "
                        "file in deployment output: "
                        f"{normalized}"
                    )

                if full_path.suffix.lower() in {
                    ".html",
                    ".htm",
                }:
                    try:
                        text = full_path.read_text(
                            encoding="utf-8",
                            errors="ignore",
                        ).lower()

                        draft_markers = [
                            '"lifecycle_status": "draft"',
                            '"lifecycle_status":"draft"',
                            "lifecycle_status = draft",
                            "lifecycle_status=draft",
                            'data-lifecycle="draft"',
                            "data-lifecycle='draft'",
                        ]

                        if any(
                            marker in text
                            for marker in draft_markers
                        ):
                            errors.append(
                                "CRITICAL ERROR: DRAFT lifecycle "
                                "marker found in deployed HTML: "
                                f"{normalized}"
                            )

                    except OSError as exc:
                        errors.append(
                            "CRITICAL ERROR: Could not inspect "
                            f"{normalized}: {exc}"
                        )

    if errors:
        print("\n".join(sorted(set(errors))))
        return 1

    print(
        "Deployment validation passed: actual deploy_output "
        "contains only allowlisted public content."
    )

    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    sys.exit(validate(target))
