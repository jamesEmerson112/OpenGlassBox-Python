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

The simulation engine, pygame demo, packaging, automated tests, and optional tick-by-tick session
recording are available. The port remains a work in progress.

## Requirements

Python 3.10 or newer. Pygame is the only runtime dependency and is used by the demo; the simulation
engine itself does not import it.

```sh
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # Linux and macOS
python -m pip install -e ".[dev]"
```

## Running the demo

From the repository root:

```sh
python -m demo.src.main
```

After installation, `openglassbox-demo` runs the same entry point. Pass `--debug` to enable
per-agent logging or `--no-record` to disable the JSON session recording written when the demo
exits.

The demo opens a 1024x768 resizable window on a 12x12 grid and **starts paused** — press `P` to run
it. It builds two cities from `demo/data/Simulations/TestCity.txt`: Paris at (400, 200) with three nodes in a
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

Scenarios are written in a small DSL parsed by `openglassbox/script_parser.py`. The grammar is
specified in [`docs/DSL_SPEC.md`](docs/DSL_SPEC.md).

The only scenario in the repo is `TestCity.txt`. It declares three resources (Water, Grass, People),
a `Road` path type and a `Dirt` segment type, two agent types (`People` and `Worker`, both speed 33),
two unit types (`Home`, which sends people to work, and `Work`, which sends them home and converts
people into water), and two maps (Water at capacity 100, Grass at capacity 10 growing under the
`CreateGrass` rule).

The demo loads the scenario from `demo/data/Simulations/TestCity.txt`.

## Project layout

```
openglassbox/               Installable simulation-engine package
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

tests/                      Pytest test suite
scripts/debug/              Debug and diagnostic scripts
docs/                       Developer documentation and development diary
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
python -m pytest
```

Run the suite from the repository root after installing the development dependencies.

## Documentation

- [`docs/DSL_SPEC.md`](docs/DSL_SPEC.md) — the scenario file grammar.
- [`docs/DEVELOPER_GUIDE.md`](docs/DEVELOPER_GUIDE.md) — a walkthrough of the architecture.
- `docs/diary/day1.md`, `day2.md`, and `day4.md` are the historical development journal.
- [`docs/PORTING_SESSION_SUMMARY.md`](docs/PORTING_SESSION_SUMMARY.md) summarizes the porting work.

## License

MIT. See [`LICENSE`](LICENSE).

The original C++ OpenGlassBox is Copyright (c) 2020 Quentin Quadrat and is MIT licensed, as is
federicodangelo's C# MultiAgentSimulation upstream of it. Both notices are preserved in `LICENSE`.
