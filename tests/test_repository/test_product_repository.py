import unittest
from unittest.mock import MagicMock
from decimal import Decimal
from botocore.exceptions import ClientError

from app.repository.product_repository import ProductRepository
from app.models.products import Product
from app.app_exception.app_exception import AppException


def ddb_tx_error(code: str):
    return ClientError(
        error_response={"Error": {"Code": code, "Message": "error"}},
        operation_name="TransactWriteItems",
    )


class TestProductRepository(unittest.TestCase):
    def setUp(self):
        self.mock_table = MagicMock()
        self.mock_ddb_client = MagicMock()

        self.mock_table.meta.client = self.mock_ddb_client
        self.mock_table.name = "test-table"

        self.repo = ProductRepository(table=self.mock_table)

    def test_save_product_success(self):
        product = Product(
            id="p1",
            name="Laptop",
            price=50000,
            quantity=10,
            category="ELECTRONICS",
            override_threshold=None,
            low_stock_alert_sent=False,
        )

        self.repo.save_product(product)

        self.mock_ddb_client.transact_write_items.assert_called_once()

    def test_save_product_already_exists(self):
        self.mock_ddb_client.transact_write_items.side_effect = ddb_tx_error(
            "TransactionCanceledException"
        )

        product = Product(
            id="p1",
            name="Laptop",
            price=50000,
            quantity=10,
            category="ELECTRONICS",
            override_threshold=None,
            low_stock_alert_sent=False,
        )

        with self.assertRaises(AppException) as ctx:
            self.repo.save_product(product)

        exc = ctx.exception
        self.assertEqual(exc.status_code, 409)
        self.assertEqual(exc.error_code, "PRODUCT_ALREADY_EXISTS")

    def test_save_product_generic_failure(self):
        self.mock_ddb_client.transact_write_items.side_effect = ddb_tx_error(
            "InternalServerError"
        )

        product = Product(
            id="p1",
            name="Laptop",
            price=50000,
            quantity=10,
            category="ELECTRONICS",
            override_threshold=None,
            low_stock_alert_sent=False,
        )

        with self.assertRaises(AppException) as ctx:
            self.repo.save_product(product)

        self.assertEqual(ctx.exception.status_code, 500)

    def test_get_all_products_success(self):
        self.mock_table.query.return_value = {
            "Items": [
                {
                    "id": "p1",
                    "name": "Item1",
                    "price": Decimal("10"),
                    "quantity": 5,
                    "category": "CAT",
                },
                {
                    "id": "p2",
                    "name": "Item2",
                    "price": Decimal("20"),
                    "quantity": 10,
                    "category": "CAT",
                },
            ]
        }

        products = self.repo.get_all_products()

        self.assertEqual(len(products), 2)
        self.assertIsInstance(products[0], Product)
        self.assertEqual(products[1].id, "p2")

    def test_stock_in_success(self):
        self.repo.stock_in("p1", 5)

        self.mock_ddb_client.transact_write_items.assert_called_once()

    def test_stock_in_failure(self):
        self.mock_ddb_client.transact_write_items.side_effect = ddb_tx_error(
            "InternalServerError"
        )

        with self.assertRaises(AppException) as ctx:
            self.repo.stock_in("p1", 5)

        self.assertEqual(ctx.exception.error_code, "STOCK_IN_FAILED")

    def test_stock_out_success(self):
        self.repo.stock_out("p1", 2)

        self.mock_ddb_client.transact_write_items.assert_called_once()

    def test_stock_out_insufficient_stock(self):
        self.mock_ddb_client.transact_write_items.side_effect = ddb_tx_error(
            "TransactionCanceledException"
        )

        with self.assertRaises(AppException) as ctx:
            self.repo.stock_out("p1", 5)

        exc = ctx.exception
        self.assertEqual(exc.status_code, 400)
        self.assertEqual(exc.error_code, "INSUFFICIENT_STOCK")

    def test_stock_out_failure(self):
        self.mock_ddb_client.transact_write_items.side_effect = ddb_tx_error(
            "InternalServerError"
        )

        with self.assertRaises(AppException) as ctx:
            self.repo.stock_out("p1", 5)

        self.assertEqual(ctx.exception.error_code, "STOCK_OUT_FAILED")

    def test_update_low_stock_alert_success(self):
        self.repo.update_low_stock_alert_sent("p1", True)

        self.mock_ddb_client.transact_write_items.assert_called_once()

    def test_update_low_stock_alert_not_found(self):
        self.mock_ddb_client.transact_write_items.side_effect = ddb_tx_error(
            "TransactionCanceledException"
        )

        with self.assertRaises(AppException) as ctx:
            self.repo.update_low_stock_alert_sent("p1", True)

        exc = ctx.exception
        self.assertEqual(exc.status_code, 404)
        self.assertEqual(exc.error_code, "PRODUCT_NOT_FOUND")

    def test_update_low_stock_alert_failure(self):
        self.mock_ddb_client.transact_write_items.side_effect = ddb_tx_error(
            "InternalServerError"
        )

        with self.assertRaises(AppException) as ctx:
            self.repo.update_low_stock_alert_sent("p1", True)

        self.assertEqual(ctx.exception.error_code, "DATABASE_ERROR")

    def test_delete_product_success(self):
        self.repo.delete_product("p1")

        self.mock_ddb_client.transact_write_items.assert_called_once()

    def test_delete_product_not_found(self):
        self.mock_ddb_client.transact_write_items.side_effect = ddb_tx_error(
            "TransactionCanceledException"
        )

        with self.assertRaises(AppException) as ctx:
            self.repo.delete_product("p1")

        exc = ctx.exception
        self.assertEqual(exc.status_code, 404)
        self.assertEqual(exc.error_code, "PRODUCT_NOT_FOUND")
