"""
Page Objects for Pure Sound E2E Tests

This module provides page object models for interacting with web pages
during end-to-end testing. Page objects encapsulate page-specific logic
and selectors, making tests more maintainable.
"""


# ============================================================================
# Login Page Object
# ============================================================================

class LoginPage:
    """
    Page object for the login page.
    
    Handles login form interactions.
    """
    
    # Selectors
    USERNAME_INPUT = "#username"
    EMAIL_INPUT = "#email"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "button[type='submit']"
    REMEMBER_ME_CHECKBOX = "#remember-me"
    ERROR_MESSAGE = ".error-message"
    
    def __init__(self, page):
        self.page = page
        self.base_url = ""
    
    def navigate(self, url=None):
        """Navigate to login page"""
        login_url = url or f"{self.base_url}/login"
        self.page.goto(login_url)
    
    def is_loaded(self):
        """Check if login page is loaded"""
        return self.page.is_visible(self.USERNAME_INPUT)
    
    def login(self, username, password, remember_me=False):
        """Perform login action"""
        self.page.fill(self.USERNAME_INPUT, username)
        self.page.fill(self.PASSWORD_INPUT, password)
        if remember_me:
            self.page.click(self.REMEMBER_ME_CHECKBOX)
        self.page.click(self.LOGIN_BUTTON)
        self.page.wait_for_timeout(1000)
        return {"success": True, "username": username}
    
    def get_error_message(self):
        """Get login error message"""
        if self.page.is_visible(self.ERROR_MESSAGE):
            return self.page.text_content(self.ERROR_MESSAGE)
        return ""


# ============================================================================
# Dashboard Page Object
# ============================================================================

class DashboardPage:
    """
    Page object for the main dashboard.
    
    Handles dashboard interactions.
    """
    
    # Navigation
    HOME_LINK = "a[href='/dashboard']"
    JOBS_LINK = "a[href='/jobs']"
    
    # User section
    USER_PROFILE_LINK = "a[href='/profile']"
    USER_NAME = ".user-name"
    LOGOUT_LINK = "a[href='/logout']"
    
    # Quick actions
    UPLOAD_BUTTON = "button:has-text('Upload')"
    NEW_JOB_BUTTON = "button:has-text('New Job')"
    ANALYZE_BUTTON = "button:has-text('Analyze')"
    
    # Dashboard content
    WELCOME_MESSAGE = ".welcome-message"
    JOB_CARDS = ".job-card"
    STATS_CARDS = ".stats-card"
    
    def __init__(self, page):
        self.page = page
    
    def navigate(self, url=None):
        """Navigate to dashboard"""
        dashboard_url = url or f"{self.page.context.pages[0].url if self.page.context.pages else ''}/dashboard"
        self.page.goto(dashboard_url)
    
    def is_loaded(self):
        """Check if dashboard is loaded"""
        return self.page.is_visible(self.WELCOME_MESSAGE) or self.page.is_visible(self.HOME_LINK)
    
    def get_user_name(self):
        """Get logged-in user name"""
        if self.page.is_visible(self.USER_NAME):
            return self.page.text_content(self.USER_NAME)
        return ""
    
    def click_jobs(self):
        """Navigate to jobs page"""
        self.page.click(self.JOBS_LINK)
    
    def click_profile(self):
        """Navigate to profile page"""
        self.page.click(self.USER_PROFILE_LINK)
    
    def logout(self):
        """Log out"""
        self.page.click(self.LOGOUT_LINK)


# ============================================================================
# Jobs Page Object
# ============================================================================

class JobsPage:
    """
    Page object for the jobs management page.
    
    Handles job-related interactions.
    """
    
    PAGE_TITLE = "h1:has-text('Jobs')"
    NEW_JOB_BUTTON = "button:has-text('New Job')"
    JOB_ITEMS = ".job-item"
    
    # Filters
    STATUS_FILTER = "#status-filter"
    SEARCH_INPUT = "#job-search"
    
    def __init__(self, page):
        self.page = page
    
    def navigate(self, url=None):
        """Navigate to jobs page"""
        jobs_url = url or "/jobs"
        self.page.goto(jobs_url)
    
    def is_loaded(self):
        """Check if jobs page is loaded"""
        return self.page.is_visible(self.PAGE_TITLE)
    
    def get_job_count(self):
        """Get total number of jobs"""
        return len(self.page.query_selector_all(self.JOB_ITEMS))
    
    def filter_by_status(self, status):
        """Filter jobs by status"""
        self.page.select_option(self.STATUS_FILTER, status)
    
    def cancel_job(self, job_id):
        """Cancel a pending or running job"""
        job_item = self.page.query_selector(f"[data-job-id='{job_id}']")
        if job_item:
            cancel_btn = job_item.locator("button:has-text('Cancel')")
            if cancel_btn.is_enabled():
                cancel_btn.click()
                return True
        return False


# ============================================================================
# Profile Page Object
# ============================================================================

class ProfilePage:
    """
    Page object for the user profile page.
    
    Handles profile-related interactions.
    """
    
    PAGE_TITLE = "h1:has-text('Profile')"
    
    # Profile form
    USERNAME_INPUT = "#username"
    EMAIL_INPUT = "#email"
    FULL_NAME_INPUT = "#full-name"
    BIO_INPUT = "#bio"
    
    # Save buttons
    SAVE_PROFILE_BUTTON = "button:has-text('Save Profile')"
    SUCCESS_MESSAGE = ".success-message"
    
    # Settings
    NOTIFICATION_TOGGLE = "#notifications"
    THEME_SELECT = "#theme"
    LANGUAGE_SELECT = "#language"
    
    # Password section
    CURRENT_PASSWORD_INPUT = "#current-password"
    NEW_PASSWORD_INPUT = "#new-password"
    CHANGE_PASSWORD_BUTTON = "button:has-text('Change Password')"
    
    def __init__(self, page):
        self.page = page
    
    def navigate(self, url=None):
        """Navigate to profile page"""
        profile_url = url or "/profile"
        self.page.goto(profile_url)
    
    def is_loaded(self):
        """Check if profile page is loaded"""
        return self.page.is_visible(self.PAGE_TITLE)
    
    def update_profile(self, data):
        """Update profile information"""
        if "username" in data:
            self.page.fill(self.USERNAME_INPUT, data["username"])
        if "email" in data:
            self.page.fill(self.EMAIL_INPUT, data["email"])
        if "full_name" in data:
            self.page.fill(self.FULL_NAME_INPUT, data["full_name"])
        if "bio" in data:
            self.page.fill(self.BIO_INPUT, data["bio"])
        
        self.page.click(self.SAVE_PROFILE_BUTTON)
        self.page.wait_for_timeout(1000)
        return self.page.is_visible(self.SUCCESS_MESSAGE)
    
    def change_password(self, current, new):
        """Change user password"""
        self.page.fill(self.CURRENT_PASSWORD_INPUT, current)
        self.page.fill(self.NEW_PASSWORD_INPUT, new)
        self.page.click(self.CHANGE_PASSWORD_BUTTON)
        self.page.wait_for_timeout(1000)
        return self.page.is_visible(self.SUCCESS_MESSAGE)


# ============================================================================
# Search Page Object
# ============================================================================

class SearchPage:
    """
    Page object for search functionality.
    
    Handles search-related interactions.
    """
    
    SEARCH_INPUT = "#search-input"
    SEARCH_BUTTON = "button:has-text('Search')"
    RESULT_ITEMS = ".result-item"
    NO_RESULTS_MESSAGE = ".no-results"
    
    # Filters
    CATEGORY_FILTER = "#category-filter"
    FORMAT_FILTER = "#format-filter"
    
    def __init__(self, page):
        self.page = page
    
    def navigate(self, url=None):
        """Navigate to search page"""
        search_url = url or "/search"
        self.page.goto(search_url)
    
    def is_loaded(self):
        """Check if search page is loaded"""
        return self.page.is_visible(self.SEARCH_INPUT)
    
    def search(self, query):
        """Perform search"""
        self.page.fill(self.SEARCH_INPUT, query)
        self.page.click(self.SEARCH_BUTTON)
        self.page.wait_for_timeout(1000)
    
    def get_results(self):
        """Get search results"""
        results = []
        for item in self.page.query_selector_all(self.RESULT_ITEMS):
            results.append({
                "id": item.get_attribute("data-id"),
                "name": item.text_content().strip(),
            })
        return results
    
    def filter_by_category(self, category):
        """Filter results by category"""
        self.page.select_option(self.CATEGORY_FILTER, category)
        self.page.wait_for_timeout(500)
    
    def has_results(self):
        """Check if search has results"""
        return self.page.is_visible(self.RESULT_ITEMS)


# ============================================================================
# Checkout Page Object
# ============================================================================

class CheckoutPage:
    """
    Page object for checkout and payment flow.
    
    Handles checkout interactions.
    """
    
    PAGE_TITLE = "h1:has-text('Checkout')"
    CART_ITEMS = ".cart-item"
    
    # Payment form
    CARD_NUMBER_INPUT = "#card-number"
    EXPIRY_INPUT = "#expiry"
    CVV_INPUT = "#cvv"
    
    # Billing address
    ADDRESS_INPUT = "#address"
    CITY_INPUT = "#city"
    ZIP_INPUT = "#zip"
    
    # Buttons
    PLACE_ORDER_BUTTON = "button:has-text('Place Order')"
    ORDER_CONFIRMATION = ".order-confirmation"
    
    def __init__(self, page):
        self.page = page
    
    def navigate(self, url=None):
        """Navigate to checkout page"""
        checkout_url = url or "/checkout"
        self.page.goto(checkout_url)
    
    def is_loaded(self):
        """Check if checkout page is loaded"""
        return self.page.is_visible(self.PAGE_TITLE)
    
    def get_order_total(self):
        """Get order total"""
        total_element = self.page.query_selector(".order-total")
        if total_element:
            text = total_element.text_content()
            return float(text.replace("$", ""))
        return 0.0
    
    def enter_payment_info(self, payment_data):
        """Enter payment information"""
        self.page.fill(self.CARD_NUMBER_INPUT, payment_data.get("card_number", ""))
        self.page.fill(self.EXPIRY_INPUT, payment_data.get("expiry", ""))
        self.page.fill(self.CVV_INPUT, payment_data.get("cvv", ""))
    
    def enter_billing_address(self, address_data):
        """Enter billing address"""
        self.page.fill(self.ADDRESS_INPUT, address_data.get("address", ""))
        self.page.fill(self.CITY_INPUT, address_data.get("city", ""))
        self.page.fill(self.ZIP_INPUT, address_data.get("zip", ""))
    
    def place_order(self):
        """Place order"""
        self.page.click(self.PLACE_ORDER_BUTTON)
        self.page.wait_for_timeout(2000)
        return self.page.is_visible(self.ORDER_CONFIRMATION)
    
    def is_order_confirmed(self):
        """Check if order is confirmed"""
        return self.page.is_visible(self.ORDER_CONFIRMATION)
