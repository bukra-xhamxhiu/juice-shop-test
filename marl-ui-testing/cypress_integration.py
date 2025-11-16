"""
Cypress Integration for MARL-generated UI Tests
Converts MARL-generated test scenarios into executable Cypress test files.
"""

import os
from typing import List, Dict, Any
from datetime import datetime


class CypressTestGenerator:
    """
    Generates Cypress test files from MARL-generated test scenarios.
    """
    
    def __init__(self):
        self.test_template = self._load_test_template()
        self.cypress_commands = {
            'navigate': 'cy.visit',
            'click': 'cy.get',
            'type': 'cy.get',
            'wait': 'cy.wait',
            'scroll': 'cy.scrollTo',
            'hover': 'cy.get',
            'select': 'cy.get',
            'check': 'cy.get',
            'uncheck': 'cy.get'
        }
    
    def _load_test_template(self) -> str:
        """Load the base Cypress test template."""
        return '''
import {{ }} from 'cypress'

describe('MARL Generated Tests - {test_name}', () => {{
  beforeEach(() => {{
    // Setup before each test
    cy.visit('http://localhost:3000')
  }})

  it('{test_description}', () => {{
    {test_steps}
  }})
}})
'''
    
    def generate_cypress_tests(self, test_scenarios: List[Dict[str, Any]]) -> str:
        """Generate Cypress test file from multiple test scenarios."""
        test_file_content = self._generate_file_header()
        
        for i, scenario in enumerate(test_scenarios):
            test_content = self._generate_single_test(scenario, i)
            test_file_content += test_content + '\n\n'
        
        return test_file_content
    
    def _generate_file_header(self) -> str:
        """Generate file header with imports and setup."""
        return f'''/*
 * MARL Generated Cypress Tests
 * Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * 
 * These tests were automatically generated using Multi-Agent Reinforcement Learning
 * for UI test generation on the OWASP Juice Shop application.
 */

import {{ }} from 'cypress'

// Global test configuration
const BASE_URL = 'http://localhost:3000'
const DEFAULT_TIMEOUT = 10000

// Custom commands for MARL-generated tests
Cypress.Commands.add('marlWait', (ms = 1000) => {{
  cy.wait(ms)
}})

Cypress.Commands.add('marlScrollToElement', (selector) => {{
  cy.get(selector).scrollIntoView()
}})

Cypress.Commands.add('marlTypeWithDelay', (selector, text, delay = 100) => {{
  cy.get(selector).clear()
  cy.get(selector).type(text, {{ delay }})
}})

'''
    
    def _generate_single_test(self, scenario: Dict[str, Any], test_index: int) -> str:
        """Generate a single Cypress test from a test scenario."""
        test_name = scenario.get('name', f'marl_test_{test_index}')
        test_pattern = scenario.get('pattern', 'general')
        steps = scenario.get('steps', [])
        assertions = scenario.get('assertions', [])
        
        # Generate test description
        test_description = self._generate_test_description(scenario)
        
        # Generate test steps
        test_steps = self._generate_test_steps(steps)
        
        # Generate assertions
        test_assertions = self._generate_assertions(assertions)
        
        # Combine everything
        test_content = f'''
describe('{test_name} - {test_pattern}', () => {{
  beforeEach(() => {{
    cy.visit(BASE_URL)
    cy.marlWait(1000) // Wait for page to load
  }})

  it('{test_description}', () => {{
    {test_steps}
    
    // Assertions
    {test_assertions}
  }})
}})
'''
        
        return test_content
    
    def _generate_test_description(self, scenario: Dict[str, Any]) -> str:
        """Generate human-readable test description."""
        pattern = scenario.get('pattern', 'general')
        
        descriptions = {
            'login_flow': 'should successfully complete login flow',
            'registration_flow': 'should successfully complete user registration',
            'product_search': 'should search for products and display results',
            'add_to_basket': 'should add product to shopping basket',
            'checkout_flow': 'should complete checkout process',
            'user_profile': 'should access and modify user profile',
            'admin_functions': 'should perform administrative functions',
            'error_handling': 'should handle error conditions properly',
            'security_tests': 'should validate security measures',
            'accessibility_tests': 'should meet accessibility requirements'
        }
        
        return descriptions.get(pattern, 'should perform automated test scenario')
    
    def _generate_test_steps(self, steps: List[Dict[str, Any]]) -> str:
        """Generate Cypress test steps from scenario steps."""
        if not steps:
            return '// No test steps defined'
        
        generated_steps = []
        
        for step in steps:
            action = step.get('action', '')
            target = step.get('target', '')
            value = step.get('value', '')
            duration = step.get('duration', 1000)
            
            step_code = self._generate_step_code(action, target, value, duration)
            if step_code:
                generated_steps.append(step_code)
        
        return '\n    '.join(generated_steps)
    
    def _generate_step_code(self, action: str, target: str, value: str, duration: int) -> str:
        """Generate Cypress code for a single step."""
        if action == 'navigate':
            if target.startswith('/'):
                return f'cy.visit(BASE_URL + "{target}")'
            else:
                return f'cy.visit("{target}")'
        
        elif action == 'click':
            selector = self._generate_selector(target)
            return f'cy.get("{selector}").click()'
        
        elif action == 'type':
            selector = self._generate_selector(target)
            if value:
                return f'cy.marlTypeWithDelay("{selector}", "{value}")'
            else:
                return f'cy.get("{selector}").clear()'
        
        elif action == 'wait':
            return f'cy.marlWait({duration})'
        
        elif action == 'scroll':
            if target:
                selector = self._generate_selector(target)
                return f'cy.marlScrollToElement("{selector}")'
            else:
                return f'cy.scrollTo("bottom")'
        
        elif action == 'hover':
            selector = self._generate_selector(target)
            return f'cy.get("{selector}").trigger("mouseover")'
        
        elif action == 'select':
            selector = self._generate_selector(target)
            return f'cy.get("{selector}").select("{value}")'
        
        elif action == 'check':
            selector = self._generate_selector(target)
            return f'cy.get("{selector}").check()'
        
        elif action == 'uncheck':
            selector = self._generate_selector(target)
            return f'cy.get("{selector}").uncheck()'
        
        else:
            return f'// Unknown action: {action}'
    
    def _generate_selector(self, target: str) -> str:
        """Generate CSS selector from target description."""
        # Handle different target formats
        if target.startswith('#'):
            return target  # Already a CSS selector
        elif target.startswith('.'):
            return target  # Already a CSS selector
        elif target.startswith('[') and target.endswith(']'):
            return target  # Already a CSS selector
        else:
            # Convert common target names to selectors
            selector_map = {
                'email': 'input[type="email"], input[name="email"], #email',
                'password': 'input[type="password"], input[name="password"], #password',
                'login_button': 'button[type="submit"], .login-button, #loginButton',
                'search_input': 'input[type="search"], input[name="search"], #searchQuery',
                'search_button': 'button[type="submit"], .search-button, #searchButton',
                'add_to_basket_button': '.add-to-basket, .add-to-cart, [data-testid="add-to-basket"]',
                'basket_button': '.basket, .cart, [data-testid="basket"]',
                'user_menu': '.user-menu, .account-menu, [data-testid="user-menu"]',
                'product_card': '.product-card, .product-item, [data-testid="product"]',
                'basket_item': '.basket-item, .cart-item, [data-testid="basket-item"]',
                'basket_count': '.basket-count, .cart-count, [data-testid="basket-count"]'
            }
            
            return selector_map.get(target, f'[data-testid="{target}"], #{target}, .{target}')
    
    def _generate_assertions(self, assertions: List[Dict[str, Any]]) -> str:
        """Generate Cypress assertions from scenario assertions."""
        if not assertions:
            return '// No assertions defined'
        
        generated_assertions = []
        
        for assertion in assertions:
            assertion_type = assertion.get('type', '')
            target = assertion.get('target', '')
            value = assertion.get('value', '')
            min_count = assertion.get('min', 1)
            
            assertion_code = self._generate_assertion_code(assertion_type, target, value, min_count)
            if assertion_code:
                generated_assertions.append(assertion_code)
        
        return '\n    '.join(generated_assertions)
    
    def _generate_assertion_code(self, assertion_type: str, target: str, value: str, min_count: int) -> str:
        """Generate Cypress assertion code."""
        if assertion_type == 'element_visible':
            selector = self._generate_selector(target)
            return f'cy.get("{selector}").should("be.visible")'
        
        elif assertion_type == 'element_count':
            selector = self._generate_selector(target)
            return f'cy.get("{selector}").should("have.length.at.least", {min_count})'
        
        elif assertion_type == 'text_contains':
            selector = self._generate_selector(target)
            return f'cy.get("{selector}").should("contain.text", "{value}")'
        
        elif assertion_type == 'url_contains':
            return f'cy.url().should("include", "{value}")'
        
        elif assertion_type == 'attribute_equals':
            selector = self._generate_selector(target)
            attr_name = assertion.get('attribute', 'value')
            return f'cy.get("{selector}").should("have.attr", "{attr_name}", "{value}")'
        
        elif assertion_type == 'css_property':
            selector = self._generate_selector(target)
            property_name = assertion.get('property', 'color')
            return f'cy.get("{selector}").should("have.css", "{property_name}", "{value}")'
        
        elif assertion_type == 'performance_metric':
            metric_name = assertion.get('metric', 'loadTime')
            threshold = assertion.get('threshold', 3000)
            return f'cy.window().its("performance.timing.loadEventEnd").should("be.less.than", {threshold})'
        
        elif assertion_type == 'accessibility_check':
            return f'cy.injectAxe()\n    cy.checkA11y()'
        
        else:
            return f'// Unknown assertion type: {assertion_type}'
    
    def save_test_file(self, test_content: str, filename: str = None) -> str:
        """Save generated test content to file."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'marl_generated_tests_{timestamp}.spec.ts'
        elif not filename.endswith('.spec.ts'):
            # Ensure .spec.ts extension for Cypress compatibility
            if filename.endswith('.ts'):
                filename = filename[:-3] + '.spec.ts'
            else:
                filename = filename + '.spec.ts'
        
        # Ensure the test directory exists
        test_dir = '../test/cypress/e2e'
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
        
        filepath = os.path.join(test_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        return filepath
    
    def generate_test_data(self, test_scenarios: List[Dict[str, Any]]) -> str:
        """Generate test data file for the generated tests."""
        test_data = {
            'users': {
                'valid_user': {
                    'email': 'test@example.com',
                    'password': 'password123',
                    'firstName': 'Test',
                    'lastName': 'User'
                },
                'admin_user': {
                    'email': 'admin@juice-sh.op',
                    'password': 'admin123',
                    'role': 'admin'
                }
            },
            'products': {
                'apple_juice': {
                    'name': 'Apple Juice',
                    'price': 1.99,
                    'description': 'Fresh apple juice'
                },
                'orange_juice': {
                    'name': 'Orange Juice',
                    'price': 2.49,
                    'description': 'Fresh orange juice'
                }
            },
            'test_strings': {
                'xss_payload': '<script>alert("XSS")</script>',
                'sql_injection': "' OR '1'='1",
                'long_string': 'A' * 1000,
                'special_chars': '!@#$%^&*()_+-=[]{}|;:,.<>?'
            }
        }
        
        import json
        return json.dumps(test_data, indent=2)
    
    def generate_readme(self) -> str:
        """Generate README file for the generated tests."""
        return '''# MARL Generated UI Tests

This directory contains automatically generated UI tests for the OWASP Juice Shop application using Multi-Agent Reinforcement Learning (MARL).

## Overview

These tests were generated by two AI agents:
1. **UI Exploration Agent**: Discovers and maps UI elements
2. **Test Generation Agent**: Creates test scenarios based on discovered patterns

## Running the Tests

1. Start the Juice Shop application:
   ```bash
   npm start
   ```

2. Run the generated tests:
   ```bash
   npx cypress run --spec "test/cypress/e2e/marl_generated_tests_*.ts"
   ```

3. Open Cypress Test Runner:
   ```bash
   npx cypress open
   ```

## Test Categories

The generated tests cover various scenarios:
- Login and registration flows
- Product search and browsing
- Shopping basket operations
- User profile management
- Administrative functions
- Security and accessibility tests

## Customization

You can modify the generated tests to:
- Add more specific assertions
- Include additional test data
- Customize selectors for your application
- Add performance and accessibility checks

## Notes

- Tests are generated based on the current state of the application
- Some tests may need manual adjustment for specific scenarios
- Regular regeneration is recommended as the application evolves
'''

