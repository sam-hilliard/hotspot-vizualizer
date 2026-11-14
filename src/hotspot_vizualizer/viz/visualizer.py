#!/usr/bin/env python3

from pathlib import Path
from typing import Iterable

import plotly.express as px
import plotly.graph_objects as go

from models.source_file import SourceFile

class TreemapViz:

    def __init__(self, files: Iterable[SourceFile], output_path: str = "hotspots.html", color_by: str = "hotspot_density", ):
        self.files = list(files)
        self.output_path = output_path
        self.color_by = color_by

        self.fig = None

    def _build_dataframe(self):
        import pandas as pd

        rows = []

        directories = {}

        for source_file in self.files:
            path = Path(source_file.path)

            parent = ""

            # Build directory hierarchy.
            for directory in path.parent.parts:
                current = f"{parent}/{directory}" if parent else directory

                if current not in directories:
                    directories[current] = {
                        "id": current,
                        "name": directory,
                        "parent": parent,
                        "loc": 0,
                        "hotspot_count": 0,
                        "hotspot_density": 0,
                    }

                parent = current

            # Add file.
            rows.append({
                "id": str(path),
                "name": path.name,
                "parent": parent,
                "loc": source_file.loc,
                "hotspot_count": source_file.hotspot_count,
                "hotspot_density": source_file.hotspot_density,
            })

        # Include directories and files.
        directory_rows = list(directories.values())

        return pd.DataFrame(directory_rows + rows)

    def _build_treemap(self):
        """
        Generate the hierarchical Plotly treemap.
        """

        df = self._build_dataframe()

        self.fig = px.treemap(
            df,
            names="name",
            parents="parent",
            ids="id",
            values="loc",
            color=self.color_by,
            color_continuous_scale=[
                [0.0, "#2ecc71"],
                [0.5, "#f1c40f"],
                [1.0, "#e74c3c"],
            ],
            custom_data=[
                "id",
                "loc",
                "hotspot_count",
                "hotspot_density",
            ],
            hover_data={
                "id": True,
                "loc": True,
                "hotspot_count": True,
                "hotspot_density": ":.2f",
            },
        )


        self.fig.update_layout(
            title="Codebase Hotspot Visualization",
            margin=dict(t=50, l=10, r=10, b=10),
            coloraxis_colorbar=dict(
                title="Hotspot Density"
            ),
        )

        return self.fig

    def generate(self):
        """
        Generate and export the interactive treemap.
        """

        fig = self._build_treemap()

        fig.write_html(
            self.output_path,
            include_plotlyjs=True,
            full_html=True,
            config={
                "displayModeBar": True,
                "responsive": True,
            },
        )

        return fig

    def show(self):
        """
        Display the treemap in a browser.
        """

        if self.fig is None:
            self._build_treemap()

        self.fig.show()
