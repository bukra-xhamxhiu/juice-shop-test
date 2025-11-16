# Quick Start: Run MARL-Generated Tests

## Fastest Way to Run Tests

### 1. Make sure Juice Shop is running
```bash
# Terminal 1: From project root
npm start
```

### 2. Generate tests (if you haven't already)
```bash
# Terminal 2: From marl-ui-testing directory
cd marl-ui-testing
python demo.py
```

### 3. Run the generated tests
```bash
# Terminal 2: From project root (cd .. from marl-ui-testing)
npx cypress run --spec "test/cypress/e2e/demo_marl_tests.spec.ts"
```

## All-in-One Commands

### Generate and Run in One Go
```bash
# Terminal 1
npm start

# Terminal 2
cd marl-ui-testing && python demo.py && cd .. && npx cypress run --spec "test/cypress/e2e/demo_marl_tests.spec.ts"
```

### Interactive Test Runner
```bash
# Terminal 1
npm start

# Terminal 2
npm run cypress:open
# Then click on the test file in the Cypress UI
```

## Common Commands Summary

| Command | Description |
|---------|-------------|
| `npm start` | Start Juice Shop application |
| `npx cypress run` | Run all Cypress tests headlessly |
| `npm run cypress:open` | Open Cypress Test Runner (interactive) |
| `npx cypress run --spec "test/cypress/e2e/demo_marl_tests.spec.ts"` | Run specific test file |
| `npx cypress run --spec "test/cypress/e2e/*marl*.spec.ts"` | Run all MARL-generated tests |

## Troubleshooting Quick Fixes

**Tests can't connect?** → Make sure `npm start` is running on port 3000

**No tests found?** → Check if files exist in `test/cypress/e2e/` with `.spec.ts` extension

**Cypress not installed?** → Run `npm install` from project root

For more details, see `RUN_TESTS.md`
