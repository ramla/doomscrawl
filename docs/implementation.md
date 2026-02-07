# Implementation Document

<!--Toteutusdokumentin tulee sisältää seuraavat:

Ohjelman yleisrakenne

* Saavutetut aika- ja tilavaativuudet (esim. O-analyysit pseudokoodista)
* Suorituskyky- ja O-analyysivertailu (mikäli sopii työn aiheeseen)
* Työn mahdolliset puutteet ja parannusehdotukset
* Laajojen kielimallien (ChatGPT yms.) käyttö. Mainitse mitä mallia on käytetty ja miten. Mainitse myös mikäli et ole käyttänyt. Tämä on tärkeää!
* Lähteet, joita olet käyttänyt, vain ne joilla oli merkitystä työn kannalta.
-->



By iterating through all triangles to find bad ones the algorithm performs at O(n²). This can be observed with n of 10², 10³, 10⁴ AND 10⁵ the algorithm runs at 0.001, 0.05, 1 and 177 seconds respectively (TestBowyerWatson.test_random_points_float).

At the moment you could say only the minimum viable algorithm has been implemented. There is an unsolved problem with how to handle triangles where all points are on the same line which causes problems in my use case if the triangle is just discarded. In addition there is an issue with some combination and order of points where triangle edges come to cross each other, but I have yet to analyse the issue in depth.

Microsoft Copilot Chat has been used for the following:
- Asked for different typical implementation styles of collision detection in pygame to find most suitable one for the dungeon
- Asked for some OOP structuring guidance (triangle & edge classes needing references to other edges)
- Vibeconfigured running tests in VSCode for easier debug
- Asked what was wrong with my circumcenter function after I ran out of ideas, found I was solving x=(c1-c2)/det instead of intended (c2-c1)/det and I was calculating it with the edge's slope instead of the perpendicular bisector's
- Asked about ways of passing callables as arguments in Python, settled with methodcaller
- Dictionary KeyError debug help; learned keys can repr the same but can have different hashes
- Invoke configuration help
- Pygame font rendering debug help (turned out render func returned a surface but I wasn't storing it)

Sources used for the project:
[Wikipedia: Bowyer-Watson algorithm](https://en.wikipedia.org/wiki/Bowyer%E2%80%93Watson_algorithm)
[Wikipedia: Delaunay triangulation](https://en.wikipedia.org/wiki/Delaunay_triangulation)
[S. Rebay: Efficient Unstructured Mesh Generation by Means of Delaunay Triangulation and Bowyer-Watson Algorithm](http://www.electronicsandbooks.com/edt/manual/Magazine/J/Journal%20of%20Computational%20Physics/Volume%20106/1/12.pdf)
[WikiHow: Find the Perpendicular Bisector of Two Points](https://www.wikihow.com/Find-the-Perpendicular-Bisector-of-Two-Points)
[WikiHow: Methods to Find and Solve Circumcenter](https://www.wikihow.com/Find-Circumcenter)
[Efficient Algorithm for Intersection of Two Lines: Comparing Determinants vs. Normal Algebra (No Matrices Needed)](https://www.tutorialpedia.org/blog/algorithm-for-intersection-of-2-lines/#5-practical-examples)
