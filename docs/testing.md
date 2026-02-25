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

<!--I'm basically only testing Edges and Triangles at this point. Coverage percentage is lying because the BowyerWatson tests I run are not really testing much at all.


```
================================== 10 passed in 0.27s ===================================
Name                   Stmts   Miss Branch BrPart  Cover   Missing
------------------------------------------------------------------
src/bowyer_watson.py     283     47    122     15    79%   27-33, 44, 48, 53, 71->69,
                                                           81->94, 92-93, 95-96, 113->110,
                                                           137, 147-149, 157-162, 166-171,
                                                           175-180, 186-188, 213, 230,
                                                           233, 243->246, 255->258,
                                                           348-349, 372, 375, 378
------------------------------------------------------------------
TOTAL                    283     47    122     15    79%
```
-->

Testing covers basic Edge and Triangle class methods. For Edge, calculating midpoint, slope, the perpendicular bisector's slope and y-intercept; for Triangle, calculating radius and circumcentre and whether the method to check if vertex is inside circumcircle works.

The Visualizer class has its own bookkeeping of drawn triangles and its equality with the BowyerWatson class triangle dictionary is tested. Edges and vertices are on todo-list.

The BowyerWatson class itself is tested with some potentially hard cases like triangles with slopes of 0 and infinity and small floats.

Tests, apart from performance testing, can be run with `poetry run invoke coverage-report`

As geometric shapes are harder to comprehend without visuals one can also launch Doomscrawl a list of points [and room sizes] to serve as room centers and then run the it with visible visualisation. At the moment this can be done only by editing main.py.

One implemented test compares the algorithm's resulting triangles versus what was drawn on paper. A custom supertriangle override was created to simulate the exact same situation as was reasonable to draw on paper. Additionally when using custom super triangle the list of points is not processed for duplicates through set to preserve order. At first we add vertex A. The only triangle is a bad triangle, and the polygon formed by bad triangles is the super triangle XYZ. An edge is drawn from each super vertex to A, forming three triangles. Drawn on paper we can find the two circumcircles that will be violated by adding B. The resulting polygon is XYZA, only the triangle XAY remains. 

An edge is drawn to B from each of the polygon's vertices, forming XDA, XZD, ZYD, DYA. After drawing XDA and ZYD's circumcircles we can see that the latter is violated by adding C. We can also trivially see that ZYD is the only other bad triangle.

New triangles ZCB, ZYC and CYA are created in the ZYAB polygon. Next we can see that D falls inside ZYC's and CYA's circumcircle, but outside the other triangles'.

Triangles ZDC, ZYD and ADY are created in the ZYAC polygon. Then, adding E we see it inside the circumcircles of BCA and XBA. Edge AB disappears with the two triangles, while AE, BE, CE and EX form the triangles BCE, CAE, XBE and XEA inside XBCA.

For a five point triangulation we are ready adding points. Now we must remove the triangles connected to supervertices X, Y and Z. The final triangulation contains the triangles BCE, ECA and CDA. We can also notice that there is an intersection of all three circumcircles of the triangulations in the middle. 

Assume we didn't remove the super-connected triangles yet and continued the triangulation by visually aiming point F (420, 400) at the middle of the intersection, we should end up with three bad triangles forming the polygon BCDAE and point F in the middle of it, connecting to the vertices and forming five triangles FAE, FEB, FBC, FCD and FDA. The written test looks for triangles formed with these vertices and asserts equal the amount of triangles that we expect to find in each case.

```
================= 13 passed in 291.69s (0:04:51) =================
Name                   Stmts   Miss Branch BrPart  Cover   Missing
------------------------------------------------------------------
src/bowyer_watson.py     308     29    136     13    88%   72->74,
84, 103->105, 109-115, 124->137, 135-136, 156->158, 188-190,
199->exit, 210->exit, 220, 222->exit, 233->236, 240-242, 254-268,
273, 276, 279, 329, 351->354, 441-442
------------------------------------------------------------------
TOTAL                    308     29    136     13    88%
```
