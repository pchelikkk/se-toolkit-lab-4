"""Edge case and boundary value tests for interaction endpoints and models."""

import pytest
from app.models.interaction import InteractionLog, InteractionLogCreate


def _make_log(id: int, learner_id: int, item_id: int, kind: str = "attempt") -> InteractionLog:
    """Helper to create InteractionLog instances for testing."""
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind=kind)


class TestFilterByItemIdEdgeCases:
    """Edge case tests for the _filter_by_item_id function."""

    def test_filter_returns_empty_when_item_id_not_found(self):
        """Filtering by a non-existent item_id should return an empty list."""
        from app.routers.interactions import _filter_by_item_id

        interactions = [
            _make_log(1, 1, 1),
            _make_log(2, 1, 2),
            _make_log(3, 1, 3),
        ]

        result = _filter_by_item_id(interactions, item_id=999)

        assert result == []

    def test_filter_returns_multiple_matches_for_same_item_id(self):
        """Filtering should return all interactions matching the item_id, not just the first."""
        from app.routers.interactions import _filter_by_item_id

        interactions = [
            _make_log(1, 1, 1, kind="view"),
            _make_log(2, 1, 1, kind="attempt"),
            _make_log(3, 1, 1, kind="complete"),
            _make_log(4, 2, 2, kind="view"),
        ]

        result = _filter_by_item_id(interactions, item_id=1)

        assert len(result) == 3
        assert all(i.item_id == 1 for i in result)
        assert set(i.id for i in result) == {1, 2, 3}

    def test_filter_with_zero_as_item_id(self):
        """Filtering by item_id=0 should work correctly (zero is a valid integer filter)."""
        from app.routers.interactions import _filter_by_item_id

        interactions = [
            _make_log(1, 1, 0),
            _make_log(2, 1, 1),
            _make_log(3, 1, 0),
        ]

        result = _filter_by_item_id(interactions, item_id=0)

        assert len(result) == 2
        assert all(i.item_id == 0 for i in result)
        assert set(i.id for i in result) == {1, 3}
    def test_filter_preserves_order_when_filtering(self):
        """Filtering should preserve the original order of interactions."""
        from app.routers.interactions import _filter_by_item_id

        interactions = [
            _make_log(1, 1, 2),
            _make_log(2, 1, 1),
            _make_log(3, 1, 2),
            _make_log(4, 1, 1),
            _make_log(5, 1, 3),
        ]

        result = _filter_by_item_id(interactions, item_id=1)

        assert len(result) == 2
        assert result[0].id == 2
        assert result[1].id == 4

    def test_filter_with_negative_item_id(self):
        """Filtering by negative item_id should work (edge case for integer boundaries)."""
        from app.routers.interactions import _filter_by_item_id

        interactions = [
            _make_log(1, 1, -1),
            _make_log(2, 1, 1),
            _make_log(3, 1, -1),
        ]

        result = _filter_by_item_id(interactions, item_id=-1)

        assert len(result) == 2
        assert all(i.item_id == -1 for i in result)


class TestInteractionLogCreateValidation:
    """Boundary value tests for InteractionLogCreate model validation."""

    def test_interaction_log_create_with_empty_kind_is_allowed(self):
        """Creating an InteractionLogCreate with empty kind is allowed by Pydantic (edge case)."""
        log = InteractionLogCreate(learner_id=1, item_id=1, kind="")
        assert log.kind == ""

    def test_interaction_log_create_with_whitespace_kind_is_allowed(self):
        """Creating an InteractionLogCreate with whitespace-only kind is allowed by Pydantic (edge case)."""
        log = InteractionLogCreate(learner_id=1, item_id=1, kind="   ")
        assert log.kind == "   "

    def test_interaction_log_create_with_zero_learner_id(self):
        """Creating an InteractionLogCreate with learner_id=0 should be allowed (boundary value)."""
        log = InteractionLogCreate(learner_id=0, item_id=1, kind="attempt")
        assert log.learner_id == 0
        assert log.item_id == 1
        assert log.kind == "attempt"

    def test_interaction_log_create_with_zero_item_id(self):
        """Creating an InteractionLogCreate with item_id=0 should be allowed (boundary value)."""
        log = InteractionLogCreate(learner_id=1, item_id=0, kind="attempt")
        assert log.learner_id == 1
        assert log.item_id == 0
        assert log.kind == "attempt"

    def test_interaction_log_create_with_negative_ids(self):
        """Creating an InteractionLogCreate with negative IDs should be allowed by model validation."""
        log = InteractionLogCreate(learner_id=-1, item_id=-1, kind="attempt")
        assert log.learner_id == -1
        assert log.item_id == -1

    def test_interaction_log_create_with_very_long_kind(self):
        """Creating an InteractionLogCreate with a very long kind string should be allowed."""
        long_kind = "a" * 1000
        log = InteractionLogCreate(learner_id=1, item_id=1, kind=long_kind)
        assert log.kind == long_kind
        assert len(log.kind) == 1000

    def test_interaction_log_create_with_special_characters_in_kind(self):
        """Creating an InteractionLogCreate with special characters in kind should be allowed."""
        log = InteractionLogCreate(learner_id=1, item_id=1, kind="view/attempt@2024!#$%")
        assert log.kind == "view/attempt@2024!#$%"

    def test_interaction_log_create_with_unicode_kind(self):
        """Creating an InteractionLogCreate with unicode characters in kind should be allowed."""
        log = InteractionLogCreate(learner_id=1, item_id=1, kind="表示・試行")
        assert log.kind == "表示・試行"
