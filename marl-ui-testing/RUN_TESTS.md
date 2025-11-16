# How to Run MARL-Generated Test Cases

This guide explains how to run the automatically generated UI test cases for the OWASP Juice Shop application.

## Prerequisites

1. **Juice Shop Application Running**
   ```bash
   # From the project root directory
   npm start
   ```
   The application should be running at `http://localhost:3000`

2. **Dependencies Installed**
   ```bash
   # From the project root directory
   npm install
   ```

## Step 1: Generate Tests (if not already done)

### Option A: Generate Tests Using the Demo
```bash
cd marl-ui-testing
python demo.py
```

### Option B: Generate Tests Using Example Scripts
```bash
cd marl-ui-testing
python example_usage.py
```

### Option C: Train Model and Generate Tests
```bash
cd marl-ui-testing
python train_marl.py
```

## Step 2: Verify Generated Tests

The generated tests should be saved to:
- `test/cypress/e2e/marl_generated_tests_*.spec.ts`
- `test/cypress/e2e/comprehensive_marl_tests.spec.ts`
- `test/cypress/e2e/demo_marl_tests.spec.ts`
- `test/cypress/e2e/final_generated_tests.spec.ts`

## Step 3: Run the Tests

### Option A: Run All Cypress Tests (Including MARL Tests)
```bash
# From project root
npm run cypress:run
```

### Option B: Run Only MARL-Generated Tests
```bash
# From project root
npx cypress run --spec "test/cypress/e2e/marl_generated_tests*.spec.ts"
npx cypress run --spec "test/cypress/e2e/comprehensive_marl_tests.spec.ts"
npx cypress run --spec "test/cypress/e2e/demo_marl_tests.spec.ts"
npx cypress run --spec "test/cypress/e2e/final_generated_tests.spec.ts"
```

### Option C: Run All MARL Tests (Wildcard)
```bash
npx cypress run --spec "test/cypress/e2e/*marl*.spec.ts"
```

### Option D: Open Cypress Test Runner (Interactive)
```bash
# From project root
npm run cypress:open
# Then select the test file you want to run from the UI
```

### Option E: Run Specific Test File
```bash
npx cypress run --spec "test/cypress/e2e/demo_marl_tests.spec.ts"
```

## Step 4: View Test Results

### Console Output
When running tests, you'll see output like:
```
✓ Login flow test (2000ms)
✓ Product search test (1500ms)
✗ Add to basket test (ERROR)
```

### Cypress Dashboard (if configured)
If you have Cypress Dashboard set up, results will be available at:
https://dashboard.cypress.io

### Test Reports
Cypress generates screenshots and videos for failed tests in:
- `cypress/screenshots/`
- `cypress/videos/`

## Troubleshooting

### Issue: Tests can't connect to application
**Solution:** Make sure Juice Shop is running on `http://localhost:3000`
```bash
npm start
```

### Issue: Tests fail with selector errors
**Solution:** The selectors might need adjustment. Check the generated test files and update selectors if needed.

### Issue: Cypress not found
**Solution:** Install Cypress
```bash
npm install --save-dev cypress
```

### Issue: TypeScript compilation errors
**Solution:** Ensure TypeScript is installed
```bash
npm install --save-dev typescript
```

### Issue: Tests timeout
**Solution:** Increase timeout in `cypress.config.ts` or add waits in test files.

## Quick Test Run Example

Here's a complete workflow:

```bash
# 1. Start the application (in one terminal)
npm start

# 2. Generate tests (in another terminal)
cd marl-ui-testing
python demo.py

# 3. Run the tests (in the same terminal)
cd ..
npx cypress run --spec "test/cypress/e2e/demo_marl_tests.spec.ts"
```

## Advanced Options

### Run Tests in Different Browsers
```bash
npx cypress run --browser chrome
npx cypress run --browser firefox
npx cypress run --browser edge
```

### Run Tests with Headless Mode (Default)
```bash
npx cypress run  # Already headless by default
```

### Run Tests with Browser Visible
```bash
npx cypress run --headed
```

### Run Tests with Specific Configuration
```bash
npx cypress run --config video=true,screenshotOnRunFailure=true
```

## Continuous Integration

For CI/CD pipelines, add to your workflow:

```yaml
- name: Run MARL Generated Tests
  run: |
    npm start &
    sleep 10
    npx cypress run --spec "test/cypress/e2e/*marl*.spec.ts"
```

## Next Steps

- Review generated test files in `test/cypress/e2e/`
- Customize tests for your specific needs
- Integrate into your CI/CD pipeline
- Generate more tests by running the training script again
