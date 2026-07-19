#!/usr/bin/env python3
"""
Copy dummy images into the Django media directory with clean product names.
Run from project root with venv active.
"""
import shutil, os

SRC = "dummy-images"
DST = "media/products/primary"
os.makedirs(DST, exist_ok=True)

copies = [
    # BAGS
    ("WhatsApp Image 2026-07-08 at 12.44.19 PM.jpeg",    "bag-brown-small-purse.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.21 PM.jpeg",    "bag-tan-crossbody.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.23 PM.jpeg",    "bag-beige-large-handbag.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.25 PM.jpeg",    "bag-red-glitter-clutch.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.27 PM.jpeg",    "bag-tan-canvas-tote.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.28 PM.jpeg",    "bag-dark-brown-mini.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.31 PM.jpeg",    "bag-burgundy-coach-tote.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.35 PM.jpeg",    "bag-gold-crystal-clutch.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.39 PM.jpeg",    "bag-maroon-jeweled-clutch.jpg"),
    # MAKEUP / LIP
    ("WhatsApp Image 2026-07-08 at 12.44.11 PM.jpeg",    "makeup-lip-glaze-pink.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.13 PM.jpeg",    "makeup-lip-glaze-shelf.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.13 PM (1).jpeg","makeup-liquid-lipstick.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.16 PM.jpeg",    "makeup-mocha-lip-gloss.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.18 PM.jpeg",    "makeup-coloressence-lipstick.jpg"),
    # SKINCARE
    ("WhatsApp Image 2026-07-08 at 12.44.39 PM (1).jpeg","skincare-vaseline-spf50.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.40 PM.jpeg",    "skincare-vaseline-lotion.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.41 PM.jpeg",    "skincare-dotkey-sunscreen.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.43 PM.jpeg",    "skincare-gaga-sun-cream.jpg"),
    ("WhatsApp Image 2026-07-08 at 12.44.43 PM (1).jpeg","skincare-dotkey-moisturizer.jpg"),
]

for src_name, dst_name in copies:
    src = os.path.join(SRC, src_name)
    dst = os.path.join(DST, dst_name)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"  ✓ {dst_name}")
    else:
        print(f"  ✗ MISSING: {src_name}")

print(f"\nDone. Files in {DST}:")
for f in sorted(os.listdir(DST)):
    print(f"  {f}")
