#!/usr/bin/env python3
"""
Generate application icon for FRESCO Studio
Creates a PNG icon from the animated logo design
"""

import math
from PIL import Image, ImageDraw, ImageFont

def generate_icon(size=512):
    """Generate the FRESCO Studio icon"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = size // 2

    # Scale factor
    scale = size / 256

    # Draw background circle (optional - for better visibility in dock)
    bg_radius = int(120 * scale)
    draw.ellipse(
        [center - bg_radius, center - bg_radius,
         center + bg_radius, center + bg_radius],
        fill=(255, 255, 255, 240)
    )

    # Orbit parameters
    orbit_rx = int(90 * scale)
    orbit_ry = int(36 * scale)
    orbit_colors = [
        (59, 130, 246, 255),   # Blue
        (16, 185, 129, 255),   # Green
        (236, 72, 153, 255),   # Pink
    ]
    orbit_rotations = [-30, 30, 90]

    # Draw orbits
    for color, rotation in zip(orbit_colors, orbit_rotations):
        # Create a temporary image for the rotated ellipse
        temp_size = size * 2
        temp = Image.new('RGBA', (temp_size, temp_size), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        temp_center = temp_size // 2

        # Draw ellipse
        line_width = int(4 * scale)
        for i in range(360):
            angle1 = math.radians(i)
            angle2 = math.radians(i + 2)
            x1 = temp_center + orbit_rx * math.cos(angle1)
            y1 = temp_center + orbit_ry * math.sin(angle1)
            x2 = temp_center + orbit_rx * math.cos(angle2)
            y2 = temp_center + orbit_ry * math.sin(angle2)
            temp_draw.line([(x1, y1), (x2, y2)], fill=color, width=line_width)

        # Rotate
        temp = temp.rotate(-rotation, center=(temp_center, temp_center), expand=False)

        # Paste onto main image
        img.paste(temp, (center - temp_center, center - temp_center), temp)

    # Draw nucleus
    nucleus_radius = int(40 * scale)
    # Gradient effect (simplified)
    for r in range(nucleus_radius, 0, -1):
        ratio = r / nucleus_radius
        color = (
            int(37 + (79 - 37) * ratio),  # R
            int(99 + (142 - 99) * ratio),  # G
            int(235 + (247 - 235) * ratio),  # B
            255
        )
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            fill=color
        )

    # Draw "F" letter
    font_size = int(48 * scale)
    font = None
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except:
            continue

    text = "F"
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = center - text_width // 2
        text_y = center - text_height // 2 - int(5 * scale)
        draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
    else:
        # Fallback - draw a simple F shape
        f_width = int(24 * scale)
        f_height = int(32 * scale)
        f_x = center - f_width // 2
        f_y = center - f_height // 2
        stroke = int(6 * scale)
        # Vertical bar
        draw.rectangle([f_x, f_y, f_x + stroke, f_y + f_height], fill=(255, 255, 255, 255))
        # Top horizontal
        draw.rectangle([f_x, f_y, f_x + f_width, f_y + stroke], fill=(255, 255, 255, 255))
        # Middle horizontal
        draw.rectangle([f_x, f_y + f_height//2 - stroke//2, f_x + f_width*3//4, f_y + f_height//2 + stroke//2], fill=(255, 255, 255, 255))

    # Draw electrons
    electron_radius = int(10 * scale)
    electron_angle = 45  # Static position for icon

    for i, (color, rotation) in enumerate(zip(orbit_colors, orbit_rotations)):
        angle_rad = math.radians(electron_angle + i * 120)
        rot_rad = math.radians(rotation)

        # Position on ellipse
        ex = orbit_rx * math.cos(angle_rad)
        ey = orbit_ry * math.sin(angle_rad)

        # Rotate position
        rx = ex * math.cos(rot_rad) - ey * math.sin(rot_rad)
        ry = ex * math.sin(rot_rad) + ey * math.cos(rot_rad)

        # Draw glow
        glow_radius = electron_radius + int(3 * scale)
        glow_color = (*color[:3], 100)
        draw.ellipse(
            [center + rx - glow_radius, center + ry - glow_radius,
             center + rx + glow_radius, center + ry + glow_radius],
            fill=glow_color
        )

        # Draw electron
        draw.ellipse(
            [center + rx - electron_radius, center + ry - electron_radius,
             center + rx + electron_radius, center + ry + electron_radius],
            fill=color
        )

    return img


def main():
    import os

    # Get the resources directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(script_dir, 'resources')

    # Generate icons at different sizes
    sizes = [16, 32, 64, 128, 256, 512, 1024]

    for size in sizes:
        icon = generate_icon(size)
        icon_path = os.path.join(resources_dir, f'icon_{size}.png')
        icon.save(icon_path, 'PNG')
        print(f"Generated: {icon_path}")

    # Also save a standard icon.png at 256px
    icon = generate_icon(256)
    icon_path = os.path.join(resources_dir, 'icon.png')
    icon.save(icon_path, 'PNG')
    print(f"Generated: {icon_path}")

    # Generate icns for macOS (if possible)
    try:
        # Create iconset directory
        iconset_dir = os.path.join(resources_dir, 'icon.iconset')
        os.makedirs(iconset_dir, exist_ok=True)

        # Generate required sizes for iconset
        iconset_sizes = [
            (16, '16x16'),
            (32, '16x16@2x'),
            (32, '32x32'),
            (64, '32x32@2x'),
            (128, '128x128'),
            (256, '128x128@2x'),
            (256, '256x256'),
            (512, '256x256@2x'),
            (512, '512x512'),
            (1024, '512x512@2x'),
        ]

        for size, name in iconset_sizes:
            icon = generate_icon(size)
            icon_path = os.path.join(iconset_dir, f'icon_{name}.png')
            icon.save(icon_path, 'PNG')

        # Convert to icns using iconutil (macOS only)
        icns_path = os.path.join(resources_dir, 'icon.icns')
        os.system(f'iconutil -c icns "{iconset_dir}" -o "{icns_path}"')
        print(f"Generated: {icns_path}")

        # Clean up iconset
        import shutil
        shutil.rmtree(iconset_dir)

    except Exception as e:
        print(f"Could not generate icns: {e}")


if __name__ == '__main__':
    main()
