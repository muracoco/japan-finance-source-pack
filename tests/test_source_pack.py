from __future__ import annotations

from argparse import Namespace

from japan_finance_source_pack.cli import build_pack


def test_build_pack_without_network_flags() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        skip_jquants=True,
        output="",
    )

    pack = build_pack(args)

    assert pack["stock"]["code"] == "7203"
    assert pack["retrieved_sources"]["company_ir"]
    assert pack["retrieved_sources"]["jpx_public"] == []
    assert pack["retrieved_sources"]["jquants_free"] == []
