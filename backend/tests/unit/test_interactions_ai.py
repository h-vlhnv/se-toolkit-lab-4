"""Unit tests for interaction filtering logic - edge cases and boundary values."""

from app.models.interaction import InteractionLog
from app.routers.interactions import filter_by_max_item_id


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    """Helper to create an InteractionLog for testing."""
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


# KEPT: covers the case where all interactions are filtered out, returning empty list
def test_filter_all_interactions_above_max_returns_empty() -> None:
    """When all item_ids are greater than max_item_id, return empty list."""
    interactions = [_make_log(1, 1, 5), _make_log(2, 2, 10), _make_log(3, 3, 15)]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=3)
    assert result == []


# KEPT: tests the zero boundary case which is important for edge case coverage
def test_filter_zero_item_id_with_zero_max() -> None:
    """Test filtering when item_id is 0 and max_item_id is 0 (boundary)."""
    interactions = [_make_log(1, 1, 0)]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=0)
    assert len(result) == 1
    assert result[0].item_id == 0


# KEPT: tests zero item_id with positive max, different from existing tests
def test_filter_zero_item_id_with_positive_max() -> None:
    """Test filtering when item_id is 0 and max_item_id is positive."""
    interactions = [_make_log(1, 1, 0), _make_log(2, 2, 5)]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=3)
    assert len(result) == 1
    assert result[0].item_id == 0


# KEPT: covers negative item_ids edge case not tested elsewhere
def test_filter_negative_item_id_included_with_positive_max() -> None:
    """Negative item_ids should be included when max_item_id is positive."""
    interactions = [_make_log(1, 1, -5), _make_log(2, 2, 3)]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=10)
    assert len(result) == 2
    assert result[0].item_id == -5
    assert result[1].item_id == 3


# KEPT: tests negative max_item_id which is an important edge case
def test_filter_negative_max_item_id_excludes_positive_ids() -> None:
    """When max_item_id is negative, positive item_ids should be excluded."""
    interactions = [_make_log(1, 1, -3), _make_log(2, 2, 5), _make_log(3, 3, 10)]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=-1)
    assert len(result) == 1
    assert result[0].item_id == -3


# KEPT: tests multiple items at exact boundary, not covered by existing tests
def test_filter_multiple_interactions_at_same_boundary() -> None:
    """Multiple interactions with item_id equal to max_item_id should all be included."""
    interactions = [
        _make_log(1, 1, 5),
        _make_log(2, 2, 5),
        _make_log(3, 3, 5),
        _make_log(4, 4, 6),
    ]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=5)
    assert len(result) == 3
    assert all(i.item_id == 5 for i in result)


# KEPT: tests duplicate item_ids across boundary, good coverage
def test_filter_duplicate_item_ids_mixed_values() -> None:
    """Test filtering with duplicate item_ids across the boundary."""
    interactions = [
        _make_log(1, 1, 3),
        _make_log(2, 2, 3),
        _make_log(3, 3, 4),
        _make_log(4, 4, 4),
        _make_log(5, 5, 5),
    ]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=4)
    assert len(result) == 4
    assert all(i.item_id <= 4 for i in result)


# DISCARDED: duplicates test_filter_returns_interactions_below_max logic with different values
# def test_filter_single_interaction_above_max() -> None:
#     """Single interaction with item_id above max_item_id should be filtered out."""
#     interactions = [_make_log(1, 1, 100)]
#     result = filter_by_max_item_id(interactions=interactions, max_item_id=50)
#     assert result == []


# DISCARDED: duplicates test_filter_returns_interactions_below_max logic with different values
# def test_filter_single_interaction_below_max() -> None:
#     """Single interaction with item_id below max_item_id should be included."""
#     interactions = [_make_log(1, 1, 10)]
#     result = filter_by_max_item_id(interactions=interactions, max_item_id=50)
#     assert len(result) == 1
#     assert result[0].item_id == 10


# KEPT: stress test with large integer values, important for robustness
def test_filter_very_large_item_id_values() -> None:
    """Test filtering with very large item_id values (boundary stress test)."""
    large_id = 2**31 - 1  # Max 32-bit signed integer
    interactions = [
        _make_log(1, 1, large_id - 1),
        _make_log(2, 2, large_id),
        _make_log(3, 3, large_id + 1),
    ]
    result = filter_by_max_item_id(interactions=interactions, max_item_id=large_id)
    assert len(result) == 2
    assert result[0].item_id == large_id - 1
    assert result[1].item_id == large_id
