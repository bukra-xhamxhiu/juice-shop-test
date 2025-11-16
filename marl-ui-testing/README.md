# MARL-Based UI Test Generation for Juice Shop

This project implements a Multi-Agent Reinforcement Learning (MARL) system to automatically generate UI tests for the OWASP Juice Shop application.

## Architecture Overview

### Two-Agent System

1. **UI Exploration Agent**: Discovers and maps UI elements
2. **Test Generation Agent**: Creates test scenarios based on discovered patterns

### Key Components

- **State Representation**: DOM structure, element properties, user context
- **Action Spaces**: UI interactions and test generation actions
- **Reward System**: Coverage, quality, and bug discovery metrics
- **Deep Learning Models**: Neural networks for policy learning

## Getting Started

1. Install dependencies: `npm install`
2. Start Juice Shop: `npm start`
3. Run MARL training: `python train_marl.py`
4. Generate tests: `python generate_tests.py`

## Integration

The system integrates with existing Cypress tests and can generate new test files in the `test/cypress/e2e/` directory.

