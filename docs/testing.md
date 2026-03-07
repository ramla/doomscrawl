# Testing report
<!-- Testausdokumentin pitääs sisältää seuraavat:

- Yksikkötestauksen kattavuusraportti.
- Mitä on testattu, miten tämä tehtiin?
- Minkälaisilla syötteillä testaus tehtiin?
- Miten testit voidaan toistaa?
- Ohjelman toiminnan mahdollisen empiirisen testauksen tulosten esittäminen graafisessa muodossa. (Mikäli sopii aiheeseen) Ei siis riitä todeta, että testaus on tehty käyttäen automaattisia yksikkötestejä, vaan tarvitaan konkreettista tietoa testeistä, kuten:
    * Testattu, että tekoäly osaa tehdä oikeat siirrot tilanteessa, jossa on varma 4 siirron voitto. Todettu, että siirroille palautuu voittoarvo 100000.
    * Testattu 10 kertaan satunnaisesti valituilla lähtö- ja maalipisteillä, että JPS löytää saman pituisen reitin kuin Dijkstran algoritmi.
    * Kummallakin algoritmilla on pakattu 8 MB tekstitiedosto, purettu se ja tarkastettu, että tuloksena on täsmälleen alkuperäinen tiedosto.-->

Tests can be run with `poetry run invoke test` or with the coverage report included `poetry run invoke coverage-report`

## Triangulation

First covered are basic Edge and Triangle class methods. For Edge, calculating midpoint, slope, the perpendicular bisector's slope and y-intercept; for Triangle, calculating radius and circumcentre and whether the method to check if vertex is inside circumcircle works.

The BowyerWatson class itself is tested with some potentially hard cases like triangles with slopes of 0 and infinity and small floats.

### Simulation on Paper

One implemented test compares the algorithm's resulting triangles versus what was drawn on paper. A custom supertriangle override was created to simulate the exact same situation as was reasonable to draw on paper. Additionally when using custom super triangle the list of points is not processed for duplicates through set to preserve order.

[Drawing 1](https://github.com/ramla/doomscrawl/blob/main/docs/images/1.JPG), [Render 1](https://github.com/ramla/doomscrawl/blob/main/docs/images/r1.png): At first we add vertex A. The only triangle is a bad triangle, and the polygon formed by bad triangles is the super triangle XYZ. An edge is drawn from each super vertex to A, forming three triangles. Drawn on paper we can find the two circumcircles that will be violated by adding B. The resulting polygon is XYZA, only the triangle XAY remains.

[Drawing 2](https://github.com/ramla/doomscrawl/blob/main/docs/images/2.JPG), [Render 2](https://github.com/ramla/doomscrawl/blob/main/docs/images/r2.png): An edge is drawn to B from each of the polygon's vertices, forming XDA, XZD, ZYD, DYA. After drawing XDA and ZYD's circumcircles we can see that the latter is violated by adding C. We can also trivially see that ZYD is the only other bad triangle.

[Drawing 3](https://github.com/ramla/doomscrawl/blob/main/docs/images/3.JPG), [Render 3](https://github.com/ramla/doomscrawl/blob/main/docs/images/r3.png): New triangles ZCB, ZYC and CYA are created in the ZYAB polygon. Next we can see that D falls inside ZYC's and CYA's circumcircle, but outside the other triangles'.

[Drawing 4](https://github.com/ramla/doomscrawl/blob/main/docs/images/4.JPG), [Render 4](https://github.com/ramla/doomscrawl/blob/main/docs/images/r4.png): Triangles ZDC, ZYD and ADY are created in the ZYAC polygon. Then, adding E we see it inside the circumcircles of BCA and XBA.

[Drawing 5](https://github.com/ramla/doomscrawl/blob/main/docs/images/5.JPG), [Render 5](https://github.com/ramla/doomscrawl/blob/main/docs/images/r5.png): Edge AB disappears with the two triangles, while AE, BE, CE and EX form the triangles BCE, CAE, XBE and XEA inside XBCA.

[Drawing 6](https://github.com/ramla/doomscrawl/blob/main/docs/images/6.JPG), [Render 6](https://github.com/ramla/doomscrawl/blob/main/docs/images/r6.png): For a five point triangulation we are ready adding points. Now we must remove the triangles connected to supervertices X, Y and Z. The final triangulation contains the triangles BCE, ECA and CDA. We can also notice that there is an intersection of all three circumcircles of the triangulations in the middle.

[Drawing 7](https://github.com/ramla/doomscrawl/blob/main/docs/images/7.JPG), [Render 7](https://github.com/ramla/doomscrawl/blob/main/docs/images/r7.png): Assume we didn't remove the super-connected triangles yet and continued the triangulation by visually aiming point F (420, 400) at the middle of the intersection, we should end up with three bad triangles forming the polygon BCDAE and point F in the middle of it, connecting to the vertices and forming five triangles FAE, FEB, FBC, FCD and FDA. The written test looks for triangles formed with these vertices and asserts equal the amount of triangles that we expect to find in each case.

[Render 8](https://github.com/ramla/doomscrawl/blob/main/docs/images/r8.png): The final triangulation with its circumcircles after adding the sixth point.

### Hardcoded Tests

The first tests written were tests with points that could pose difficult in divisions by zero or other issues and are just expected to run without error. Another case is a known set of points (found in random four points test) that initially generated only one triangle where there ought to have been two.

For a later described random triangle count test, TestBowyerWatson.is_convex_triangulation method is asserted to find a known convex triangulation convex and a known concave triangulation (with the super vertices used in my implementation) concave.

### Random Tests

#### Four Points Test

A most thorough test on all the edge cases Bowyer-Watson can produce with four points and how they're being handled has been implemented. Random four unique points are generated and the validity of the resulting number of triangles or edges is asserted.

Test is repeated with new points 10**3 times. The edge cases encountered (~40 in 1000) can be visually confirmed, the application launches with each excepted point set, which can be cancelled by pressing the space bar. The edge case description reads in the window title. Failing the test with a visual inspection is not implemented.

- All convex triangulations of 4 points should result in two triangles. Convex is determined by checking whether any of the given points lie inside the triangle formed by the other three.

- As the most common exception, when three points lie close enough to being on the same line, point may be correctly detected to lie within the triangle formed by the other points, but due to non-infinite distance to supervertices the result of two triangles is still a valid result of the Bowyer-Watson algorithm. This is how Bowyer-Watson can result in a concave triangulation, even though the Delaunay triangulation is described has having a convex hull.

- In four points, one may be rejected due to hitting another triangle's circumcircle's perimeter exactly enough => one triangle should be found.

- Points location and order of triangulation may cause the sole edge connecting one point to other triangulated points to only form triangles containing supervertices, and thus the edge will get removed in the end. For the use case this is handled by checking for such edge when removing triangles. This case should result in one triangle and four edges.

- If all points lie close to being on the same line, all formed triangles may be supervertex-connected and be removed at the final phase. Again, this is handled and results in no triangles but three edges.

#### No Other Points Inside Circumcircles

1000 points with float coordinates are randomised and triangulated, after which for every triangle in the result every point beside the triangle's own three is checked to not lie within the circumcircle.

#### Random Points Convex Triangulation Triangle Count Test

Iterated a 100 times, a set of points between 5 and 100 in size is randomised and triangulated, and randomised again if the triangulation happens to be concave. From a convex triangulation we can assert the amount of triangles to be equal to n * 2 - h - 2 where n is the number of points in triangulation and h is the number of points on the hull of the triangulation.

### Visualisation

As geometric shapes are harder to comprehend without visuals one can also launch Doomscrawl a list of points (and room sizes) to serve as room centers and then run the it with visible visualisation. The Visualizer class has its own bookkeeping of drawn triangles and its equality with the BowyerWatson class' triangle dictionary is tested.

## Prim's

Prim's algorithm is passed a fully connected graph, after which the returned edges count is asserted to equal amount of nodes - 1. The edges are then converted back to a graph and the graph is explored to assert all nodes are reachable.

## A*

The AStar class' grid is tested to verify the paths it generates along with the rooms form an area whose every square is reachable from a random room or path cell when a Dungeon with randomly generated Rooms with an edgelist from triangulation call for pathing.

The pathing itself is tested with given grids with known best path lengths. The taken route is tested by asserting the weight on the grid has been overwritten to 0 (for corridor weight) where the best path must be taken through.

## Coverage

As mentioned in implementation report, the coverage is not what it should be due to this being the first project where I used tests, resulting in me writing code that is hard to write tests for before considering the tests that would cover it and how.

Some of the code missing coverage is entirely unused and could be removed or could otherwise possibly be turned a blind eye to, but in BowyerWatson coverage report lists an embarrassing uncovered section 118->141 which is the entire section of finding bad triangles in the triangulate_point method.

```
====================== 24 passed in 30.39s =======================
Name                   Stmts   Miss Branch BrPart  Cover   Missing
------------------------------------------------------------------
src/astar.py             131     12     52      6    87%   106->129, 118-119, 145-146, 161-162, 185-186, 223-226, 231
src/bowyer_watson.py     380     48    158      8    85%   118->141, 185, 189-194, 214, 236, 256-264, 280->284, 323, 325, 337->exit, 342-350, 361-371, 376-377, 380, 425, 428, 505, 556, 588-589, 592
src/prims.py              34      1     16      2    94%   17, 24->27
------------------------------------------------------------------
TOTAL                    545     61    226     16    86%
```
