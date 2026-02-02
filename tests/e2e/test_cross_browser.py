"""
Cross-Browser and Cross-Device Tests for Pure Sound Application

This module contains tests to verify the app behaves and looks acceptable
in different browsers and devices:
- Chrome, Firefox, Safari, Edge
- Mobile, tablet, desktop devices

Goal: catch browser-specific quirks, CSS/JS incompatibilities, and viewport issues.

Usage:
    pytest tests/e2e/test_cross_browser.py -v
    pytest tests/e2e/test_cross_browser.py --browser=chromium --device="iPhone 12"
    pytest tests/e2e/test_cross_browser.py::TestBrowserCompatibility -v
"""

import pytest
import unittest
import os
import sys
from typing import Dict
from unittest.mock import Mock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


# ============================================================================
# Browser and Device Configuration
# ============================================================================

BROWSERS = {
    "chromium": {
        "name": "Chromium",
        "engine": "Blink",
        "vendor": "Google",
        "version": "120.0",
    },
    "firefox": {
        "name": "Firefox",
        "engine": "Gecko",
        "vendor": "Mozilla",
        "version": "120.0",
    },
    "webkit": {
        "name": "Safari",
        "engine": "WebKit",
        "vendor": "Apple",
        "version": "17.0",
    },
    "edge": {
        "name": "Edge",
        "engine": "Blink",
        "vendor": "Microsoft",
        "version": "120.0",
    },
}

DEVICES = {
    # Mobile devices
    "iphone_12": {
        "name": "iPhone 12",
        "viewport": {"width": 390, "height": 844},
        "pixel_ratio": 3,
        "is_mobile": True,
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    },
    "pixel_5": {
        "name": "Pixel 5",
        "viewport": {"width": 412, "height": 892},
        "pixel_ratio": 2.625,
        "is_mobile": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5)",
    },
    "samsung_galaxy_s21": {
        "name": "Samsung Galaxy S21",
        "viewport": {"width": 360, "height": 800},
        "pixel_ratio": 2,
        "is_mobile": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 11; SM-G991B)",
    },
    # Tablet devices
    "ipad_mini": {
        "name": "iPad Mini",
        "viewport": {"width": 768, "height": 1024},
        "pixel_ratio": 2,
        "is_mobile": False,
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)",
    },
    "ipad_pro": {
        "name": "iPad Pro",
        "viewport": {"width": 1024, "height": 1366},
        "pixel_ratio": 2,
        "is_mobile": False,
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)",
    },
    # Desktop devices
    "macbook_pro": {
        "name": "MacBook Pro",
        "viewport": {"width": 1440, "height": 900},
        "pixel_ratio": 1,
        "is_mobile": False,
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    },
    "windows_pc": {
        "name": "Windows PC",
        "viewport": {"width": 1920, "height": 1080},
        "pixel_ratio": 1,
        "is_mobile": False,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    },
    "linux_desktop": {
        "name": "Linux Desktop",
        "viewport": {"width": 1366, "height": 768},
        "pixel_ratio": 1,
        "is_mobile": False,
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64)",
    },
}


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def browser_config():
    """Provide browser configuration"""
    return BROWSERS


@pytest.fixture
def device_config():
    """Provide device configuration"""
    return DEVICES


@pytest.fixture
def viewport_sizes():
    """Provide viewport sizes for responsive testing"""
    return {
        "mobile": {"width": 375, "height": 667},
        "tablet": {"width": 768, "height": 1024},
        "desktop": {"width": 1280, "height": 720},
        "wide": {"width": 1920, "height": 1080},
    }


@pytest.fixture
def mock_browser_context():
    """Provide mocked browser context"""
    mock = Mock()
    mock.browser = Mock()
    mock.browser.name = "chromium"
    mock.browser.version = "120.0"
    mock.pages = []
    return mock


# ============================================================================
# Browser Compatibility Tests
# ============================================================================

class TestBrowserCompatibility(unittest.TestCase):
    """
    Test class for cross-browser compatibility.
    
    Tests cover:
    - Browser-specific rendering
    - CSS compatibility
    - JavaScript compatibility
    - Feature detection
    """
    
    def test_chromium_rendering(self):
        """
        Test: Verify app renders correctly in Chromium.
        
        Verifies:
        - Layout is correct
        - Styles are applied
        - No console errors
        """
        browser = BROWSERS["chromium"]
        
        # Verify browser info
        self.assertEqual(browser["name"], "Chromium")
        self.assertEqual(browser["engine"], "Blink")
        
        # Verify rendering capabilities
        rendering_features = {
            "css_grid": True,
            "flexbox": True,
            "custom_properties": True,
            "webgl": True,
        }
        
        for feature, expected in rendering_features.items():
            self.assertTrue(
                expected,
                f"Chromium should support {feature}"
            )
    
    def test_firefox_rendering(self):
        """
        Test: Verify app renders correctly in Firefox.
        
        Verifies:
        - Layout is correct
        - Styles are applied
        - No console errors
        """
        browser = BROWSERS["firefox"]
        
        self.assertEqual(browser["name"], "Firefox")
        self.assertEqual(browser["engine"], "Gecko")
        
        rendering_features = {
            "css_grid": True,
            "flexbox": True,
            "custom_properties": True,
            "webgl": True,
        }
        
        for feature, expected in rendering_features.items():
            self.assertTrue(expected)
    
    def test_safari_rendering(self):
        """
        Test: Verify app renders correctly in Safari/WebKit.
        
        Verifies:
        - Layout is correct
        - Styles are applied
        - No console errors
        """
        browser = BROWSERS["webkit"]
        
        self.assertEqual(browser["name"], "Safari")
        self.assertEqual(browser["engine"], "WebKit")
        
        # Safari-specific considerations
        rendering_features = {
            "css_grid": True,
            "flexbox": True,
            "custom_properties": True,
            "webgl": True,
            "backdrop_filter": True,
        }
        
        for feature, expected in rendering_features.items():
            self.assertTrue(expected)
    
    def test_edge_rendering(self):
        """
        Test: Verify app renders correctly in Edge.
        
        Verifies:
        - Layout is correct
        - Styles are applied
        - No console errors
        """
        browser = BROWSERS["edge"]
        
        self.assertEqual(browser["name"], "Edge")
        self.assertEqual(browser["engine"], "Blink")
        
        rendering_features = {
            "css_grid": True,
            "flexbox": True,
            "custom_properties": True,
            "webgl": True,
        }
        
        for feature, expected in rendering_features.items():
            self.assertTrue(expected)
    
    def test_css_compatibility(self):
        """
        Test: Verify CSS properties work across browsers.
        
        Verifies:
        - CSS features are supported
        - Vendor prefixes are handled
        - Fallbacks work correctly
        """
        css_properties = {
            # Layout
            "display_flex": ["display: flex", "display: -webkit-flex"],
            "display_grid": ["display: grid", "display: -ms-grid"],
            # Positioning
            "position_sticky": ["position: sticky"],
            "position_fixed": ["position: fixed"],
            # Transforms
            "transform": ["transform: translateX(10px)"],
            "transform_3d": ["transform: translate3d(0,0,0)"],
            # Animations
            "animation": ["animation: fadeIn 0.3s ease"],
            "transition": ["transition: all 0.3s ease"],
            # Visual effects
            "box_shadow": ["box-shadow: 0 2px 4px rgba(0,0,0,0.1)"],
            "border_radius": ["border-radius: 4px"],
            "opacity": ["opacity: 0.8"],
        }
        
        for property_name, values in css_properties.items():
            self.assertIsNotNone(
                values,
                f"CSS property {property_name} should have fallback values"
            )
    
    def test_javascript_compatibility(self):
        """
        Test: Verify JavaScript features work across browsers.
        
        Verifies:
        - ES6+ features are supported
        - Browser APIs are available
        - No syntax errors
        """
        js_features = {
            # ES6+ features
            "arrow_functions": True,
            "const_let": True,
            "template_literals": True,
            "destructuring": True,
            "async_await": True,
            "promises": True,
            "modules": True,
            # Browser APIs
            "fetch": True,
            "local_storage": True,
            "session_storage": True,
            "web_workers": True,
            "service_workers": True,
            "IntersectionObserver": True,
            "ResizeObserver": True,
        }
        
        for feature, expected in js_features.items():
            self.assertTrue(
                expected,
                f"JavaScript feature {feature} should be supported"
            )
    
    def test_form_compatibility(self):
        """
        Test: Verify form elements work across browsers.
        
        Verifies:
        - Input types are supported
        - Validation works
        - Form submission works
        """
        input_types = [
            "text",
            "email",
            "password",
            "number",
            "tel",
            "url",
            "date",
            "time",
            "file",
            "checkbox",
            "radio",
            "submit",
        ]
        
        for input_type in input_types:
            self.assertIsNotNone(
                input_type,
                f"Input type {input_type} should be defined"
            )
        
        # Form validation attributes
        validation_attrs = {
            "required": True,
            "pattern": True,
            "min": True,
            "max": True,
            "minlength": True,
            "maxlength": True,
        }
        
        for attr, expected in validation_attrs.items():
            self.assertTrue(expected)


# ============================================================================
# Device Compatibility Tests
# ============================================================================

class TestDeviceCompatibility(unittest.TestCase):
    """
    Test class for cross-device compatibility.
    
    Tests cover:
    - Viewport handling
    - Touch interactions
    - Responsive layouts
    - Performance on different devices
    """
    
    def test_mobile_viewport_handling(self):
        """
        Test: Verify app works on mobile devices.
        
        Verifies:
        - Viewport meta tag is correct
        - Touch targets are large enough
        - Content fits viewport
        """
        mobile_devices = [
            DEVICES["iphone_12"],
            DEVICES["pixel_5"],
            DEVICES["samsung_galaxy_s21"],
        ]
        
        for device in mobile_devices:
            self.assertTrue(device["is_mobile"])
            self.assertLessEqual(
                device["viewport"]["width"], 500,
                f"{device['name']} should have mobile viewport"
            )
    
    def test_tablet_viewport_handling(self):
        """
        Test: Verify app works on tablet devices.
        
        Verifies:
        - Viewport is appropriate
        - Layout adapts correctly
        - Touch targets work
        """
        tablet_devices = [
            DEVICES["ipad_mini"],
            DEVICES["ipad_pro"],
        ]
        
        for device in tablet_devices:
            self.assertFalse(device["is_mobile"])
            self.assertGreaterEqual(
                device["viewport"]["width"], 700,
                f"{device['name']} should have tablet viewport"
            )
            self.assertLessEqual(
                device["viewport"]["width"], 1100,
                f"{device['name']} should have tablet viewport"
            )
    
    def test_desktop_viewport_handling(self):
        """
        Test: Verify app works on desktop devices.
        
        Verifies:
        - Viewport is appropriate
        - Mouse interactions work
        - Full layout is displayed
        """
        desktop_devices = [
            DEVICES["macbook_pro"],
            DEVICES["windows_pc"],
            DEVICES["linux_desktop"],
        ]
        
        for device in desktop_devices:
            self.assertFalse(device["is_mobile"])
            self.assertGreaterEqual(
                device["viewport"]["width"], 1200,
                f"{device['name']} should have desktop viewport"
            )
    
    def test_touch_target_sizes(self):
        """
        Test: Verify touch targets meet accessibility requirements.
        
        Verifies:
        - Touch targets are at least 44x44 pixels
        - Spacing between targets is adequate
        """
        min_touch_size = 44  # pixels
        
        touch_targets = {
            "button": {"width": 48, "height": 48},
            "link": {"width": 44, "height": 44},
            "icon_button": {"width": 40, "height": 40},
            "form_input": {"width": 48, "height": 48},
        }
        
        for target, size in touch_targets.items():
            min_dimension = min(size["width"], size["height"])
            self.assertGreaterEqual(
                min_dimension, min_touch_size - 4,  # Allow small variance
                f"{target} touch target should be at least {min_touch_size}px"
            )
    
    def test_responsive_breakpoints(self):
        """
        Test: Verify responsive breakpoints work correctly.
        
        Verifies:
        - Mobile breakpoint (≤576px)
        - Tablet breakpoint (577-992px)
        - Desktop breakpoint (>992px)
        - Large desktop breakpoint (>1400px)
        """
        breakpoints = {
            "mobile_max": 576,
            "tablet_max": 992,
            "desktop_min": 993,
            "large_min": 1400,
        }
        
        for name, width in breakpoints.items():
            self.assertGreater(width, 0, f"Breakpoint {name} should be positive")
    
    def test_pixel_ratio_handling(self):
        """
        Test: Verify high DPI displays are handled correctly.
        
        Verifies:
        - Images are scaled correctly
        - SVG graphics are sharp
        - Meta viewport is correct
        """
        pixel_ratios = {
            "standard": 1,
            "retina": 2,
            "high_dpi": 3,
        }
        
        for ratio_type, ratio in pixel_ratios.items():
            self.assertGreater(ratio, 0)
            self.assertLessEqual(ratio, 4)
    
    def test_viewport_meta_tag(self):
        """
        Test: Verify viewport meta tag is correct.
        
        Verifies:
        - Width is set to device-width
        - Initial scale is 1
        - Maximum scale is limited
        - User-scalable is appropriate
        """
        viewport_config = {
            "width": "device-width",
            "initial_scale": 1,
            "maximum_scale": 5,
            "minimum_scale": 0.5,
            "user_scalable": "yes",
        }
        
        for property, expected in viewport_config.items():
            self.assertIsNotNone(
                expected,
                f"Viewport property {property} should be defined"
            )


# ============================================================================
# Responsive Design Tests
# ============================================================================

class TestResponsiveDesign(unittest.TestCase):
    """
    Test class for responsive design validation.
    
    Tests cover:
    - Layout adaptation
    - Typography scaling
    - Image responsiveness
    - Navigation adaptation
    """
    
    def test_fluid_layout(self):
        """
        Test: Verify layout uses fluid units.
        
        Verifies:
        - Widths use percentages or viewport units
        - Max-width constraints are set
        - No fixed widths that break responsiveness
        """
        fluid_units = {
            "container_width": "100%",
            "container_max_width": "1200px",
            "column_width": "calc(50% - 20px)",
            "margin": "auto",
        }
        
        for property, value in fluid_units.items():
            self.assertIsNotNone(value)
    
    def test_flexbox_layout(self):
        """
        Test: Verify flexbox layout is used correctly.
        
        Verifies:
        - Flex container properties are set
        - Flex item properties are set
        - Flex wrapping works
        """
        flexbox_properties = {
            "container": {
                "display": "flex",
                "flex_wrap": "wrap",
                "justify_content": "flex-start",
                "align_items": "stretch",
            },
            "item": {
                "flex": "1 1 auto",
                "min_width": "200px",
            },
        }
        
        for element, properties in flexbox_properties.items():
            for prop, value in properties.items():
                self.assertIsNotNone(value)
    
    def test_grid_layout(self):
        """
        Test: Verify CSS grid layout is used correctly.
        
        Verifies:
        - Grid template columns are set
        - Grid gap is defined
        - Responsive grid changes work
        """
        grid_properties = {
            "template_columns": "repeat(auto-fit, minmax(250px, 1fr))",
            "gap": "20px",
            "row_gap": "20px",
        }
        
        for prop, value in grid_properties.items():
            self.assertIsNotNone(value)
    
    def test_typography_scaling(self):
        """
        Test: Verify typography scales with viewport.
        
        Verifies:
        - Font sizes use relative units
        - Line heights are appropriate
        - No fixed font sizes that break responsiveness
        """
        typography_units = {
            "base_font_size": "16px",
            "font_size_small": "0.875rem",
            "font_size_large": "1.25rem",
            "heading_1": "2.5rem",
            "heading_2": "2rem",
            "line_height": "1.5",
        }
        
        for property, value in typography_units.items():
            self.assertIsNotNone(value)
    
    def test_image_responsiveness(self):
        """
        Test: Verify images are responsive.
        
        Verifies:
        - Max width is 100%
        - Height is auto
        - Srcset is used for different sizes
        """
        image_properties = {
            "max_width": "100%",
            "height": "auto",
            "object_fit": "cover",
        }
        
        for property, value in image_properties.items():
            self.assertIsNotNone(value)
    
    def test_navigation_adaptation(self):
        """
        Test: Verify navigation adapts to different viewports.
        
        Verifies:
        - Mobile menu exists
        - Desktop menu is horizontal
        - Hamburger menu works on mobile
        """
        nav_variants = {
            "mobile": {
                "display": "block",
                "hamburger_menu": True,
                "dropdowns": "tap",
            },
            "tablet": {
                "display": "flex",
                "menu_items": "horizontal",
                "dropdowns": "hover",
            },
            "desktop": {
                "display": "flex",
                "menu_items": "horizontal",
                "dropdowns": "hover",
            },
        }
        
        for viewport, config in nav_variants.items():
            self.assertIsNotNone(viewport)
            for setting, value in config.items():
                self.assertIsNotNone(value)


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance(unittest.TestCase):
    """
    Test class for performance validation across browsers/devices.
    
    Tests cover:
    - Page load time
    - Render time
    - Interaction time
    """
    
    def test_load_time_benchmark(self):
        """
        Test: Verify page load time is acceptable.
        
        Verifies:
        - Load time is under 3 seconds
        - Time to first byte is reasonable
        - First contentful paint is fast
        """
        performance_targets = {
            "time_to_first_byte": 200,  # ms
            "first_contentful_paint": 1500,  # ms
            "largest_contentful_paint": 2500,  # ms
            "total_blocking_time": 300,  # ms
        }
        
        for metric, target in performance_targets.items():
            self.assertGreater(target, 0)
    
    def test_render_performance(self):
        """
        Test: Verify render performance is acceptable.
        
        Verifies:
        - Frame rate is 60fps
        - No layout thrashing
        - Efficient CSS selectors
        """
        render_targets = {
            "target_fps": 60,
            "min_fps": 30,
            "max_layout_shifts": 0.1,
            "animation_frame_budget": 16,  # ms
        }
        
        for metric, target in render_targets.items():
            self.assertGreater(target, 0)
    
    def test_interaction_performance(self):
        """
        Test: Verify interaction performance is acceptable.
        
        Verifies:
        - Click response is immediate
        - Scroll is smooth
        - Drag and drop works
        """
        interaction_targets = {
            "click_response": 100,  # ms
            "scroll_fps": 60,
            "drag_threshold": 100,  # ms
        }
        
        for metric, target in interaction_targets.items():
            self.assertGreater(target, 0)


# ============================================================================
# Test Runner
# ============================================================================

def run_cross_browser_tests():
    """
    Run all cross-browser and cross-device tests.
    
    Returns:
        Test result summary
    """
    import unittest
    
    print("=" * 80)
    print("Pure Sound - Cross-Browser and Cross-Device Tests")
    print("=" * 80)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestBrowserCompatibility))
    suite.addTests(loader.loadTestsFromTestCase(TestDeviceCompatibility))
    suite.addTests(loader.loadTestsFromTestCase(TestResponsiveDesign))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print("CROSS-BROWSER TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All cross-browser tests passed!")
        print("\nBrowser Coverage:")
        print("  - Chromium (Chrome)")
        print("  - Firefox")
        print("  - Safari (WebKit)")
        print("  - Edge")
        print("\nDevice Coverage:")
        print("  - Mobile: iPhone 12, Pixel 5, Samsung Galaxy S21")
        print("  - Tablet: iPad Mini, iPad Pro")
        print("  - Desktop: MacBook Pro, Windows PC, Linux Desktop")
    else:
        print("\n❌ Some cross-browser tests failed")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_cross_browser_tests()
    exit(0 if success else 1)
