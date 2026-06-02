"""
Unit tests for ETL/load.py

Run with:  pytest tests/test_etl_load.py -v

These tests use unittest.mock so no real database is needed.
Each loader function is tested with:
  - a normal happy-path case
  - an empty-list early-return case
"""

import uuid
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from ETL.load import (
    load_all,
    load_branches,
    load_payment_types,
    load_products,
    load_transaction_items,
    load_transactions,
)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def mock_cursor():
    return MagicMock()


@pytest.fixture
def mock_conn(mock_cursor):
    conn = MagicMock()
    conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return conn


def make_uuid():
    return str(uuid.uuid4())


# ============================================================
# load_branches
# ============================================================


class TestLoadBranches:
    def test_inserts_rows(self, mock_cursor):
        branches = [
            {"branch_id": make_uuid(), "branch_name": "Leeds"},
            {"branch_id": make_uuid(), "branch_name": "Manchester"},
        ]
        count = load_branches(branches, mock_cursor)

        assert count == 2
        assert mock_cursor.execute.called
        assert count == len(branches)

    def test_empty_list_returns_zero(self, mock_cursor):
        count = load_branches([], mock_cursor)

        assert count == 0
        mock_cursor.execute.assert_not_called()


# ============================================================
# load_payment_types
# ============================================================


class TestLoadPaymentTypes:
    def test_inserts_rows(self, mock_cursor):
        payment_types = [
            {"payment_method_id": make_uuid(), "payment_method": "CARD"},
            {"payment_method_id": make_uuid(), "payment_method": "CASH"},
        ]
        count = load_payment_types(payment_types, mock_cursor)

        assert count == 2

    def test_empty_list_returns_zero(self, mock_cursor):
        count = load_payment_types([], mock_cursor)

        assert count == 0


# ============================================================
# load_products
# ============================================================


class TestLoadProducts:
    def test_inserts_rows(self, mock_cursor):
        products = [
            {
                "product_id": make_uuid(),
                "product_name": "Large Latte",
                "current_price": Decimal("2.85"),
            },
            {
                "product_id": make_uuid(),
                "product_name": "Regular Flat White",
                "current_price": Decimal("2.45"),
            },
        ]
        count = load_products(products, mock_cursor)

        assert count == 2

    def test_empty_list_returns_zero(self, mock_cursor):
        assert load_products([], mock_cursor) == 0


# ============================================================
# load_transactions
# ============================================================


class TestLoadTransactions:
    def _make_transaction(self):
        return {
            "transaction_id": make_uuid(),
            "branch_id": make_uuid(),
            "payment_method_id": make_uuid(),
            "transaction_timestamp": datetime(2025, 3, 28, 9, 0, 0),
            "transaction_total": Decimal("5.30"),
        }

    def test_inserts_rows(self, mock_cursor):
        txns = [self._make_transaction() for _ in range(5)]
        count = load_transactions(txns, mock_cursor)

        assert count == 5

    def test_empty_list_returns_zero(self, mock_cursor):
        assert load_transactions([], mock_cursor) == 0

    def test_batching_splits_correctly(self, mock_cursor):
        txns = [self._make_transaction() for _ in range(15)]

        with patch("ETL.load.extras.execute_values") as mock_ev:
            count = load_transactions(txns, mock_cursor, batch_size=5)

        assert count == 15
        assert mock_ev.call_count == 3


# ============================================================
# load_transaction_items
# ============================================================


class TestLoadTransactionItems:
    def _make_item(self):
        return {
            "transaction_item_id": make_uuid(),
            "transaction_id": make_uuid(),
            "product_id": make_uuid(),
            "quantity": 1,
            "unit_price": Decimal("2.85"),
        }

    def test_inserts_rows(self, mock_cursor):
        items = [self._make_item() for _ in range(4)]
        count = load_transaction_items(items, mock_cursor)

        assert count == 4

    def test_empty_list_returns_zero(self, mock_cursor):
        assert load_transaction_items([], mock_cursor) == 0

    def test_batching_splits_correctly(self, mock_cursor):
        items = [self._make_item() for _ in range(22)]

        with patch("ETL.load.extras.execute_values") as mock_ev:
            count = load_transaction_items(items, mock_cursor, batch_size=10)

        assert count == 22
        assert mock_ev.call_count == 3


# ============================================================
# load_all
# ============================================================


class TestLoadAll:
    def _make_transformed_data(self):
        branch_id = make_uuid()
        payment_id = make_uuid()
        product_id = make_uuid()
        txn_id = make_uuid()

        return {
            "branches": [{"branch_id": branch_id, "branch_name": "Leeds"}],
            "payment_types": [{"payment_method_id": payment_id, "payment_method": "CARD"}],
            "products": [
                {
                    "product_id": product_id,
                    "product_name": "Large Latte",
                    "current_price": Decimal("2.85"),
                }
            ],
            "transactions": [
                {
                    "transaction_id": txn_id,
                    "branch_id": branch_id,
                    "payment_method_id": payment_id,
                    "transaction_timestamp": datetime(2025, 3, 28, 9, 0, 0),
                    "transaction_total": Decimal("2.85"),
                }
            ],
            "transaction_items": [
                {
                    "transaction_item_id": make_uuid(),
                    "transaction_id": txn_id,
                    "product_id": product_id,
                    "quantity": 1,
                    "unit_price": Decimal("2.85"),
                }
            ],
        }

    def test_commits_on_success(self, mock_conn):
        data = self._make_transformed_data()

        with patch("ETL.load.extras.execute_values"):
            counts = load_all(data, mock_conn)

        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()

        assert counts["branches"] == 1
        assert counts["payment_types"] == 1
        assert counts["products"] == 1
        assert counts["transactions"] == 1
        assert counts["transaction_items"] == 1

    def test_rolls_back_on_failure(self, mock_conn):
        data = self._make_transformed_data()

        with patch("ETL.load.extras.execute_values", side_effect=Exception("DB error")):
            with pytest.raises(Exception, match="DB error"):
                load_all(data, mock_conn)

        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()

    def test_handles_missing_keys_gracefully(self, mock_conn):
        with patch("ETL.load.extras.execute_values"):
            counts = load_all({}, mock_conn)

        assert counts["branches"] == 0
        assert counts["transaction_items"] == 0
        mock_conn.commit.assert_called_once()
