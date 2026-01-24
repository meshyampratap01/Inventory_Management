import unittest
from unittest.mock import MagicMock, patch

from app.services.product_service import ProductService
from app.app_exception.app_exception import AppException
from app.dto.create_product_request import CreateProductRequest
from app.dto.stock_update_request import StockUpdateRequest
from app.models.products import Product


class TestProductService(unittest.TestCase):
    def setUp(self):
        self.mock_product_repo = MagicMock()
        self.mock_category_repo = MagicMock()
        self.mock_cognito_client = MagicMock()

        cognito_config = (self.mock_cognito_client, "ap-south-1", "pool-id")

        self.service = ProductService(
            cognito_config=cognito_config,
            product_repo=self.mock_product_repo,
            category_repo=self.mock_category_repo,
        )

    def test_create_product_success(self):
        self.mock_category_repo.get_category.return_value = MagicMock()

        req = CreateProductRequest(
            name="Laptop",
            price=50000,
            quantity=10,
            category="ELECTRONICS",
            override_threshold=None,
        )

        product = self.service.create_product(req)

        self.assertIsInstance(product, Product)
        self.assertEqual(product.name, "Laptop")
        self.assertFalse(product.low_stock_alert_sent)

        self.mock_product_repo.save_product.assert_called_once()

    def test_get_all_products(self):
        self.mock_product_repo.get_all_products.return_value = ["p1", "p2"]

        result = self.service.get_all_products()

        self.assertEqual(result, ["p1", "p2"])
        self.mock_product_repo.get_all_products.assert_called_once()

    def test_get_product_by_id(self):
        self.mock_product_repo.get_product_by_id.return_value = "product"

        result = self.service.get_product_by_id("pid")

        self.assertEqual(result, "product")
        self.mock_product_repo.get_product_by_id.assert_called_once_with("pid")

    def test_stock_in_resets_low_stock_alert(self):
        product = Product(
            id="p1",
            name="Item",
            price=100,
            quantity=20,
            category="CAT",
            override_threshold=None,
            low_stock_alert_sent=True,
        )

        category = MagicMock(default_threshold=10)

        self.mock_product_repo.get_product_by_id.return_value = product
        self.mock_category_repo.get_category.return_value = category

        req = StockUpdateRequest(product_id="p1", quantity=5)

        self.service.stock_in(req)

        self.mock_product_repo.stock_in.assert_called_once_with("p1", 5)
        self.mock_product_repo.update_low_stock_alert_sent.assert_called_once_with(
            "p1", False
        )

    def test_stock_out_insufficient_stock(self):
        product = Product(
            id="p1",
            name="Item",
            price=100,
            quantity=5,
            category="CAT",
            override_threshold=None,
            low_stock_alert_sent=False,
        )

        self.mock_product_repo.get_product_by_id.return_value = product
        self.mock_category_repo.get_category.return_value = MagicMock(
            default_threshold=2
        )

        req = StockUpdateRequest(product_id="p1", quantity=10)

        with self.assertRaises(AppException) as ctx:
            self.service.stock_out(req)

        exc = ctx.exception
        self.assertEqual(exc.status_code, 400)
        self.assertEqual(exc.error_code, "INSUFFICIENT_STOCK")

    def test_stock_out_no_alert(self):
        product = Product(
            id="p1",
            name="Item",
            price=100,
            quantity=20,
            category="CAT",
            override_threshold=None,
            low_stock_alert_sent=False,
        )

        updated_product = Product(
            id="p1",
            name="Item",
            price=100,
            quantity=15,
            category="CAT",
            override_threshold=None,
            low_stock_alert_sent=False,
        )

        self.mock_product_repo.get_product_by_id.side_effect = [
            product,
            updated_product,
        ]
        self.mock_category_repo.get_category.return_value = MagicMock(
            default_threshold=5
        )

        req = StockUpdateRequest(product_id="p1", quantity=5)

        self.service.stock_out(req)

        self.mock_product_repo.stock_out.assert_called_once_with("p1", 5)

    @patch("app.services.product_service.SNSEventPublisher")
    def test_stock_out_triggers_low_stock_alert(self, mock_sns_cls):
        product = Product(
            id="p1",
            name="Item",
            price=100,
            quantity=6,
            category="CAT",
            override_threshold=None,
            low_stock_alert_sent=False,
        )

        updated_product = Product(
            id="p1",
            name="Item",
            price=100,
            quantity=3,
            category="CAT",
            override_threshold=None,
            low_stock_alert_sent=False,
        )

        self.mock_product_repo.get_product_by_id.side_effect = [
            product,
            updated_product,
        ]

        self.mock_category_repo.get_category.return_value = MagicMock(
            default_threshold=5
        )

        self.mock_cognito_client.list_users_in_group.return_value = {
            "Users": [{"Attributes": [{"Name": "email", "Value": "manager@test.com"}]}]
        }

        req = StockUpdateRequest(product_id="p1", quantity=3)

        self.service.stock_out(req)

        mock_sns_cls.return_value.publish_event.assert_called_once()
        self.mock_product_repo.update_low_stock_alert_sent.assert_called_once_with(
            "p1", True
        )
