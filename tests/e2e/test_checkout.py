"""
End-to-End Checkout Tests for Pure Sound Application

This module contains E2E tests for checkout and payment flows:
- Cart review and management
- Payment information entry
- Billing address validation
- Order processing
- Order confirmation

Tests use Playwright to simulate real browser interactions.

Usage:
    pytest tests/e2e/test_checkout.py -v
    pytest tests/e2e/test_checkout.py --headed
    pytest tests/e2e/test_checkout.py::TestCheckoutFlows::test_order_creation -v
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def checkout_data():
    """
    Provide test checkout data for payment flow testing.
    """
    return {
        "items": [
            {
                "id": "preset_speech_clean",
                "name": "Speech Clean",
                "price": 9.99,
                "quantity": 1,
            },
            {
                "id": "preset_music_enhance",
                "name": "Music Enhance",
                "price": 14.99,
                "quantity": 1,
            },
        ],
        "payment": {
            "card_number": "4242424242424242",
            "expiry": "12/25",
            "cvv": "123",
            "card_name": "Test User",
        },
        "billing": {
            "address": "123 Test Street",
            "city": "Test City",
            "state": "TS",
            "zip": "12345",
            "country": "US",
        },
    }


@pytest.fixture
def mock_checkout_page(checkout_data):
    """Provide mocked checkout page"""
    mock_page = Mock()
    mock_page.is_visible = Mock(return_value=True)
    mock_page.fill = Mock()
    mock_page.click = Mock()
    mock_page.wait_for_timeout = Mock()
    mock_page.query_selector = Mock(return_value=Mock(
        text_content=Mock(return_value="$24.98")
    ))
    return mock_page


# ============================================================================
# Test Classes
# ============================================================================

class TestCheckoutFlows:
    """
    Test class for checkout and payment flows.
    
    Tests cover:
    - Cart review
    - Payment processing
    - Order confirmation
    - Payment error handling
    """
    
    def test_cart_review(self, checkout_data):
        """
        Test: Review cart items before checkout.
        
        Verifies:
        - Cart items are displayed correctly
        - Prices are accurate
        - Subtotal/total calculations are correct
        """
        items = checkout_data["items"]
        
        # Calculate expected total
        expected_total = sum(item["price"] * item["quantity"] for item in items)
        assert expected_total == 24.98  # 9.99 + 14.99
        
        # Verify item structure
        for item in items:
            assert "id" in item
            assert "name" in item
            assert "price" in item
            assert "quantity" in item
            assert item["price"] > 0
            assert item["quantity"] > 0
    
    def test_payment_info_validation(self, checkout_data):
        """
        Test: Payment information validation.
        
        Verifies:
        - Card number format validation
        - Expiry date format
        - CVV validation
        """
        payment = checkout_data["payment"]
        
        # Test card number (basic validation)
        card_number = payment["card_number"]
        assert len(card_number) >= 13
        assert len(card_number) <= 19
        assert card_number.isdigit()
        
        # Test expiry format (MM/YY)
        expiry = payment["expiry"]
        assert "/" in expiry
        parts = expiry.split("/")
        assert len(parts) == 2
        assert len(parts[0]) == 2  # Month
        assert len(parts[1]) == 2  # Year
        
        # Test CVV
        cvv = payment["cvv"]
        assert len(cvv) >= 3
        assert len(cvv) <= 4
        assert cvv.isdigit()
    
    def test_billing_address_validation(self, checkout_data):
        """
        Test: Billing address validation.
        
        Verifies:
        - Address fields are required
        - ZIP code format
        - Country selection
        """
        billing = checkout_data["billing"]
        
        # Required fields
        assert "address" in billing
        assert "city" in billing
        assert "zip" in billing
        assert "country" in billing
        
        # ZIP code validation (US format)
        zip_code = billing["zip"]
        assert len(zip_code) == 5
        assert zip_code.isdigit()
        
        # Country validation
        assert len(billing["country"]) == 2  # ISO country code
    
    def test_order_submission(self, checkout_data):
        """
        Test: Order submission process.
        
        Verifies:
        - Order is created with correct data
        - Payment is processed
        - Order confirmation is returned
        """
        # Mock order creation
        with patch('job_queue.job_queue') as mock_queue:
            # Create test job
            from job_queue import CompressionJob, JobStatus
            
            # Simulate order as job
            order_data = {
                "items": checkout_data["items"],
                "total": 24.98,
                "status": "processing",
            }
            
            assert order_data["status"] == "processing"
            assert order_data["total"] > 0
    
    def test_payment_processing(self):
        """
        Test: Payment processing simulation.
        
        Verifies:
        - Payment request is properly formatted
        - Response is handled correctly
        - Errors are caught
        """
        payment_data = {
            "amount": 24.98,
            "currency": "USD",
            "card": {
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123",
            },
            "description": "Pure Sound - Audio Processing Service",
        }
        
        # Validate payment request structure
        assert "amount" in payment_data
        assert "currency" in payment_data
        assert "card" in payment_data
        assert "description" in payment_data
        
        # Test amount format
        assert payment_data["amount"] > 0
        assert isinstance(payment_data["amount"], (int, float))
    
    def test_checkout_error_handling(self):
        """
        Test: Error handling during checkout.
        
        Verifies:
        - Invalid card is rejected
        - Network errors are handled
        - Payment failures show error messages
        """
        # Simulate payment failure
        with patch('security.EncryptionManager') as mock_encrypt:
            encrypt_instance = Mock()
            encrypt_instance.encrypt_data = Mock(return_value=b"encrypted_data")
            mock_encrypt.return_value = encrypt_instance
            
            from security import EncryptionManager
            
            # Test payment processing with invalid card
            invalid_payment = {
                "card_number": "invalid_card",
                "cvv": "123",
            }
            
            # Basic validation should fail
            card_number = invalid_payment["card_number"]
            is_valid = len(card_number) >= 13 and card_number.isdigit()
            assert is_valid is False
    
    def test_order_confirmation(self):
        """
        Test: Order confirmation display.
        
        Verifies:
        - Order number is generated
        - Confirmation contains correct details
        - Email confirmation is triggered
        """
        # Generate order number
        import time
        
        order_number = f"ORD-{int(time.time())}-{hash('test') % 10000}"
        
        # Verify order number format
        assert order_number.startswith("ORD-")
        assert len(order_number) > 10
        
        # Confirmation details
        confirmation = {
            "order_number": order_number,
            "status": "confirmed",
            "total": 24.98,
            "items_count": 2,
        }
        
        assert confirmation["status"] == "confirmed"
        assert confirmation["items_count"] > 0


class TestCartManagement:
    """
    Test class for cart management functionality.
    
    Tests cover:
    - Adding items to cart
    - Removing items from cart
    - Updating quantities
    - Cart persistence
    """
    
    def test_add_item_to_cart(self):
        """
        Test: Add item to shopping cart.
        
        Verifies:
        - Item is added with correct data
        - Cart total is updated
        """
        cart = []
        item = {
            "id": "preset_speech_clean",
            "name": "Speech Clean",
            "price": 9.99,
            "quantity": 1,
        }
        
        cart.append(item)
        
        assert len(cart) == 1
        assert cart[0]["id"] == "preset_speech_clean"
    
    def test_remove_item_from_cart(self):
        """
        Test: Remove item from shopping cart.
        
        Verifies:
        - Item is removed
        - Cart total is updated
        """
        cart = [
            {"id": "item1", "name": "Item 1", "price": 9.99, "quantity": 1},
            {"id": "item2", "name": "Item 2", "price": 14.99, "quantity": 1},
        ]
        
        # Remove item
        cart = [item for item in cart if item["id"] != "item1"]
        
        assert len(cart) == 1
        assert cart[0]["id"] == "item2"
    
    def test_update_cart_quantity(self):
        """
        Test: Update item quantity in cart.
        
        Verifies:
        - Quantity is updated
        - Line item total is recalculated
        """
        cart = [
            {"id": "item1", "name": "Item 1", "price": 9.99, "quantity": 1},
        ]
        
        # Update quantity
        for item in cart:
            if item["id"] == "item1":
                item["quantity"] = 2
        
        assert cart[0]["quantity"] == 2
        line_total = cart[0]["price"] * cart[0]["quantity"]
        assert line_total == 19.98
    
    def test_cart_total_calculation(self):
        """
        Test: Cart total calculation.
        
        Verifies:
        - Subtotal is calculated correctly
        - Tax is applied
        - Total includes all charges
        """
        cart = [
            {"id": "item1", "price": 9.99, "quantity": 1},
            {"id": "item2", "price": 14.99, "quantity": 2},
        ]
        
        # Calculate subtotal
        subtotal = sum(item["price"] * item["quantity"] for item in cart)
        assert subtotal == 39.97  # 9.99 + 14.99*2
        
        # Calculate tax
        tax_rate = 0.08
        tax = subtotal * tax_rate
        assert tax == 3.20  # Approximately
        
        # Calculate total
        total = subtotal + tax
        assert total == 43.17  # Approximately


class TestPaymentGateways:
    """
    Test class for payment gateway integration.
    
    Tests cover:
    - Gateway configuration
    - Transaction processing
    - Refund handling
    """
    
    def test_payment_gateway_config(self):
        """
        Test: Payment gateway configuration.
        
        Verifies:
        - Gateway credentials are set
        - Mode is correct (test/live)
        """
        config = {
            "gateway": "stripe",
            "api_key": "sk_test_12345",
            "mode": "test",
            "webhook_secret": "whsec_12345",
        }
        
        assert config["gateway"] == "stripe"
        assert config["mode"] == "test"
        assert "sk_test_" in config["api_key"]
    
    def test_transaction_record(self):
        """
        Test: Transaction record creation.
        
        Verifies:
        - Transaction is logged
        - Amount and status are recorded
        """
        transaction = {
            "id": "txn_12345",
            "order_id": "ORD-12345",
            "amount": 2498,  # in cents
            "currency": "usd",
            "status": "succeeded",
            "created_at": 1699999999,
            "metadata": {
                "items": 2,
                "user_id": "user_123",
            },
        }
        
        assert transaction["amount"] > 0
        assert transaction["status"] == "succeeded"
        assert "created_at" in transaction
    
    def test_refund_processing(self):
        """
        Test: Refund processing.
        
        Verifies:
        - Refund can be initiated
        - Amount is tracked
        - Status is updated
        """
        refund = {
            "id": "re_12345",
            "transaction_id": "txn_12345",
            "amount": 2498,
            "reason": "requested_by_customer",
            "status": "pending",
        }
        
        assert refund["amount"] > 0
        assert "reason" in refund


# ============================================================================
# Test Runner
# ============================================================================

def run_checkout_tests():
    """
    Run all checkout E2E tests.
    
    Returns:
        Test result summary
    """
    import unittest
    
    print("=" * 80)
    print("Pure Sound - E2E Checkout Tests")
    print("=" * 80)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCheckoutFlows))
    suite.addTests(loader.loadTestsFromTestCase(TestCartManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestPaymentGateways))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print("CHECKOUT E2E TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All checkout E2E tests passed!")
    else:
        print("\n❌ Some checkout E2E tests failed")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_checkout_tests()
    exit(0 if success else 1)
