import config

class BowyerWatson:
    def __init__(self, points):
        super_triangle = ((0,0), 
                          (config.viewport_x * 2, 0), 
                          (0, config.viewport_y * 2)
                         )
        self.points = points
        self.triangulation = {
            "verts":    super_triangle.copy(),
            "edges":    [
                (super_triangle[0],super_triangle[1]),
                (super_triangle[0],super_triangle[2]),
                (super_triangle[2],super_triangle[1]),
                ],
            "tris":     [
                (super_triangle[0], super_triangle[1], super_triangle[2])
                ]
            }
