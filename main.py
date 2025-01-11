import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from rasterio.features import rasterize
from rasterio.transform import from_origin
import geodatasets
from scipy.ndimage import zoom

world = gpd.read_file(geodatasets.get_path('geoda nyc'))


def calculate_square_unit():
    # Calculate how many square kilometers are in a square unit
    nyc_area = 778.18  # Square kilometers (source: Wikipedia)
    nyc_area_units = world.area.sum()
    square_unit_conversion = nyc_area / nyc_area_units
    return square_unit_conversion


def get_area_of_interest():
    print(world['name'])

    input_index = int(input("Enter the index of the area of interest: "))
    if input_index < 0 or input_index >= len(world):
        raise IndexError("Index out of range")
    area_of_interest = world.iloc[[input_index]]
    print(f"Selected area of interest: {area_of_interest['name'].values[0]}")
    return area_of_interest



# Define grid resolution
grid_size = 1000  # 1000x1000 Grid

# Select the northernmost, southernmost, easternmost, and westernmost points
minx, miny, maxx, maxy = world.total_bounds


# Define the raster transform
pixel_width = (maxx - minx) / grid_size
pixel_height = (maxy - miny) / grid_size
# This function creates an affine transformation matrix for a raster dataset.
# This transformation matrix is used to map pixel coordinates to geographic coordinates.

transform = from_origin(minx, maxy, pixel_width, pixel_height)


def calculate_area(rasterized_matrix, num_samples=68000):
    # Generate random points
    x_samples = np.random.uniform(minx, maxx, num_samples)
    y_samples = np.random.uniform(miny, maxy, num_samples)

    # Count the number of points inside the polygon
    count = 0
    for x, y in zip(x_samples, y_samples):
        i = int((x - minx) / pixel_width)    # Convert x to column index
        j = int((maxy - y) / pixel_height)   # Convert y to row index
        if rasterized_matrix[j, i] == 1:
            count += 1

    # Calculate the area
    width = maxx - minx
    height = maxy - miny

    area = count / num_samples * width * height
    return area


# Map of NYC

# Rasterize: Convert geometries to a 2D matrix
shapes = [(geom, 1) for geom in world.geometry]  # Assign value 1 to all geometries
rasterized_matrix = rasterize(
    shapes=shapes,
    out_shape=(grid_size, grid_size),  # Define output grid size
    transform=transform,
    fill=0  # Background value
    # (0: background, 1: inside the polygon)
)

# Plot the original map
world.plot(cmap="jet", edgecolor="black", column="name")
plt.title('Dataset Map')
plt.show()

# Plot the rasterized matrix
plt.imshow(rasterized_matrix, cmap='Greys', extent=(minx, maxx, miny, maxy))
plt.title("Rasterized Map")
plt.show()

# Run Monte Carlo simulation to calculate the area of NYC
approximated_area = calculate_area(rasterized_matrix)
print()
print(f"Real area of NYC: {world.area.sum()} square units")
print(f"Approximated Area NYC: {approximated_area:.2f} square units")

print()
print(f"Real area of NYC in square kilometers: {world.area.sum() * calculate_square_unit():.2f} square kilometers")
print(f"Aproximated Area in square kilometers: {approximated_area * calculate_square_unit():.2f} square kilometers")


# Area of Interest
area_of_interest = get_area_of_interest()

# Plot the area of interest
area_of_interest.plot()
plt.title('Area of Interest')
plt.show()

# Rasterize the area of interest
shapes = [(geom, 1) for geom in area_of_interest.geometry]
rasterized_matrix_interest = rasterize(
    shapes=shapes,
    out_shape=(grid_size, grid_size),
    transform=transform,
    fill=0
)

# Plot the rasterized matrix
plt.imshow(rasterized_matrix_interest, cmap='Greys', extent=(minx, maxx, miny, maxy))
plt.title("Rasterized Map Interest Area")
plt.show()


# # Run Monte Carlo simulation to calculate the area of the area of interest
approximated_area_of_interest = calculate_area(rasterized_matrix_interest)

print()
print(f"Real area of Interest: {area_of_interest.area.sum()} square units")
print(f"Aproximated Area of Interest: {approximated_area_of_interest:.2f} square units")


print()
print(f"Real area of Interest in square kilometers: {area_of_interest.area.sum() * calculate_square_unit():.2f} square kilometers")
print(f"Aproximated Area of Interest in square kilometers: {approximated_area_of_interest * calculate_square_unit():.2f} square kilometers")

