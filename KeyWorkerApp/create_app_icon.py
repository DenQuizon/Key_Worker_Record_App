from PIL import Image, ImageDraw, ImageFont

# Create a simple 256x256 icon with initials "AH"
size = (256, 256)
img = Image.new('RGBA', size, (22, 115, 177, 255))  # blue background

draw = ImageDraw.Draw(img)
text = "AH"
# Try to load a truetype font; fallback to default if not available
try:
    font = ImageFont.truetype("arial.ttf", 140)
except Exception:
    font = ImageFont.load_default()

# Center the text
bbox = draw.textbbox((0, 0), text, font=font)
text_w = bbox[2] - bbox[0]
text_h = bbox[3] - bbox[1]
position = ((size[0] - text_w) // 2, (size[1] - text_h) // 2)

# Draw white text
draw.text(position, text, fill=(255, 255, 255, 255), font=font)

# Save as .ico with multiple sizes
img.save("app_icon.ico", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
print("Icon generated: app_icon.ico")
