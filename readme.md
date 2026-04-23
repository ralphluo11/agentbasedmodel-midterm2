# Axelrod (1997) — Dissemination of Culture

A Mesa 3.1.4 implementation of Axelrod's cultural dissemination model.

## How to run

```bash
pip install mesa solara
solara run app.py
```

Adjust parameters in the left sidebar, then press Play. The simulation 
halts automatically when a stable state is reached.

## Files

- `model.py` — `CultureModel` class, region counter (BFS), stability check
- `agents.py` — `CultureAgent` with Axelrod's interaction rule
- `app.py` — SolaraViz GUI with grid visualization and regions-over-time plot
