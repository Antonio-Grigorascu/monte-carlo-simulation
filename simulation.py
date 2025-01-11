import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
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


num_simulations = 1000
approximated_areas = []
sum_of_accepted = 0
for i in range(num_simulations):
    approximated_area = calculate_area(rasterized_matrix)
    approximated_areas.append(approximated_area)
    accepted_range = [world.area.sum() - world.area.sum() * 0.01, world.area.sum() + world.area.sum() * 0.01]
    if accepted_range[0] <= approximated_area <= accepted_range[1]:
        sum_of_accepted += 1

proportion_accepted = sum_of_accepted / num_simulations

plt.hist(approximated_areas, bins=50, color='blue', alpha=0.7, label='Approximated Areas')
plt.axvline(world.area.sum(), color='red', linestyle='dashed', linewidth=2, label='Actual Area')
plt.axvline(world.area.sum() * 0.99, color='green', linestyle='dashed', linewidth=2, label='1% Error Bound')
plt.axvline(world.area.sum() * 1.01, color='green', linestyle='dashed', linewidth=2)

plt.gca().xaxis.set_visible(False)
plt.xlabel('Area (square units)')
plt.ylabel('Frequency')
plt.title('Distribution of Approximated Areas')
plt.legend()
# save the plot
plt.savefig('distribution_of_approximated_areas.png')
plt.show()




plt.bar(['Accepted', 'Rejected'], [proportion_accepted, 1 - proportion_accepted], color=['green', 'red'])
plt.ylabel('Proportion')
plt.title('Proportion of Accepted Samples (within 1% error)')
# save the plot
plt.savefig('proportion_of_accepted_samples.png')
plt.show()

print(f"Proportion of accepted samples: {proportion_accepted:.2f}")

