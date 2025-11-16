"""
Demo script for MARL-based UI Test Generation
Shows how to use the system to generate UI tests for Juice Shop.
"""

import os
import sys
import time
import json
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from marl_agents import MARLSystem, Action
from reward_system import RewardCalculator
from ui_state_representation import UIStateRepresentation
from cypress_integration import CypressTestGenerator


class MARLDemo:
    """
    Demo class that showcases MARL-based UI test generation.
    """
    
    def __init__(self):
        self.marl_system = MARLSystem(state_size=200, action_size=20)
        self.reward_calculator = RewardCalculator()
        self.cypress_generator = CypressTestGenerator()
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome WebDriver for demo."""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✓ WebDriver setup successful")
            return True
        except Exception as e:
            print(f"✗ WebDriver setup failed: {e}")
            print("Make sure ChromeDriver is installed and in PATH")
            return False
    
    def demo_ui_exploration(self):
        """Demo UI exploration capabilities."""
        print("\n=== UI Exploration Demo ===")
        
        if not self.driver:
            print("WebDriver not available")
            return
        
        try:
            # Navigate to Juice Shop
            print("Navigating to Juice Shop...")
            self.driver.get("http://localhost:3000")
            time.sleep(2)
            
            # Get initial page state
            page_state = self.marl_system._get_page_state(self.driver)
            print(f"✓ Page loaded: {page_state.title}")
            print(f"✓ Page type: {page_state.page_type}")
            print(f"✓ Elements found: {len(page_state.elements)}")
            
            # Show discovered elements
            print("\nDiscovered UI elements:")
            for i, element in enumerate(page_state.elements[:10]):  # Show first 10
                print(f"  {i+1}. {element.element_type}: {element.tag} - {element.text[:50]}")
            
            if len(page_state.elements) > 10:
                print(f"  ... and {len(page_state.elements) - 10} more elements")
            
            # Demo exploration actions
            print("\nDemo exploration actions:")
            available_actions = self.marl_system.exploration_agent.get_available_actions(page_state)
            print(f"✓ Available actions: {len(available_actions)}")
            
            # Try a few actions
            for i, action in enumerate(available_actions[:3]):
                print(f"  {i+1}. {action.action_type}")
                if action.target_element:
                    print(f"     Target: {action.target_element.element_type}")
            
        except Exception as e:
            print(f"✗ Exploration demo failed: {e}")
    
    def demo_test_generation(self):
        """Demo test generation capabilities."""
        print("\n=== Test Generation Demo ===")
        
        # Create sample exploration data
        exploration_data = {
            'ui_state': np.random.random(200),
            'coverage': {
                'page_coverage': 0.3,
                'element_coverage': 0.4,
                'interaction_coverage': 0.2
            },
            'quality': {
                'test_diversity': 0.6,
                'test_complexity': 0.7,
                'assertion_coverage': 0.5
            }
        }
        
        # Generate test scenarios
        print("Generating test scenarios...")
        test_scenarios = []
        
        for i in range(5):
            scenario = self.marl_system.test_generation_agent.generate_test(exploration_data)
            test_scenarios.append(scenario)
            print(f"✓ Generated test: {scenario['name']} ({scenario['pattern']})")
        
        # Show test details
        print("\nTest scenario details:")
        for i, scenario in enumerate(test_scenarios):
            print(f"\n{i+1}. {scenario['name']}")
            print(f"   Pattern: {scenario['pattern']}")
            print(f"   Steps: {len(scenario['steps'])}")
            print(f"   Assertions: {len(scenario['assertions'])}")
            
            # Show first few steps
            if scenario['steps']:
                print("   Sample steps:")
                for j, step in enumerate(scenario['steps'][:3]):
                    print(f"     {j+1}. {step['action']} - {step.get('target', 'N/A')}")
        
        return test_scenarios
    
    def demo_cypress_integration(self, test_scenarios):
        """Demo Cypress test generation."""
        print("\n=== Cypress Integration Demo ===")
        
        # Generate Cypress tests
        print("Converting to Cypress tests...")
        cypress_tests = self.cypress_generator.generate_cypress_tests(test_scenarios)
        
        # Save test file
        test_file = self.cypress_generator.save_test_file(cypress_tests, "demo_marl_tests.ts")
        print(f"✓ Cypress tests saved to: {test_file}")
        
        # Show sample of generated code
        print("\nSample generated Cypress code:")
        lines = cypress_tests.split('\n')
        for i, line in enumerate(lines[:20]):  # Show first 20 lines
            print(f"{i+1:2d}: {line}")
        
        if len(lines) > 20:
            print(f"... and {len(lines) - 20} more lines")
        
        return test_file
    
    def demo_reward_system(self):
        """Demo reward system calculations."""
        print("\n=== Reward System Demo ===")
        
        # Simulate some exploration data
        page_state = self.marl_system._get_page_state(self.driver) if self.driver else None
        
        if page_state:
            # Calculate exploration reward
            exploration_reward = self.reward_calculator.calculate_exploration_reward(
                page_state, 'click', True
            )
            print(f"✓ Exploration reward: {exploration_reward:.2f}")
            
            # Calculate coverage reward
            coverage_reward = self.reward_calculator.calculate_coverage_reward()
            print(f"✓ Coverage reward: {coverage_reward:.2f}")
            
            # Show metrics
            metrics = self.reward_calculator.get_metrics_summary()
            print(f"✓ Pages visited: {metrics['coverage']['pages_visited']}")
            print(f"✓ Elements discovered: {metrics['coverage']['elements_discovered']}")
            print(f"✓ Interactions performed: {metrics['coverage']['interactions_performed']}")
        
        # Demo test quality evaluation
        sample_test = {
            'name': 'demo_test',
            'pattern': 'login_flow',
            'steps': [
                {'action': 'navigate', 'target': '/login'},
                {'action': 'type', 'target': 'email', 'value': 'test@example.com'},
                {'action': 'type', 'target': 'password', 'value': 'password123'},
                {'action': 'click', 'target': 'login_button'}
            ],
            'assertions': [
                {'type': 'url_contains', 'value': '/search'},
                {'type': 'element_visible', 'target': 'user_menu'}
            ]
        }
        
        quality_reward = self.reward_calculator.calculate_test_quality_reward(sample_test)
        print(f"✓ Test quality reward: {quality_reward:.2f}")
    
    def demo_training_simulation(self):
        """Demo a simplified training simulation."""
        print("\n=== Training Simulation Demo ===")
        
        if not self.driver:
            print("WebDriver not available for training simulation")
            return
        
        print("Running 5 training episodes...")
        
        for episode in range(5):
            print(f"\nEpisode {episode + 1}:")
            
            # Reset to home page
            self.driver.get("http://localhost:3000")
            time.sleep(1)
            
            # Get current state
            current_state = self.marl_system._get_current_state(self.driver)
            page_state = self.marl_system._get_page_state(self.driver)
            
            # Get available actions
            available_actions = self.marl_system.exploration_agent.get_available_actions(page_state)
            
            if available_actions:
                # Select and execute action
                action = self.marl_system.exploration_agent.get_action(current_state, available_actions)
                print(f"  Action: {action.action_type}")
                
                # Execute action (simplified)
                try:
                    if action.action_type == 'click' and action.target_element:
                        element = self.driver.find_element("xpath", action.target_element.xpath)
                        element.click()
                        print("  ✓ Action executed successfully")
                    elif action.action_type == 'scroll_down':
                        self.driver.execute_script("window.scrollBy(0, 300);")
                        print("  ✓ Scrolled down")
                    else:
                        print("  - Action skipped (demo mode)")
                except Exception as e:
                    print(f"  ✗ Action failed: {e}")
                
                # Calculate reward
                reward = self.reward_calculator.calculate_exploration_reward(
                    page_state, action.action_type, True
                )
                print(f"  Reward: {reward:.2f}")
            
            time.sleep(0.5)
        
        print("\n✓ Training simulation completed")
    
    def run_full_demo(self):
        """Run the complete demo."""
        print("=== MARL UI Test Generation Demo ===")
        print("This demo showcases Multi-Agent Reinforcement Learning for UI test generation")
        
        # Setup
        if not self.setup_driver():
            print("Demo cannot continue without WebDriver")
            return
        
        try:
            # Run demo components
            self.demo_ui_exploration()
            test_scenarios = self.demo_test_generation()
            test_file = self.demo_cypress_integration(test_scenarios)
            self.demo_reward_system()
            self.demo_training_simulation()
            
            print("\n=== Demo Summary ===")
            print("✓ UI exploration demonstrated")
            print("✓ Test generation demonstrated")
            print(f"✓ Cypress integration demonstrated ({test_file})")
            print("✓ Reward system demonstrated")
            print("✓ Training simulation demonstrated")
            
            print("\nNext steps:")
            print("1. Start Juice Shop: npm start")
            print("2. Run generated tests: npx cypress run --spec test/cypress/e2e/demo_marl_tests.ts")
            print("3. Train full model: python train_marl.py")
            
        except Exception as e:
            print(f"Demo failed: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
                print("✓ WebDriver cleaned up")


def main():
    """Main demo function."""
    demo = MARLDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main()

