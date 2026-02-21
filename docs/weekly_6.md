### Weekly Report 6

My implementation may be the slowest ever created in this course due to bad architectural decisions made early on and the focus on visualisation, but at least it now runs in O(n log n) time due to now finding the conflicting circumcircles by looking at neighboring triangles after finding the first one, instead of looping through all of them.

A state machine was finally implemented to the game so that when adding Prim's and A-star my interface logic wouldn't be a jungle of booleans. A-star and Prim's were both succesfully implemented, however the visual quality of the added corridors is still subjectively not on an acceptable level.

A lot of time was spent sorting out the visualisation as well, as accumulated technical debt caused or revealed more bugs.

Testing is lagging behind but completing all functionality for the demo is more pressing atm. Still I found a suitable moment to implement a test for none of the final triangles' circumcircles containing inappropriate points.

24 hours spent this week.
