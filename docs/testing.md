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

I'm basically only testing Edges and Triangles at this point. Coverage percentage is lying because the BowyerWatson tests I run are not really testing much at all.

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
