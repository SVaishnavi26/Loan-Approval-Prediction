"""
Build Script for Loan Approval Prediction System
Packages the application into a dedicated build/ directory and distribution archive.
"""

import os
import shutil
import zipfile
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_NAME = "Loan-Approval-Prediction-v1.0.0"
ZIP_FILE = DIST_DIR / f"{BUILD_NAME}.zip"

# Items to include in the release bundle
INCLUDE_FILES = [
    "app.py",
    "wsgi.py",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    ".dockerignore",
    "run.bat",
    "run.sh",
    "render.yaml",
    "README.md",
    ".gitignore",
]

INCLUDE_DIRS = [
    ("src", ["__init__.py", "predict.py", "data_preprocessing.py"]),
    ("models", ["best_model.joblib", "preprocessor.joblib"]),
    ("templates", ["index.html", "result.html", "about.html"]),
    ("static/css", ["style.css"]),
    ("static/js", ["script.js"]),
    ("data", ["loan_approval_dataset.csv"]),
]


def sha256_file(filepath):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def build():
    print("=" * 65)
    print("BUILDING LOAN APPROVAL PREDICTION SYSTEM")
    print("=" * 65)

    # 1. Prepare build/ directory
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[PREPARE] Initialized build directory: {BUILD_DIR}")

    # 2. Copy root files into build/
    print("\n[COPY] Copying core root files to build/:")
    for fname in INCLUDE_FILES:
        src = PROJECT_ROOT / fname
        if src.exists():
            shutil.copy2(src, BUILD_DIR / fname)
            print(f"  [OK] {fname}")
        else:
            print(f"  [WARN] Optional file missing: {fname}")

    # 3. Copy directories and components into build/
    print("\n[COPY] Copying components and models to build/:")
    for rel_dir, files in INCLUDE_DIRS:
        dest_dir = BUILD_DIR / rel_dir
        dest_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            src_file = PROJECT_ROOT / rel_dir / f
            if src_file.exists():
                shutil.copy2(src_file, dest_dir / f)
                print(f"  [OK] {rel_dir}/{f}")
            else:
                raise FileNotFoundError(f"Required build artifact not found: {src_file}")

    # 4. Create ZIP archive in dist/
    print(f"\n[ARCHIVE] Creating distribution ZIP from build/: {ZIP_FILE.name}")
    with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(BUILD_DIR):
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(BUILD_DIR)
                zipf.write(file_path, arcname=rel_path)

    zip_size_mb = ZIP_FILE.stat().st_size / (1024 * 1024)
    zip_hash = sha256_file(ZIP_FILE)

    print("\n" + "=" * 65)
    print("BUILD COMPLETED SUCCESSFULLY!")
    print(f"Build Folder       : {BUILD_DIR}")
    print(f"Distribution Zip   : {ZIP_FILE}")
    print(f"Package Size       : {zip_size_mb:.2f} MB")
    print(f"SHA-256 Checksum   : {zip_hash}")
    print("=" * 65)
    return BUILD_DIR


if __name__ == "__main__":
    build()
