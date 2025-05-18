@echo off

echo.
echo Running development checks...

echo.
echo Running black...
black ./stat_arb
black ./tests

echo.
echo Running flake8...

flake8 ./stat_arb
flake8 ./tests

echo.
echo Running mypy...

mypy ./stat_arb --check-untyped-defs
mypy ./tests --check-untyped-defs

echo.
echo Development checks complete.
