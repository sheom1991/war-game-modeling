from PIL import Image

# Load the original background image
bg_img = Image.open("results/background.png")

# Resize to match DEM data dimensions (750x450)
resized_img = bg_img.resize((750, 450), Image.Resampling.LANCZOS)

# Save the resized image
resized_img.save("results/background_resized.png") 