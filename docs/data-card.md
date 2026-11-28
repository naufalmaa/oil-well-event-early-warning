# Data card: 3M DDataset 2.0.0 (Petrobras)

Format inspired by *Datasheets for Datasets* (Gebru et al.): https://arxiv.org/abs/1803.09010

| Field | Value |
|---|---|
| Source | https://github.com/petrobras/3W |
| Licence | CC BY 4.0 (data), Apache 2.0 (toolkit) |
| Owner / attribution text | Petrobras, 3W Dataset 2.0.0 (Vargas et al.) |
| Version / download date | 2.0.0 (dataset.ini), downloaded 23 Nov 2026 |
| SHA-256 of raw files | see `configs/default.yaml` |
| Rows × columns | |
| Time span | |
| Sampling frequency | 1 Hz |
| Units (assets, wells, machines) | 	27 sensors: pressures [Pa], temperatures [°C], flows [m³/s], choke openings [%], valve states [0/0.5/1] |
| Labels: what, by whom, how | class: 0 normal, 1–9 event steady state, 101–109 transient (offset 100; events 3 and 4 have none). state: well operating status (0 open, 1 shut-in, …) |

## Known quality issues (from EDA)

| Issue | Columns | Size | Handling |
|---|---|---|---|

## What this data cannot support

-
