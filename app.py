#!/usr/bin/env python3
"""
Image Renamer using Claude Vision API
--------------------------------------
Describes images using Claude and renames them based on the description.

Usage:
    # Rename images in a folder:
    python image_renamer.py --folder /path/to/images

    # Rename specific images:
    python image_renamer.py --files photo1.jpg photo2.png

Requirements:
    pip install anthropic
    Set ANTHROPIC_API_KEY environment variable
"""

import os
import re
import sys
import base64
import shutil
import argparse
from pathlib import Path
import ollama

# ── Config ────────────────────────────────────────────────────────────────────
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
MAX_FILENAME_LENGTH  = 60   # characters (excluding extension)
# ──────────────────────────────────────────────────────────────────────────────


def encode_image(image_path: Path) -> tuple[str, str]:
    """Return (base64_data, media_type) for an image file."""
    ext_to_mime = {
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png":  "image/png",
        ".gif":  "image/gif",
        ".webp": "image/webp",
        ".bmp":  "image/bmp",
    }
    media_type = ext_to_mime.get(image_path.suffix.lower(), "image/jpeg")
    with open(image_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, media_type


def describe_image(image_path: Path) -> str:
    """وصف الصورة باستخدام LLaVA عبر Ollama"""
    try:
        # هنا بنبعت مسار الصورة للموديل اللي شغال على جهازك
        response = ollama.generate(
            model='llava',
            prompt=(
                "Describe this image in 3-6 words, suitable for a filename. "
                "Use only lowercase English letters, digits, and hyphens. "
                "No punctuation, no spaces. Reply with ONLY the words."
            ),
            images=[str(image_path)],
            stream=False
        )
        
        raw = response['response'].strip().lower()
        
        # تنظيف النص الناتج من أي حروف غريبة
        clean = re.sub(r"[^a-z0-9\-]", "-", raw)
        clean = re.sub(r"-{2,}", "-", clean).strip("-")
        return clean[:MAX_FILENAME_LENGTH] or "image"
        
    except Exception as exc:
        print(f"      ❌  LLaVA error: {exc}")
        return "error-image"


def unique_path(target: Path) -> Path:
    """If target already exists, append _1, _2, … until free."""
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    counter = 1
    while True:
        candidate = target.with_name(f"{stem}_{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def rename_images(image_paths: list[Path], dry_run: bool = False) -> None:
    """Describe and rename a list of image files."""

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Processing {len(image_paths)} image(s)…\n")

    for img_path in image_paths:
        if not img_path.exists():
            print(f"  ⚠️  Skipping (not found): {img_path}")
            continue
        if img_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            print(f"  ⚠️  Skipping (unsupported format): {img_path.name}")
            continue

        print(f"  🔍  Analysing: {img_path.name}")
        try:
            description = describe_image(img_path)
        except Exception as exc:
            print(f"      ❌  LLaVA error: {exc}")
            continue

        new_name   = description + img_path.suffix.lower()
        new_path   = unique_path(img_path.parent / new_name)

        print(f"      ✅  {img_path.name}  →  {new_path.name}")

        if not dry_run:
            shutil.move(str(img_path), str(new_path))

    print("\nDone!" if not dry_run else "\n[Dry run complete — no files were changed]")


# ── CLI ───────────────────────────────────────────────────────────────────────

def collect_images_from_folder(folder: Path) -> list[Path]:
    return sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def main():
    parser = argparse.ArgumentParser(
        description="Rename images using Claude Vision descriptions."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--folder", "-d",
        type=Path,
        help="Path to a folder — all supported images inside will be renamed.",
    )
    group.add_argument(
        "--files", "-f",
        type=Path,
        nargs="+",
        help="One or more image file paths to rename.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview renames without actually changing any files.",
    )
    args = parser.parse_args()

    if args.folder:
        if not args.folder.is_dir():
            print(f"❌  Not a directory: {args.folder}")
            sys.exit(1)
        images = collect_images_from_folder(args.folder)
        if not images:
            print(f"No supported images found in {args.folder}")
            sys.exit(0)
    else:
        images = args.files

    rename_images(images, dry_run=args.dry_run)


if __name__ == "__main__":
    main()