# User Guide

## Running
- Clone repo
- `poetry install`

- Run program:
`poetry run invoke start`
- Run tests only:
`poetry run invoke test`
- Run the tests, get coverage report:
`poetry run invoke coverage-report`
- Run with paper simulated points and super triangle:
`poetry run invoke start --args="-s"`

## Usage
- `Esc, Q` to quit
- `WASD` to move character
- `R` to randomise new room (if no room list supplied)
- `T` to triangulate all points
- `F` - do-it-all -button: step triangulation, activate next phase

## Command-Line Options:

**PASS COMMAND-LINE OPTIONS WITH --args=""**, for example:
>`poetry run invoke start --args="-r '[(100,150), (600,300), (250,550)]'"`


**`-t, --no_freetype`**<br>
Do not import pygame.freetype compatibility mode. Help text and coordinate rendering not available.

**`-r, --rooms=`**<br>
Give coordinates for room centers in Python list format. The rooms will be rendered with a small size of 70*70 pixels.
> `-r [(10,10), (50,20)]`

**`-s, --super=`**<br>
Give coordinates for custom super triangle in Python list format. Can
also be given as the only argument to launch relevant test case with
rooms A to F.

> `-s [(-1100, -950), (-1100, 1700), (2400, 350)]`
