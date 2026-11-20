"""Stage 3 · Data-quality contract.

Turn every EDA finding into a rule here. The same schema is reused later in
production (Project 3) to quarantine bad batches before inference.
Docs: https://pandera.readthedocs.io/
"""

from __future__ import annotations

import pandera.pandas as pa

# Example — replace with real columns after EDA.
RAW_SCHEMA = pa.DataFrameSchema(
    columns={
        # "timestamp": pa.Column("datetime64[ns]", nullable=False),
        # "pressure_bar": pa.Column(float, pa.Check.in_range(0, 500), nullable=True),
    },
    strict=False,
    coerce=True,
)
