# OpenGlassBox Python

A Python port of [OpenGlassBox](https://github.com/Lecrapouille/OpenGlassBox), a city-simulation
engine modelled on GlassBox, the engine behind Maxis's SimCity (2013). Cities are grids of resource
maps; units sit on a road network, run rules against the resources around them, and dispatch agents
that carry resources from one unit to another. The engine itself is pure standard-library Python.
The demo renders it with pygame.

## Credits and lineage

This project is a port, and almost none of the design is mine.

- **[OpenGlassBox](https://github.com/Lecrapouille/OpenGlassBox)** by **Quentin Quadrat** — the C++
  implementation this port is translated from. Copyright (c) 2020 Quentin Quadrat, MIT licensed.
  The class names used here (`City`, `Node`, `Way`, `Resources`, `ScriptParser`) are his renamings of
  the original GDC terminology, and the `Dijkstra` class replaces the original dynamic A\*.
- **[MultiAgentSimulation](https://github.com/federicodangelo/MultiAgentSimulation)** by
  **federicodangelo** — the original C# implementation for Unity, which Quadrat ported to C++.
- **[Inside GlassBox](http://www.andrewwillmott.com/talks/inside-glassbox)** by **Andrew Willmott** —
  the GDC 2012 talk describing the engine. Since the original video is gone, an alternative recording
  is at https://youtu.be/eZfj7LEFT98.

This is neither Maxis released source nor a project affiliated with Maxis. It reimplements ideas
described in a public conference talk.

## Status

The engine and the demo run. The port is incomplete, and the repository has some rough edges worth
knowing about before you spend time here.

- **Tests**: 68 pass, 35 fail, 23 are skipped as unimplemented. Two further modules fail to collect
  at all, so a plain `pytest tests/` aborts before running anything. See [Tests](#tests).
- **Packaging does not work.** `pip install .` produces an empty distribution, because
  `pyproject.toml` looks for an `openglassbox` package that does not exist — the code lives in `src/`
  and `demo/`. Run from source instead.
- **One entry point works**: `python demo/src/main.py`. The Makefile's `run-demo` and `run-enhanced`
  targets are both broken, and so are `test-all`, `lint`, and `dev-setup`. Prefer the direct commands
  in this README over `make`.

## Requirements

Python 3.8 or newer, and pygame for the demo. Nothing in `src/` imports pygame — the simulation
engine runs on the standard library alone.

```sh
python -m venv venv
venv/Scripts/activate        # Windows
# source venv/bin/activate   # Linux and macOS
pip install -r requirements.txt
```

## Running the demo

From the repository root:

```sh
python demo/src/main.py
```

The only flag is `--debug`, which sets `OPENGLASSBOX_DEBUG=1` and turns on per-agent logging.

The demo opens a 1024x768 resizable window on a 12x12 grid and **starts paused** — press `P` to run
it. It builds two cities from `demo/src/data/TestCity.txt`: Paris at (400, 200) with three nodes in a
triangle, two `Home` units and two `Work` units, and Versailles at (0, 30) with two nodes, one `Home`
and one `Work`, connected back to Paris.

What you are looking at: pink squares are houses, cyan squares are workplaces, grey lines and dots
are ways and nodes, yellow triangles are people heading to work, white triangles are people heading
home, blue is water produced by workplaces, and green is grass consuming water.

## Controls

All of these live in `demo/src/input_handler.py`.

| Key | Action |
|-----|--------|
| `P` | Pause and resume — the demo starts paused |
| `ESC` | Quit |
| `M` | Toggle maps |
| `L` | Toggle paths |
| `U` | Toggle units |
| `A` | Toggle agents |
| `D` | Toggle the debug panel, bottom left — on by default |
| `I` | Toggle the color legend, top right |
| `C` | Toggle the comprehensive debug sidebar, right |
| `T` | Toggle the tick counter |
| `R` | Reset camera and zoom |
| `F5` | Restart the simulation |
| `F11` or `Alt+Enter` | Toggle fullscreen |

The mouse wheel zooms, dragging pans, and the window can be resized live.

Two caveats. The startup banner advertises `Ctrl+R` for restart, but it is unreachable — the plain
`R` case is tested first, so `Ctrl+R` just resets the view. Only `F5` restarts. And mouse clicks on
the debug panels do nothing; `GlassBoxDemo.handle_mouse_click` is an empty stub.

## The simulation script

Scenarios are written in a small DSL parsed by `src/script_parser.py`. The grammar is specified in
[`diary/DSL_SPEC.md`](diary/DSL_SPEC.md).

The only scenario in the repo is `TestCity.txt`. It declares three resources (Water, Grass, People),
a `Road` path type and a `Dirt` segment type, two agent types (`People` and `Worker`, both speed 10),
two unit types (`Home`, which sends people to work, and `Work`, which sends them home and converts
people into water), and two maps (Water at capacity 100, Grass at capacity 10 growing under the
`CreateGrass` rule).

It exists in three byte-identical copies, at `data/simulations/`, `demo/data/Simulations/`, and
`demo/src/data/`. The demo loads the last of these. Note that some code paths spell the directory
`Simulations` with a capital S, which resolves on Windows but would fail on a case-sensitive
filesystem.

## Project layout

```
src/                        Simulation engine, no pygame dependency
  simulation.py             Simulation, the fixed-timestep loop (200 ticks/s)
  city.py                   City, the container for maps, paths, units, agents
  map.py                    Map, the 2D resource grid
  path.py                   Path, Node, Way — the road graph
  unit.py                   Unit, stationary entities that run rules
  agent.py                  Agent, mobile resource carriers
  resource.py resources.py  A single resource amount, and a container of them
  rule.py rule_command.py rule_value.py
                            The rule system and its commands
  script_parser.py          The scenario DSL parser
  dijkstra.py               Shortest-path search
  map_coordinates_inside_radius.py map_random_coordinates.py
                            Grid-cell iterators
  vector.py node.py config.py

demo/src/
  main.py                   The working entry point
  demo.py                   GlassBoxDemo, the pygame window and render loop
  city_setup.py             Builds Paris and Versailles from a scenario
  input_handler.py          All keyboard and mouse handling
  ui_renderer/              The live debug UI (three overlays) and renderers
  Display/debug_ui.py       A Dear ImGui-style UI that is NOT wired in — see below

tests/                      21 pytest modules and 12 debug_*.py investigation scripts
data/, demo/data/           Copies of TestCity.txt
diary/                      Development notes and documentation
```

### On the debug UI

There are two debug UI implementations, and only one is live. `demo/src/ui_renderer/` is what the
demo actually draws: a small state panel on `D`, a color legend on `I`, and a full-height inspector
sidebar on `C` showing agents, units, maps, and paths. The sidebar only ever inspects the first city,
so Versailles is never shown.

`demo/src/Display/debug_ui.py` is a separate Dear ImGui-style implementation with collapsing headers
and tree nodes. Nothing imports it, and it has drifted out of sync with the engine — it calls
`resource.getAmount()`, which no longer exists. Treat it as dead code.

## Tests

```sh
python -m pytest tests/
```

Run it from the repository root. `src/` has no `__init__.py` and there is no `conftest.py`, so imports
resolve only because `python -m pytest` puts the working directory on `sys.path`. The bare `pytest`
command is not equivalent and will fail.

As of now the suite aborts during collection, because two modules cannot be imported:
`tests/test_debug_ui.py` has a syntax error on line 12 (`import debug_ui DebugUI`), and
`tests/test_demo_integration.py` imports `demo_enhanced`, a module deleted in commit `487b572`.
Skip both to run the rest:

```sh
python -m pytest tests/ --ignore=tests/test_debug_ui.py --ignore=tests/test_demo_integration.py
```

That gives 68 passed, 35 failed, 23 skipped. Most failures are drift between the tests and the
implementation rather than broken simulation logic — the tests call `addNode` where the code defines
`add_node`, construct `Resource` with a signature it does not have, and try to instantiate the
abstract `IRuleValue`. The 23 skips are explicit, marking parts of the port that were never finished.

## Known gaps

Beyond the test failures, these are the structural issues a contributor will run into:

- Type definitions are duplicated. `MapType`, `PathType`, `UnitType`, and `WayType` each exist in two
  or three of `src/city.py`, `src/map.py`, `src/path.py`, and `src/script_parser.py`.
- `Node` is defined twice, in `src/node.py` and in `src/path.py`. `dijkstra.py` imports the former
  while `Path.add_node` builds the latter.
- `City.Listener` uses snake_case hooks (`on_city_added`) while `Simulation.Listener` uses camelCase
  (`onCityAdded`), so the demo's listener overrides are never called.
- `src/agent.py` hardcodes 60 ticks per second, contradicting the 200 in `src/simulation.py`.
- `src/config.py` defines `GRID_SIZE`, but `src/city.py` and `src/node.py` each hardcode their own
  copy instead of importing it.

## Documentation

- [`diary/DSL_SPEC.md`](diary/DSL_SPEC.md) — the scenario file grammar.
- [`diary/DEVELOPER_GUIDE.md`](diary/DEVELOPER_GUIDE.md) — a walkthrough of the architecture.
- `diary/day1.md`, `day2.md`, `day4.md`, and `PORTING_SESSION_SUMMARY.md` are a development journal
  kept during the port. They are historical and describe a layout the repository no longer has.

## License

MIT. See [`LICENSE`](LICENSE).

The original C++ OpenGlassBox is Copyright (c) 2020 Quentin Quadrat and is MIT licensed, as is
federicodangelo's C# MultiAgentSimulation upstream of it. Both notices are preserved in `LICENSE`.
