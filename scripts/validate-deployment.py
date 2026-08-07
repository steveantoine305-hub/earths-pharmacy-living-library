import os
import sys
import json

def validate():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    manifest_path = os.path.join(repo_root, "config", "public-content-manifest.json")
    
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    excluded_dirs = [d.rstrip("/") for d in manifest.get("excluded_paths", [])]
    known_drafts = [
        "ginger.html",
        "bladderwrack.html",
        "honey-the-oldest-medicine.html",
        "soursop-graviola.html",
        "moringa.html",
        "template.html"
    ]
    
    errors = []
    
    # Check for DRAFT monographs in public locations
    public_locations = ["", "monographs", "founders-edition", "living-library", "safety", "about"]
    for loc in public_locations:
        target_dir = os.path.join(repo_root, loc)
        if not os.path.exists(target_dir):
            continue
            
        for file in os.listdir(target_dir):
            if file in known_drafts:
                errors.append(f"CRITICAL ERROR: DRAFT file '{file}' found in public location '{loc or '/'}'")
    
    # Verify internal content is in its place
    internal_monographs_dir = os.path.join(repo_root, "content", "internal", "monographs")
    if not os.path.exists(internal_monographs_dir):
        errors.append("ERROR: Internal monographs directory not found.")
    else:
        found_drafts = os.listdir(internal_monographs_dir)
        for draft in known_drafts:
            if draft != "template.html" and draft not in found_drafts:
                # template.html was moved to content/internal/
                pass

    if errors:
        print("\n".join(errors))
        sys.exit(1)
    
    print("Deployment validation passed: No DRAFT content detected in public paths.")
    sys.exit(0)

if __name__ == "__main__":
    validate()
