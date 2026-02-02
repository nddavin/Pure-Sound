/**
 * Playwright Configuration for Pure Sound E2E Tests
 * 
 * This configuration file sets up Playwright for running end-to-end tests
 * on the Pure Sound application.
 * 
 * Usage:
 *   npx playwright test --config=tests/e2e/playwright.config.js
 *   npx playwright test --config=tests/e2e/playwright.config.js --headed
 *   npx playwright test --config=tests/e2e/playwright.config.js --reporter=html
 */

const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  // Test directory
  testDir: '.',
  
  // Output directory for test artifacts
  outputDir: 'test-results/',
  
  // Snapshot directory
  snapshotDir: 'tests/e2e/snapshots/',
  
  // Fully parallelize tests
  fullyParallel: true,
  
  // Fail tests on flaky failures
  forbidOnly: !!process.env.CI,
  
  // Retry failures
  retries: process.env.CI ? 2 : 0,
  
  // Workers for parallel execution
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter configuration
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/e2e-results.json' }]
  ],
  
  // Global timeout
  timeout: 30000,
  
  // Expect timeout
  expect: {
    timeout: 5000,
  },
  
  // Base URL for tests
  baseURL: process.env.PURE_SOUND_BASE_URL || 'http://localhost:8080',
  
  // Environment variables
  use: {
    // Base URL for all requests
    baseURL: process.env.PURE_SOUND_BASE_URL || 'http://localhost:8080',
    
    // Trace recording
    trace: 'on-first-retry',
    
    // Screenshot on failure
    screenshot: 'only-on-failure',
    
    // Video recording
    video: 'retain-on-failure',
    
    // HTTP credentials
    httpCredentials: {
      username: process.env.HTTP_USERNAME || '',
      password: process.env.HTTP_PASSWORD || '',
    },
    
    // Locale
    locale: 'en-US',
    
    // Timezone
    timezoneId: 'America/New_York',
  },
  
  // Projects configuration - Test on multiple browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // Mobile testing
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  
  // Web server configuration
  webServer: {
    command: 'python -m http.server 8080',
    url: 'http://localhost:8080',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
