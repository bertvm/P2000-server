#!/usr/bin/env python3
"""Smoke tests for FLEX line parsing (no SDR required)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from publisher.publisher import build_alert, parse_flex_line  # noqa: E402
from publisher.services import detect_priority, detect_service  # noqa: E402


def test_parse_text_flex() -> None:
    line = "FLEX|2026-09-20 10:32:15|1600|5|1420054|ALN|P 1 Amsterdam Amstel woningbrand"
    alert = parse_flex_line(line)
    assert alert is not None
    assert alert["schema"] == 1
    assert "woningbrand" in alert["message"]
    assert alert["service"] == "brandweer"
    assert alert["priority"] == "P1"
    assert any(c["capcode"] == "1420054" for c in alert["capcodes"])


def test_parse_json_flex() -> None:
    line = '{"demod":"FLEX","address":"1512345","message":"A1 Rotterdam centrum reanimatie"}'
    alert = parse_flex_line(line)
    assert alert is not None
    assert alert["service"] == "ambulance"
    assert alert["priority"] == "A1"
    assert alert["capcodes"][0]["capcode"] == "1512345"


def test_parse_flex_next_drops_garbage() -> None:
    good = (
        "FLEX_NEXT|1600/2|11.054.A|0001120123|SS|5|ALN|3.0.K|A2 Rosmalent: 11397$"
    )
    alert = parse_flex_line(good)
    assert alert is not None
    assert alert["message"] == "A2 Rosmalent: 11397"
    assert alert["capcodes"][0]["capcode"] == "1120123"
    assert alert["priority"] == "A2"
    assert alert["region_id"] == "6"
    junk = "FLEX_NEXT|1600/2|11.044.A|0001180000|SS|5|ALN|3.0.K|TECTPREQ MO@"
    assert parse_flex_line(junk) is None
    noise = (
        "FLEX_NEXT|1600/2|11.044.A|0001180000|SS|5|ALN|3.0.K|"
        "eytykadq4309qTttrovterdao`RGT4fm zon93t9c"
    )
    assert parse_flex_line(noise) is None


def test_detect_helpers() -> None:
    assert detect_service("Lifeliner 1 onderweg") == "lifeliner"
    assert detect_priority("PRIO 2 test") == "P2"


def test_build_alert_aliases() -> None:
    alert = build_alert("P2 test", [{"capcode": "1"}], "raw", "mock")
    assert alert["tekstmelding"] == alert["message"]
    assert alert["regioid"] == alert["region_id"]


if __name__ == "__main__":
    test_parse_text_flex()
    test_parse_json_flex()
    test_parse_flex_next_drops_garbage()
    test_detect_helpers()
    test_build_alert_aliases()
    print("ok")
