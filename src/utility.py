import random

def get_random_points_float(n, min_coords, max_coords):
    return [(random.uniform(min_coords[0], max_coords[0]),
                random.uniform(min_coords[1], max_coords[1])) for _ in range(n)]

def get_random_points_int(n, min_coords, max_coords):
    return [(random.randint(min_coords[0], max_coords[0]),
                random.randint(min_coords[1], max_coords[1])) for _ in range(n)]
