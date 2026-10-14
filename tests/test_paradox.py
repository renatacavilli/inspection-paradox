import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import paradox  # noqa: E402

# A star: person 0 is friends with 1, 2, 3 and 4, who have no other friends.
STAR = np.array([[0, 1], [0, 2], [0, 3], [0, 4]])


def test_bus_example():
    gaps = [5, 15]
    assert paradox.plain_mean(gaps) == 10
    assert paradox.weighted_mean(gaps) == 12.5
    assert paradox.weighted_mean_from_formula(gaps) == 12.5


def test_equal_sizes_show_no_paradox():
    assert paradox.weighted_mean([10, 10, 10]) == paradox.plain_mean([10, 10, 10])


def test_formula_matches_direct_calculation():
    sizes = np.random.default_rng(7).pareto(1.5, 1_000) + 1
    assert paradox.weighted_mean(sizes) == pytest.approx(paradox.weighted_mean_from_formula(sizes))


def test_weighted_mean_is_never_below_plain_mean():
    sizes = np.random.default_rng(7).integers(1, 500, 200)
    assert paradox.weighted_mean(sizes) >= paradox.plain_mean(sizes)


def test_medians():
    sizes = [1, 1, 1, 1, 6]            # the large item holds 6 of the 10 units
    assert paradox.plain_median(sizes) == 1
    assert paradox.weighted_median(sizes) == 6


def test_friend_counts_in_a_star():
    assert paradox.friend_counts(STAR).tolist() == [4, 1, 1, 1, 1]


def test_friends_of_friends_in_a_star():
    assert paradox.mean_friends_of_friends(STAR).tolist() == [1, 4, 4, 4, 4]


def test_star_summary():
    summary = paradox.summarise_network(STAR)
    assert summary["people"] == 5
    assert summary["mean_friends_of_a_person"] == 1.6
    assert summary["mean_friends_of_a_friend"] == 2.5          # (4 * 4 + 4 * 1) / 8
    assert summary["share_with_fewer_friends_than_their_friends"] == 0.8


def test_everyone_equal_in_a_triangle():
    summary = paradox.summarise_network(np.array([[0, 1], [1, 2], [0, 2]]))
    assert summary["mean_friends_of_a_person"] == summary["mean_friends_of_a_friend"] == 2
    assert summary["share_with_fewer_friends_than_their_friends"] == 0
