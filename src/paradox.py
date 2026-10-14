"""The inspection paradox: the same quantity averaged in two ways.

The plain average gives every item the same weight: every gap between buses, every person.
The size-weighted average gives every item a weight equal to its own size: a gap counts once
per minute it lasts, a person counts once per friend. It answers the question "I pick a minute
(or a friendship) at random, how large is the gap (or the person) I land on?".
"""
from __future__ import annotations

import numpy as np


def plain_mean(sizes) -> float:
    """Mean size, every item counted once."""
    return float(np.mean(sizes))


def weighted_mean(sizes) -> float:
    """Mean size when every item is counted in proportion to its size."""
    sizes = np.asarray(sizes, dtype=float)
    return float((sizes ** 2).sum() / sizes.sum())


def weighted_mean_from_formula(sizes) -> float:
    """The same quantity from the identity E[X*] = E[X] + Var(X) / E[X]."""
    sizes = np.asarray(sizes, dtype=float)
    return float(sizes.mean() + sizes.var() / sizes.mean())


def plain_median(sizes) -> float:
    """Median size, every item counted once."""
    return float(np.median(sizes))


def weighted_median(sizes) -> float:
    """Median size when every item is counted in proportion to its size."""
    ordered = np.sort(np.asarray(sizes, dtype=float))
    share = np.cumsum(ordered) / ordered.sum()
    return float(ordered[np.searchsorted(share, 0.5)])


def friend_counts(links: np.ndarray) -> np.ndarray:
    """Number of friends of each person, indexed by the person's id."""
    return np.bincount(links.ravel()).astype(float)


def mean_friends_of_friends(links: np.ndarray) -> np.ndarray:
    """For each person, the average number of friends that their own friends have.

    People with no friends get nan.
    """
    counts = friend_counts(links)
    total = np.zeros_like(counts)
    np.add.at(total, links[:, 0], counts[links[:, 1]])
    np.add.at(total, links[:, 1], counts[links[:, 0]])
    return np.divide(total, counts, out=np.full_like(counts, np.nan), where=counts > 0)


def summarise_network(links: np.ndarray) -> dict[str, float]:
    """People, links, and the number of friends of a person and of a friend."""
    counts = friend_counts(links)
    of_friends = mean_friends_of_friends(links)
    connected = counts > 0
    counts, of_friends = counts[connected], of_friends[connected]
    return {
        "people": int(connected.sum()),
        "links": len(links),
        "mean_friends_of_a_person": plain_mean(counts),
        "mean_friends_of_a_friend": weighted_mean(counts),
        "median_friends_of_a_person": plain_median(counts),
        "median_friends_of_a_friend": weighted_median(counts),
        "most_friends": float(counts.max()),
        "share_with_fewer_friends_than_their_friends": float((counts < of_friends).mean()),
    }
