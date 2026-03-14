"""
fix_extract.py  –  Extract the already-downloaded kagglehub archive
to a short path (C:\\ds\\) to avoid Windows 260-char path limit errors.

Run ONCE:
    python fix_extract.py
"""

import zipfile, os, sys, shutil, pathlib, re

# ── Where kagglehub stored the archive ───────────────────────────────────────
ARCHIVE = pathlib.Path(
    r"C:\Users\Hp\.cache\kagglehub\datasets\vipoooool\new-plant-diseases-dataset\2.archive"
)

# ── Short output directory (avoids Windows MAX_PATH issues) ──────────────────
OUT_DIR = pathlib.Path(r"C:\ds")

if not ARCHIVE.exists():
    print(f"❌  Archive not found: {ARCHIVE}")
    print("    Run 'python train_model.py --epochs 1' once to download it first.")
    sys.exit(1)

OUT_DIR.mkdir(parents=True, exist_ok=True)
print(f"📦  Extracting {ARCHIVE.name}  →  {OUT_DIR}")
print("    (This may take 2-5 minutes for 87,000+ images…)\n")

with zipfile.ZipFile(ARCHIVE, "r") as zf:
    members = zf.infolist()
    total = len(members)
    for i, member in enumerate(members):
        # Sanitise the filename: strip the long nested prefix
        # e.g. "New Plant Diseases Dataset(Augmented)/New Plant .../train/Apple___scab/x.jpg"
        # → sanitised to strip the top folders, keeping split/class/image
        name = member.filename
        # Replace degree symbol and other problematic chars
        safe_name = re.sub(r'[^\w/\-_.]', '_', name)
        target = OUT_DIR / safe_name
        if member.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                with zf.open(member) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
            except Exception as e:
                print(f"  ⚠️  Skip: {name[:80]}  –  {e}")

        if i % 2000 == 0:
            print(f"  Progress: {i}/{total} files ({i*100//total}%)")

print(f"\n✅  Done! Dataset extracted to: {OUT_DIR}")

# ── Find the split root (folder with train/ and valid/) ──────────────────────
for root, dirs, _ in os.walk(OUT_DIR):
    if "train" in dirs and "valid" in dirs:
        print(f"📂  Split root found: {root}")
        print(f"\n▶  Now run training with:")
        print(f"   python train_model.py --data_dir \"{root}\" --epochs 20")
        break
else:
    print("⚠️  Could not auto-detect split root. Browse C:\\ds\\ manually.")
