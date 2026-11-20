"""Stage 4 · Leakage tests. Make these real once the split is implemented.

The rules every project must pass:
1. No test timestamp appears in train (time split).
2. No group (well / machine) appears in both train and test (group split).
3. Every feature at time t uses only data with timestamp <= t.
"""

import pytest


@pytest.mark.skip(reason="Enable in stage 4 once split + features exist")
def test_no_time_overlap(): ...


@pytest.mark.skip(reason="Enable in stage 4 once split + features exist")
def test_no_group_overlap(): ...


@pytest.mark.skip(reason="Enable in stage 4 once features exist")
def test_features_use_only_past(): ...
