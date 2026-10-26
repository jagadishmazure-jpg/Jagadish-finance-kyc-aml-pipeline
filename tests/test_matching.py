import pytest

from kyc_aml.matching import (name_variants, normalize_name, screen_name,
                              similarity)


def test_normalize_strips_diacritics_and_punctuation():
    assert normalize_name("José  Müller!") == "jose muller"


def test_transliteration_variant_covers_spelling_family():
    variants = name_variants("Mohamed Alar")
    assert "mohammed alar" in variants
    assert "muhammad alar" in variants


def test_variant_match_scores_high():
    assert similarity("Mohammed Alar", "Mohamed Alar") > 0.95


def test_exact_name_scores_one():
    assert similarity("Alaric Voss", "Alaric Voss") == 1.0


def test_unrelated_name_scores_low():
    assert similarity("Elena Marsh", "Alaric Voss") < 0.5


def test_screen_returns_hits_best_first():
    hits = screen_name("Alaric Voss", [{"name": "Alaric Voss"},
                                       {"name": "Alaric Vossel"}],
                       "synthetic-sanctions")
    assert hits[0]["matched_name"] == "Alaric Voss"
    assert hits[0]["score"] == 1.0


def test_screen_below_threshold_returns_no_hits():
    assert screen_name("Elena Marsh", [{"name": "Alaric Voss"}],
                       "synthetic-sanctions") == []


def test_screen_threshold_boundary_is_inclusive():
    hits = screen_name("Alaric Voss", [{"name": "Alaric Voss"}],
                       "synthetic-sanctions", threshold=1.0)
    assert len(hits) == 1
