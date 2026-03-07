# Implementation Document

<!--Toteutusdokumentin tulee sisältää seuraavat:

* Suorituskyky- ja O-analyysivertailu (mikäli sopii työn aiheeseen)
* Laajojen kielimallien (ChatGPT yms.) käyttö. Mainitse mitä mallia on käytetty ja miten. Mainitse myös mikäli et ole käyttänyt. Tämä on tärkeää!
* Lähteet, joita olet käyttänyt, vain ne joilla oli merkitystä työn kannalta.
-->
## Application Structure

After arguments are interpreted, the program is run by creating a Doomscrawl class. This initialises pygame with BowyerWatson, Dungeon, Visualizer, Player and StateMachine objects. Vertex, Edge and Triangle classes are utilised in Visualizer as well as BowyerWatson. Dungeon creates Rooms as a subclass of pygame's Rect. StateMachine is used to handle order of operation in the game loop.

The first state change happens when points are passed to BowyerWatson for triangulation. Triangulation is either stepped or done all at once, after which the final edges are filtered to a minimum spanning tree with prim's and the result is supplemented with random edges. They are then passed to the AStar class via Dungeon's create_corridors. When the first Corridor calls the get_path method of AStar, it generates the grid it's going to operate on and fetches the door locations from Rooms.

While Dungeon handles Rooms and Corridors, Visualizer handles objects to draw that are not game-related - vertices, edges, triangles and circumcircles. The Visualizer's event queue is pointed to relevant objects so they can put methodcaller objects for Visualizer methods to be called by Visualizer when it's its turn in the game loop. Visualizer delays the calls so that visualisation happens at a comfortable pace for the user.

## On Time and Space Complexities

I initially implemented the naive O(n²) Bowyer-Watson and then tried to improve on it by reducing the number of triangles explored for a theoretical O(n log n). Since the bad triangles will be found neighboring each other, when the first bad triangle is found it is trivial to check its neighbors next. I do this by keeping track of triangles by edge. If the neighboring triangle is not a bad triangle the cavity polygon does not extend further. While implementing and debugging this neighbor checking method I forgot about the small detail of the search for the first bad triangle must be of O(log n) for the algorithm to perform in O(n log n). Thus even though the performance improvement was noticeable, I'm still iterating to find the first bad triangle and the change did not alter the time complexity from O(n²) at all. The space complexity on the other hand is just O(n) since it depends on the amount of triangles, which is not exponential.

Prim's, implemented with Python's heapq which is a binary heap, has the time complexity of O(m log n) where m is the number of edges and n is the number of nodes in the graph, with space complexity of O(n+m) for the heaped edges and visited nodes. Finally the implemented A* is at worst O(4^d) for both time and space: four possible directions in the grid and d length of best path handled with heapq.

## What Would I Change?

While I think I succeeded in my target of step-by-step visualisation, all in all I spent way too much time on it and its problems. The complex objects I created early on might have been partly necessary, but for the scope of the project they were a hindrance, as was the break from the gridded operation in suggested implementation. By the time I was implementing A* I had to retrofit a grid back to the free coordinate system I'd created and it was messy to get right, and the resulting AStar class is proper spaghetti tied to operating with a Dungeon class. Visualisation-wise there is some code that is finally not even used and things are added to the visualisation event queue in different ways. I attribute a lot of these mistakes to inexperience.

Testing, especially the coverage, suffered from the fast expansion of the amount of classes and methods without knowing better. I wrote my first test in this project.

If I wasn't so cooked with the hours put into studies this period, I'd implement the O(log n) search for the triangles. An R-tree or a tree created from the changes made to the triangulation should work.

Less relevant to the course's thick of the meat, the config should be reworked so that changes to the values could be made while running, or for some properties, even passed as arguments at launch. The lack of scaling with window size in real time is also embarrassing to me.

## LLM Use Report

Microsoft Copilot Chat has been used for the following:
- Asked for different typical implementation styles of collision detection in pygame to find most suitable one for the dungeon
- Asked for some OOP structuring guidance (triangle & edge classes needing references to other edges)
- Vibeconfigured running tests in VSCode for easier debug
- Asked what was wrong with my circumcenter function after I ran out of ideas, found I was solving x=(c1-c2)/det instead of intended (c2-c1)/det and I was calculating it with the edge's slope instead of the perpendicular bisector's
- Asked about ways of passing callables as arguments in Python, settled with methodcaller
- Dictionary KeyError debug help; learned keys can repr the same but can have different hashes
- Invoke configuration help
- Pygame font rendering debug help (turned out render func returned a surface but I wasn't storing it)
- More of the things like the ones listed above. No code was generated for the project.

## Sources

[Wikipedia: Bowyer-Watson algorithm](https://en.wikipedia.org/wiki/Bowyer%E2%80%93Watson_algorithm)
[Wikipedia: Delaunay triangulation](https://en.wikipedia.org/wiki/Delaunay_triangulation)
[S. Rebay: Efficient Unstructured Mesh Generation by Means of Delaunay Triangulation and Bowyer-Watson Algorithm](http://www.electronicsandbooks.com/edt/manual/Magazine/J/Journal%20of%20Computational%20Physics/Volume%20106/1/12.pdf)
[WikiHow: Find the Perpendicular Bisector of Two Points](https://www.wikihow.com/Find-the-Perpendicular-Bisector-of-Two-Points)
[WikiHow: Methods to Find and Solve Circumcenter](https://www.wikihow.com/Find-Circumcenter)
[Efficient Algorithm for Intersection of Two Lines: Comparing Determinants vs. Normal Algebra (No Matrices Needed)](https://www.tutorialpedia.org/blog/algorithm-for-intersection-of-2-lines/#5-practical-examples)
[Accurate point in triangle test](https://totologic.blogspot.com/2014/01/accurate-point-in-triangle-test.html)
