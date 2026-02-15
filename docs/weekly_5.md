# Weekly Report 5

This week was a tiring bug hunt to reduce inaccurate triangulations found with random four points test. I made sense of the edge cases and categorised them for acceptable test results, or in case of points ending up within an error margin of the perimeter of an existing triangle's circumcircle I now reject the point entirely if between triangulating the rest of the points the triangulation hasn't changed favourably to triangulate the problematic point at the end. This makes for a big hit on performance if you try triangulating regularly spaced points. As it is not an expected use case, I don't mind.

Visualisation improved somewhat as well. For the actual game one can now firts triangulate one set of rooms, add more rooms and triangulate the new rooms into the existing triangulation.

A good amount of time was also spent code reviewing peer project. What was there turned out to be terse but decently executed and I found less to comment on it than I expected.

Next week's todo list includes the apparently expected Prim's and A-star in addition to the corridor creation itself. Focus will be on functionality instead of tests and docs since there still seems to be much to do for the demo.

33.5h this week
