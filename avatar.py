"""python avatar.py "TECH IN" "25" out/avatar.png   (square profile picture, safe inside Instagram's circle crop)"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + os.sep
top, big, out = sys.argv[1], sys.argv[2], sys.argv[3]
bottom = sys.argv[4] if len(sys.argv) > 4 else "SECONDS"
S = 1080
img = Image.new("RGB", (S, S), (13, 16, 28)); d = ImageDraw.Draw(img)
d.ellipse([60, 60, S - 60, S - 60], outline=(95, 220, 190), width=14)          # mint ring
f1 = ImageFont.truetype(F + "InterDisplay-Bold.otf", 120)
tw = d.textlength(top, font=f1)
x = S / 2 - (tw + 14 * (len(top) - 1)) / 2
for c in top:                                                                   # tracked small caps line
    d.text((x, 330), c, font=f1, fill=(240, 243, 248), anchor="lm"); x += d.textlength(c, font=f1) + 14
size = 520
f2 = ImageFont.truetype(F + "InterDisplay-Bold.otf", size)
while d.textlength(big, font=f2) > 640: size -= 20; f2 = ImageFont.truetype(F + "InterDisplay-Bold.otf", size)
d.text((S / 2, 610), big, font=f2, fill=(255, 190, 60), anchor="mm")
f3 = ImageFont.truetype(F + "Inter-Medium.otf", 78)
d.text((S / 2, 880), bottom, font=f3, fill=(146, 156, 178), anchor="mm")
img.save(out)
