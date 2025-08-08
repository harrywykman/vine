import os

from PIL import Image


def generate_pwa_icons(source_image_path, output_dir="static/icons"):
    """
    Generate PWA icons from a source image using Pillow

    Args:
        source_image_path (str): Path to your source image (should be high resolution, ideally 1024x1024)
        output_dir (str): Directory to save the generated icons
    """

    # Icon sizes needed for PWA manifest
    icon_sizes = [72, 96, 128, 144, 152, 192, 384, 512]

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Open the source image
        with Image.open(source_image_path) as img:
            # Convert to RGBA if not already (handles transparency)
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            print(f"Source image: {img.size[0]}x{img.size[1]} pixels")

            # Generate each icon size
            for size in icon_sizes:
                # Resize the image using high-quality resampling
                resized_img = img.resize((size, size), Image.Resampling.LANCZOS)

                # Save as PNG
                output_path = os.path.join(output_dir, f"icon-{size}x{size}.png")
                resized_img.save(output_path, "PNG", optimize=True)

                print(f"Generated: {output_path}")

    except FileNotFoundError:
        print(f"Error: Source image '{source_image_path}' not found")
    except Exception as e:
        print(f"Error: {e}")


def generate_screenshot_placeholder(
    output_dir="static/screenshots", width=640, height=1136
):
    """
    Generate a placeholder screenshot for PWA manifest
    You'll want to replace this with actual app screenshots
    """
    os.makedirs(output_dir, exist_ok=True)

    # Create a simple placeholder image
    img = Image.new("RGB", (width, height), color="#f0f0f0")

    # You could add text or other elements here if needed
    # For now, just a solid color placeholder

    output_path = os.path.join(output_dir, "mobile-screenshot.png")
    img.save(output_path, "PNG")
    print(f"Generated placeholder screenshot: {output_path}")


if __name__ == "__main__":
    # Replace 'your_source_icon.png' with the path to your source image
    # Ideally this should be a high-resolution square image (1024x1024 or larger)
    source_image = "static/img/logo.png"  # Change this path

    print("Generating PWA icons...")
    generate_pwa_icons(source_image)

    print("\nGenerating screenshot placeholder...")
    generate_screenshot_placeholder()

    print("\nDone! Don't forget to:")
    print("1. Replace the placeholder screenshot with actual app screenshots")
    print("2. Make sure your manifest.json is linked in your HTML head")
    print("3. Add a service worker for full PWA functionality")
