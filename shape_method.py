import matplotlib.image as mpimg

# Load the image
img = mpimg.imread('Cracker.png')  # Replace with your image path

# Get the shape of the image
height, width, channels = img.shape

# Print number of rows (height) and columns (width)
print(f"Rows (Height): {height}")
print(f"Columns (Width): {width}")
