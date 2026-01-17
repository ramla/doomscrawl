### Specification document for starting the course

Project will be coded in python utilising mainly the pygame library for visualisation. Planned algorithm to implement is the Bowyer-Watson algorithm to do Delaunay triangulation. The problem to solve with the algorithm is to find reasonable rooms to connect with corridors in a dungeon consisting of random sized rooms in random locations. 

The core of the project is the Delaunay triangulation and the Bowyer-Watson as the first focus point. The hard part of the algorithm is to find the triangles that need changing when another point is added. I aim to first implement and visualise the simple implementation with time complexity of O(n²) first and then see about implementing an O(n log n) version utilising a tree search from a tree of neighboring triangles to find the triangles with conflicting circumcircles. I'll have a closer look at the S. Rebay paper *Efficient Unstructured Mesh Generation by Means of Delaunay Triangulation and Bowyer-Watson Algorithm* which I hear contains the proof of the O(n log n)-ness when implemented this way. I might look into other ways to implement Delaunay triangulation.

The program will be interactive with the user being able to move a character in the generated dungeon and to trigger the triangulation and its visualisation. Corridors might be removed as a result. I am also considering extending the generation and triangulation to happen at will, so that the dungeon can extend inside or possibly even outside of the original screen dimensions.

I am a bSc student. For peer reviewing, I am well prepared to read python or GDScript, less prepared for c/c++, JS. The project will be documented in English.
