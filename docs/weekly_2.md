# Weekly Report 2

This week started with catching up on and initialising poetry and writing a helloworld test. I proceeded to implement the algorithm along with data structures for the triangulation. As soon as I had a test case failing I was surprised by how little debug info I was able to extract from pytest alone and had to spend time to configure VSCode to run the tests in in order to better see what's going on.

The maths on the circles and triangles proved expectedly unintuitive for me to implement and I spent a lot of time scratching my head and fixing tests and methods in turn. The tests for them I think are not yet comprehensive enough.

Having read some of the Rebay paper (Efficient Unstructured Mesh Generation by Means of Delaunay Triangulation and Bowyer-Watson Algorithm) I had to think through whether my original approach of randomising room positions (to use as points) to generate the triangulation was suitable. In the paper, the algorithm is used to find the points to add to a mesh in order to generate optimally shaped triangles. The dual graph can go both ways I suppose, so maybe after creating the initial couple rooms I can then also use the triangulation to find positions where new rooms might most likely still fit.

Is the code documentation of non-core part of the application as important as the core part? While the instructions say I don't need to write docstrings for all of my methods, I tried to begin the class docstrings for Vertex, Edge and Triangle but it felt like I am parroting what can be just read from method names at a glance. The Triangle class will probably still grow as well.

This week's effort comes together to about 15 hours with the writing of this report. Next I'll start writing the visualisation of points, circles and triangles so as to help with the debugging that will ensue once I call the triangulation with the first list of points.
