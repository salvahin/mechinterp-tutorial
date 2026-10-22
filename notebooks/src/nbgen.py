"""Tiny helper shared by build_nb0/1/2.py: one source -> student + solutions notebooks.

Cells are declared with md(), code(), or exercise(student_src, solution_src).
Solutions get the full code; students get the TODO scaffold (which must still
run end to end thanks to a fallback).
"""
from pathlib import Path
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

ROOT = Path(__file__).resolve().parents[1]  # notebooks/

# Versions tested on the build machine (pip show) -- keep in one place.
PINS = {
    "transformer_lens": "3.9.0",
    "sae-lens": "6.54.12",
    "circuitsvis": "1.43.3",
    "scikit-learn": "1.9.1",
    "datasets": "5.1.0",
    "plotly": "7.1.0",
    "circuit-tracer": "0.5.0",
}

SLIDES_LINK = "[⬅ Back to slides](https://salvahin.github.io/mechinterp-tutorial/slides/deck.html)"


def md(src):
    return ("md", src.strip("\n"), None)


def code(src):
    return ("code", src.strip("\n"), None)


def exercise(student, solution):
    return ("ex", student.strip("\n"), solution.strip("\n"))


def build(cells, student_name, solution_name):
    for version in ("student", "solutions"):
        nb = new_notebook()
        nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
        nb.metadata["language_info"] = {"name": "python"}
        nb.metadata["colab"] = {"provenance": [], "toc_visible": True}
        for kind, a, b in cells:
            if kind == "md":
                nb.cells.append(new_markdown_cell(a))
            elif kind == "code":
                nb.cells.append(new_code_cell(a))
            else:
                nb.cells.append(new_code_cell(a if version == "student" else b))
        name = student_name if version == "student" else solution_name
        out = ROOT / version / name
        out.parent.mkdir(parents=True, exist_ok=True)
        nbformat.validate(nb)
        nbformat.write(nb, out)
        print("wrote", out)
