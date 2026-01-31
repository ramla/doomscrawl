from invoke import task
from sys import platform

pty = True
IS_WINDOWS = platform.startswith("win")
if IS_WINDOWS:
    pty = False


@task
def start(ctx):
    ctx.run("python3 src/main.py", pty=pty)

@task
def test(ctx):
    ctx.run("pytest src", pty=pty)

@task
def coverage_report(ctx):
    ctx.run("coverage run --branch -m pytest src", pty=pty)
    ctx.run("coverage report -m", pty=pty)