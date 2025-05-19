import unittest
from datetime import datetime, timedelta
from src.shared.utils import (
    format_timestamp,
    validate_email,
    sanitize_text,
    calculate_time_difference,
    generate_unique_id
)

class TestSharedUtils(unittest.TestCase):
    def test_format_timestamp(self):
        """Test timestamp formatting functionality"""
        # Test current timestamp
        now = datetime.now()
        formatted = format_timestamp(now)
        self.assertIsInstance(formatted, str)
        self.assertTrue(len(formatted) > 0)
        
        # Test specific timestamp
        specific_time = datetime(2024, 3, 20, 14, 30, 0)
        formatted = format_timestamp(specific_time)
        self.assertIn("2024", formatted)
        self.assertIn("14:30", formatted)

    def test_validate_email(self):
        """Test email validation functionality"""
        # Valid email addresses
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.com"
        ]
        for email in valid_emails:
            self.assertTrue(validate_email(email))
        
        # Invalid email addresses
        invalid_emails = [
            "invalid.email",
            "@domain.com",
            "user@",
            "user@.com",
            ""
        ]
        for email in invalid_emails:
            self.assertFalse(validate_email(email))

    def test_sanitize_text(self):
        """Test text sanitization functionality"""
        # Test basic sanitization
        input_text = "<script>alert('test')</script>Hello World!"
        sanitized = sanitize_text(input_text)
        self.assertNotIn("<script>", sanitized)
        self.assertIn("Hello World!", sanitized)
        
        # Test with special characters
        input_text = "Test & Special < Characters >"
        sanitized = sanitize_text(input_text)
        self.assertIn("Test & Special", sanitized)
        self.assertNotIn("< Characters >", sanitized)

    def test_calculate_time_difference(self):
        """Test time difference calculation"""
        # Test future time
        now = datetime.now()
        future = now + timedelta(hours=2)
        diff = calculate_time_difference(now, future)
        self.assertEqual(diff.total_seconds(), 7200)  # 2 hours in seconds
        
        # Test past time
        past = now - timedelta(days=1)
        diff = calculate_time_difference(now, past)
        self.assertEqual(diff.total_seconds(), -86400)  # -1 day in seconds

    def test_generate_unique_id(self):
        """Test unique ID generation"""
        # Generate multiple IDs and check uniqueness
        ids = set()
        for _ in range(100):
            new_id = generate_unique_id()
            self.assertNotIn(new_id, ids)
            ids.add(new_id)
        
        # Check ID format
        sample_id = generate_unique_id()
        self.assertIsInstance(sample_id, str)
        self.assertTrue(len(sample_id) > 0)

    def test_edge_cases(self):
        """Test edge cases for utility functions"""
        # Test None inputs
        self.assertRaises(ValueError, format_timestamp, None)
        self.assertRaises(ValueError, validate_email, None)
        self.assertRaises(ValueError, sanitize_text, None)
        self.assertRaises(ValueError, calculate_time_difference, None, datetime.now())
        
        # Test empty string inputs
        self.assertFalse(validate_email(""))
        self.assertEqual(sanitize_text(""), "")

if __name__ == '__main__':
    unittest.main() 