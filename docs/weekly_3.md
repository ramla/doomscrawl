# Weekly Report 3

The project feels like a mess already. The visualisation has its own bugs which is not helping my case. Testing is lagging behind. I got some tests for Edges and Triangles and not even all of those pass. For the actual BowyerWatson class I'm thinking I'll implement some tests that just check that all the triangles that should exist do so and no extra triangles are found, other than that I'm not sure how to approach. Empiric testing option is probably needed here as well but the way the visualisation is currently implemented I assume I'd need to implement tests to confirm my visualisation logic as well?

Reading the Rebay paper again I realise I should just have screen edges as (initial) boundary, not an oversized triangle.

Breaking up the algorithm to run one iteration at a time took most of my time this week, and all bugs introduced along with it in both the algorithm itself and the visualisation. A good crunch was still required to meet some more of week's goals. Number of hours worked this week closed in at 21.

The next chaos is to make further triangulations work after the first one. Simple enough if I just do it all over again, but it should be possible to just add a point wherever. I'm also second guessing the whole visualisation architecture. I should just have the visual classes (or just class) inherit Verts/Edges/Tris.

The boundary edges and triangles I need to keep track of are something I'm unsure of how to implement as well. Their identification might need more functions with geometry. Read about barymetric coordinates, apparently very useful if I need to check whether a point is inside a triangle.

I enabled the pylint extension in VSCode, cleaned up some and ignored some, but it doesn't seem to produce a report unfortunately.

What does "how can the tests be repeated" mean regarding testing report requirements? Is it referring to whether the tests use random values or not and if so, can they be passed a seed, and if not given one, do they output the one used?
