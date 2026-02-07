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
