"""
Example Usage of MARL-based UI Test Generation
Shows different ways to use the system for various testing scenarios.
"""

import os
import sys
import json
import numpy as np
from typing import List, Dict, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from marl_agents import MARLSystem, Action
from reward_system import RewardCalculator
from ui_state_representation import UIStateRepresentation
from cypress_integration import CypressTestGenerator


class MARLTestGenerator:
    """
    High-level interface for MARL-based test generation.
    """
    
    def __init__(self):
        self.marl_system = MARLSystem()
        self.reward_calculator = RewardCalculator()
        self.cypress_generator = CypressTestGenerator()
    
    def generate_login_tests(self, num_tests: int = 5) -> List[Dict[str, Any]]:
        """Generate login-related test scenarios."""
        print(f"Generating {num_tests} login test scenarios...")
        
        test_scenarios = []
        for i in range(num_tests):
            exploration_data = {
                'ui_state': np.random.random(200),
                'coverage': {'page_coverage': 0.1, 'element_coverage': 0.2, 'interaction_coverage': 0.1},
                'quality': {'test_diversity': 0.8, 'test_complexity': 0.6, 'assertion_coverage': 0.7}
            }
            
            # Force login pattern
            scenario = self.marl_system.test_generation_agent.generate_test(exploration_data)
            scenario['pattern'] = 'login_flow'
            scenario['name'] = f'login_test_{i+1}'
            
            # Customize for login scenarios
            scenario['steps'] = [
                {'action': 'navigate', 'target': '/login'},
                {'action': 'type', 'target': 'email', 'value': 'test@example.com'},
                {'action': 'type', 'target': 'password', 'value': 'password123'},
                {'action': 'click', 'target': 'login_button'}
            ]
            
            scenario['assertions'] = [
                {'type': 'url_contains', 'value': '/search'},
                {'type': 'element_visible', 'target': 'user_menu'}
            ]
            
            test_scenarios.append(scenario)
        
        return test_scenarios
    
    def generate_security_tests(self, num_tests: int = 3) -> List[Dict[str, Any]]:
        """Generate security-focused test scenarios."""
        print(f"Generating {num_tests} security test scenarios...")
        
        security_patterns = [
            'xss_injection',
            'sql_injection', 
            'authentication_bypass',
            'authorization_test',
            'input_validation'
        ]
        
        test_scenarios = []
        for i in range(num_tests):
            pattern = security_patterns[i % len(security_patterns)]
            
            scenario = {
                'name': f'security_test_{i+1}',
                'pattern': pattern,
                'priority': 'high',
                'steps': [],
                'assertions': [],
                'test_data': {}
            }
            
            if pattern == 'xss_injection':
                scenario['steps'] = [
                    {'action': 'navigate', 'target': '/search'},
                    {'action': 'type', 'target': 'search_input', 'value': '<script>alert("XSS")</script>'},
                    {'action': 'click', 'target': 'search_button'}
                ]
                scenario['assertions'] = [
                    {'type': 'text_contains', 'target': '.search-results', 'value': 'No results found'},
                    {'type': 'element_count', 'target': 'script', 'max': 0}
                ]
            
            elif pattern == 'sql_injection':
                scenario['steps'] = [
                    {'action': 'navigate', 'target': '/login'},
                    {'action': 'type', 'target': 'email', 'value': "admin@juice-sh.op' OR '1'='1"},
                    {'action': 'type', 'target': 'password', 'value': 'password'},
                    {'action': 'click', 'target': 'login_button'}
                ]
                scenario['assertions'] = [
                    {'type': 'url_contains', 'value': '/login'},
                    {'type': 'text_contains', 'target': '.error-message', 'value': 'Invalid'}
                ]
            
            elif pattern == 'authentication_bypass':
                scenario['steps'] = [
                    {'action': 'navigate', 'target': '/administration'},
                    {'action': 'wait', 'duration': 2000}
                ]
                scenario['assertions'] = [
                    {'type': 'url_contains', 'value': '/login'},
                    {'type': 'text_contains', 'target': 'body', 'value': 'Access denied'}
                ]
            
            test_scenarios.append(scenario)
        
        return test_scenarios
    
    def generate_ecommerce_tests(self, num_tests: int = 4) -> List[Dict[str, Any]]:
        """Generate e-commerce workflow test scenarios."""
        print(f"Generating {num_tests} e-commerce test scenarios...")
        
        ecommerce_flows = [
            'product_search_and_browse',
            'add_to_cart_flow',
            'checkout_process',
            'user_registration'
        ]
        
        test_scenarios = []
        for i in range(num_tests):
            flow = ecommerce_flows[i % len(ecommerce_flows)]
            
            scenario = {
                'name': f'ecommerce_test_{i+1}',
                'pattern': flow,
                'priority': 'medium',
                'steps': [],
                'assertions': [],
                'test_data': {}
            }
            
            if flow == 'product_search_and_browse':
                scenario['steps'] = [
                    {'action': 'navigate', 'target': '/search'},
                    {'action': 'type', 'target': 'search_input', 'value': 'apple'},
                    {'action': 'click', 'target': 'search_button'},
                    {'action': 'wait', 'duration': 2000},
                    {'action': 'click', 'target': '.product-card:first-child'}
                ]
                scenario['assertions'] = [
                    {'type': 'element_count', 'target': '.product-card', 'min': 1},
                    {'type': 'text_contains', 'target': '.product-details', 'value': 'Apple'}
                ]
            
            elif flow == 'add_to_cart_flow':
                scenario['steps'] = [
                    {'action': 'navigate', 'target': '/search'},
                    {'action': 'click', 'target': '.product-card:first-child'},
                    {'action': 'click', 'target': '.add-to-basket-button'},
                    {'action': 'click', 'target': '.basket-button'}
                ]
                scenario['assertions'] = [
                    {'type': 'element_visible', 'target': '.basket-item'},
                    {'type': 'text_contains', 'target': '.basket-count', 'value': '1'}
                ]
            
            elif flow == 'checkout_process':
                scenario['steps'] = [
                    {'action': 'navigate', 'target': '/basket'},
                    {'action': 'click', 'target': '.checkout-button'},
                    {'action': 'type', 'target': 'address', 'value': '123 Test Street'},
                    {'action': 'type', 'target': 'city', 'value': 'Test City'},
                    {'action': 'click', 'target': '.submit-order-button'}
                ]
                scenario['assertions'] = [
                    {'type': 'url_contains', 'value': '/order-completion'},
                    {'type': 'text_contains', 'target': '.success-message', 'value': 'Order placed'}
                ]
            
            elif flow == 'user_registration':
                scenario['steps'] = [
                    {'action': 'navigate', 'target': '/register'},
                    {'action': 'type', 'target': 'email', 'value': 'newuser@example.com'},
                    {'action': 'type', 'target': 'password', 'value': 'newpassword123'},
                    {'action': 'type', 'target': 'confirm_password', 'value': 'newpassword123'},
                    {'action': 'click', 'target': 'register_button'}
                ]
                scenario['assertions'] = [
                    {'type': 'url_contains', 'value': '/login'},
                    {'type': 'text_contains', 'target': '.success-message', 'value': 'Registration successful'}
                ]
            
            test_scenarios.append(scenario)
        
        return test_scenarios
    
    def generate_accessibility_tests(self, num_tests: int = 3) -> List[Dict[str, Any]]:
        """Generate accessibility-focused test scenarios."""
        print(f"Generating {num_tests} accessibility test scenarios...")
        
        test_scenarios = []
        for i in range(num_tests):
            scenario = {
                'name': f'accessibility_test_{i+1}',
                'pattern': 'accessibility_tests',
                'priority': 'high',
                'steps': [
                    {'action': 'navigate', 'target': '/search'},
                    {'action': 'wait', 'duration': 2000}
                ],
                'assertions': [
                    {'type': 'accessibility_check'},
                    {'type': 'element_visible', 'target': 'main'},
                    {'type': 'element_visible', 'target': 'nav'}
                ],
                'test_data': {
                    'screen_reader': True,
                    'keyboard_navigation': True,
                    'color_contrast': True
                }
            }
            
            test_scenarios.append(scenario)
        
        return test_scenarios
    
    def generate_comprehensive_test_suite(self) -> str:
        """Generate a comprehensive test suite with all test types."""
        print("Generating comprehensive test suite...")
        
        all_tests = []
        
        # Generate different types of tests
        all_tests.extend(self.generate_login_tests(3))
        all_tests.extend(self.generate_security_tests(3))
        all_tests.extend(self.generate_ecommerce_tests(4))
        all_tests.extend(self.generate_accessibility_tests(2))
        
        # Convert to Cypress tests
        cypress_tests = self.cypress_generator.generate_cypress_tests(all_tests)
        
        # Save to file
        test_file = self.cypress_generator.save_test_file(cypress_tests, "comprehensive_marl_tests.ts")
        
        print(f"✓ Generated {len(all_tests)} test scenarios")
        print(f"✓ Saved to: {test_file}")
        
        return test_file
    
    def generate_custom_tests(self, test_specs: List[Dict[str, Any]]) -> str:
        """Generate tests based on custom specifications."""
        print(f"Generating {len(test_specs)} custom test scenarios...")
        
        test_scenarios = []
        for i, spec in enumerate(test_specs):
            scenario = {
                'name': spec.get('name', f'custom_test_{i+1}'),
                'pattern': spec.get('pattern', 'custom'),
                'priority': spec.get('priority', 'medium'),
                'steps': spec.get('steps', []),
                'assertions': spec.get('assertions', []),
                'test_data': spec.get('test_data', {})
            }
            test_scenarios.append(scenario)
        
        # Convert to Cypress tests
        cypress_tests = self.cypress_generator.generate_cypress_tests(test_scenarios)
        
        # Save to file
        test_file = self.cypress_generator.save_test_file(cypress_tests, "custom_marl_tests.ts")
        
        return test_file


def example_custom_test_specs():
    """Example custom test specifications."""
    return [
        {
            'name': 'api_integration_test',
            'pattern': 'api_testing',
            'priority': 'high',
            'steps': [
                {'action': 'navigate', 'target': '/api/products'},
                {'action': 'wait', 'duration': 3000}
            ],
            'assertions': [
                {'type': 'text_contains', 'target': 'body', 'value': 'products'},
                {'type': 'performance_metric', 'metric': 'loadTime', 'threshold': 2000}
            ]
        },
        {
            'name': 'mobile_responsive_test',
            'pattern': 'responsive_design',
            'priority': 'medium',
            'steps': [
                {'action': 'navigate', 'target': '/search'},
                {'action': 'wait', 'duration': 2000}
            ],
            'assertions': [
                {'type': 'css_property', 'target': 'body', 'property': 'width', 'value': '100%'},
                {'type': 'element_visible', 'target': '.mobile-menu'}
            ],
            'test_data': {
                'viewport': 'mobile',
                'width': 375,
                'height': 667
            }
        }
    ]


def main():
    """Main example usage function."""
    print("=== MARL UI Test Generation Examples ===")
    
    generator = MARLTestGenerator()
    
    # Example 1: Generate specific test types
    print("\n1. Generating specific test types...")
    login_tests = generator.generate_login_tests(2)
    security_tests = generator.generate_security_tests(2)
    ecommerce_tests = generator.generate_ecommerce_tests(2)
    
    print(f"✓ Generated {len(login_tests)} login tests")
    print(f"✓ Generated {len(security_tests)} security tests")
    print(f"✓ Generated {len(ecommerce_tests)} ecommerce tests")
    
    # Example 2: Generate comprehensive test suite
    print("\n2. Generating comprehensive test suite...")
    comprehensive_file = generator.generate_comprehensive_test_suite()
    
    # Example 3: Generate custom tests
    print("\n3. Generating custom tests...")
    custom_specs = example_custom_test_specs()
    custom_file = generator.generate_custom_tests(custom_specs)
    
    # Example 4: Show test data generation
    print("\n4. Generating test data...")
    test_data = generator.cypress_generator.generate_test_data([])
    with open('test_data.json', 'w') as f:
        f.write(test_data)
    print("✓ Test data saved to test_data.json")
    
    # Example 5: Generate README
    print("\n5. Generating documentation...")
    readme_content = generator.cypress_generator.generate_readme()
    with open('README.md', 'w') as f:
        f.write(readme_content)
    print("✓ README saved to README.md")
    
    print("\n=== Examples Complete ===")
    print("Generated files:")
    print(f"- {comprehensive_file}")
    print(f"- {custom_file}")
    print("- test_data.json")
    print("- README.md")
    
    print("\nNext steps:")
    print("1. Start Juice Shop: npm start")
    print("2. Run tests: npx cypress run --spec test/cypress/e2e/*marl_tests.ts")
    print("3. View results in Cypress Dashboard")


if __name__ == "__main__":
    main()

