from sys import platform
from invoke import task

PTY = True
IS_WINDOWS = platform.startswith("win")
if IS_WINDOWS:
    PTY = False

@task()
def start(ctx, args=""):
    """
    ====== Doomscrawl: A Bowyer-Watson visualiser shoddily disguised as a game"

    ====== Options:
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    **PASS COMMAND-LINE OPTIONS WITH --args=""**, for example:
    poetry run invoke start --args="-r '[(100,150), (600,300), (250,550)]'"
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        -t, --no_freetype
            Do not import pygame.freetype compatibility mode. Help text and
            coordinate rendering not available.

        -p, --paper_case
            Render the paper-simulated test case

        -b, --bw_demo
            Render a sample case with a supertriangle that fits inside viewport
            if it looks confusing when it's outside of it

        -r, --rooms=
            Give coordinates for room centers in Python list format. The rooms
            will be rendered with a small size of 70*70 pixels.
            Example:    -r '[(10,10), (50,20)]'

        -s, --super=
            Give coordinates for custom super triangle in Python list format.
            Example:    -s '[(-1100, -950), (-1100, 1700), (2400, 350)]'

        -d, --dungeon=
            Give a list of (room_center, room_size) tuples
            Example:    -d '[((678, 403), (141, 95)), ((928, 550), (51, 165)), ((734, 120), (146, 75))]'


    ====== KEYBINDS:
       Esc, Q  -  Quit
         WASD  -  Move
            R  -  Randomise another room
            T  -  Triangulate all
            F  -  Step triangulation / Next Phase
        F1, H  -  Display help
    """
    ctx.run(f"python3 src/main.py {args}", pty=PTY)

@task
def test(ctx):
    ctx.run("pytest src", pty=PTY)

@task
def coverage_report(ctx):
    ctx.run("coverage run --branch -m pytest src", pty=PTY)
    ctx.run("coverage report -m", pty=PTY)
