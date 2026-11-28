import pandas as pd

from oil_well_event_early_warning.data.load import build_index


def test_build_index_parses_names(tmp_path):
    for rel in [
        "0/WELL-00001_20170101000000.parquet",
        "5/SIMULATED_00001.parquet",
        "7/DRAWN_00001.parquet",
    ]:
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.touch()
    idx = build_index(tmp_path).set_index("source")
    assert idx.loc["real", "well_id"] == "WELL-00001"
    assert idx.loc["real", "start_time"] == pd.Timestamp("2017-01-01")
    assert idx.loc["simulated", "event"] == 5
    assert idx.loc["drawn", "event"] == 7
    assert idx["instance_id"].is_unique
