"""
Training Pipeline for MARL-based UI Test Generation
Main training script that coordinates agent learning and evaluation.
"""

import os
import sys
import time
import json
import random
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from marl_agents import MARLSystem, Action
from reward_system import RewardCalculator
from cypress_integration import CypressTestGenerator


class MARLTrainer:
    """
    Main trainer class that orchestrates the MARL training process.
    """

    def __init__(self, config: dict):
        self.config = config
        self.marl_system = MARLSystem(
            state_size=config.get('state_size', 200),
            action_size=config.get('action_size', 20)
        )
        self.reward_calculator = RewardCalculator()
        self.cypress_generator = CypressTestGenerator()

        self.training_history = {
            'episode_rewards': [],
            'coverage_history': [],
            'test_quality_history': [],
            'bug_discovery_history': [],
            'efficiency_history': []
        }

        self.driver = self._setup_driver()

    def _setup_driver(self):
        """Setup Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            return driver
        except Exception as e:
            print(f"Error setting up WebDriver: {e}")
            print("Ensure Chrome + ChromeDriver are installed and ChromeDriver is on PATH.")
            raise

    def train(self, num_episodes: int = 100):
        print(f"Starting MARL training for {num_episodes} episodes...")

        best_reward = float('-inf')
        best_episode = -1

        for episode in range(num_episodes):
            metrics = self._train_episode(episode)
            self._update_training_history(metrics)

            if metrics['total_reward'] > best_reward:
                best_reward = metrics['total_reward']
                best_episode = episode
                self._save_best_model()

            if (episode + 1) % 10 == 0:
                self._log_progress(episode + 1, metrics)

            if (episode + 1) % 50 == 0:
                self._generate_test_suite(episode + 1)

        self._generate_final_test_suite()
        print(f"Training completed. Best reward {best_reward:.2f} at episode {best_episode}.")

    def _train_episode(self, episode: int) -> dict:
        start = time.time()
        self.driver.get("http://localhost:3000")
        self.reward_calculator.reset_metrics()

        episode_data = {
            'total_actions': 0,
            'successful_actions': 0,
            'exploration_reward': 0.0,
            'coverage_reward': 0.0,
            'quality_reward': 0.0,
            'bug_reward': 0.0,
            'efficiency_reward': 0.0,
            'duration': 0.0,
            'total_reward': 0.0
        }

        current_state = self.marl_system._get_current_state(self.driver)

        for step in range(50):
            page_state = self.marl_system._get_page_state(self.driver)
            available_actions = self.marl_system.exploration_agent.get_available_actions(page_state)
            if not available_actions:
                break

            action = self.marl_system.exploration_agent.get_action(current_state, available_actions)
            success = self._execute_action_safely(action)
            episode_data['total_actions'] += 1
            if success:
                episode_data['successful_actions'] += 1

            exploration_reward = self.reward_calculator.calculate_exploration_reward(
                page_state, action.action_type, success
            )
            episode_data['exploration_reward'] += exploration_reward

            next_state = self.marl_system._get_current_state(self.driver)
            self.marl_system.exploration_agent.remember(
                current_state, action, exploration_reward, next_state, False
            )
            current_state = next_state

            time.sleep(0.2)

        episode_data['coverage_reward'] = self.reward_calculator.calculate_coverage_reward()
        episode_data['efficiency_reward'] = self.reward_calculator.calculate_efficiency_reward(episode_data)

        exploration_data = {
            'ui_state': current_state,
            'coverage': self.reward_calculator.get_metrics_summary()['coverage'],
            'quality': self.reward_calculator.get_metrics_summary()['quality']
        }
        test_scenario = self.marl_system.test_generation_agent.generate_test(exploration_data)

        episode_data['quality_reward'] = self.reward_calculator.calculate_test_quality_reward(test_scenario)
        test_results = self._simulate_test_execution(test_scenario)
        episode_data['bug_reward'] = self.reward_calculator.calculate_bug_discovery_reward(test_results)

        episode_data['total_reward'] = self.reward_calculator.calculate_total_reward(
            episode_data['exploration_reward'],
            episode_data['coverage_reward'],
            episode_data['quality_reward'],
            episode_data['bug_reward'],
            episode_data['efficiency_reward']
        )

        episode_data['duration'] = time.time() - start

        if (episode + 1) % 10 == 0:
            self.marl_system.exploration_agent.replay()
            self.marl_system.exploration_agent.update_target_network()

        return episode_data

    def _execute_action_safely(self, action: Action) -> bool:
        try:
            if action.action_type == 'click' and action.target_element:
                el = self.driver.find_element("xpath", action.target_element.xpath)
                el.click()
                return True
            if action.action_type == 'type' and action.target_element:
                el = self.driver.find_element("xpath", action.target_element.xpath)
                el.clear()
                el.send_keys(action.value or '')
                return True
            if action.action_type == 'scroll_up':
                self.driver.execute_script("window.scrollBy(0, -300);")
                return True
            if action.action_type == 'scroll_down':
                self.driver.execute_script("window.scrollBy(0, 300);")
                return True
            if action.action_type == 'wait':
                time.sleep(0.5)
                return True
            if action.action_type == 'navigate_back':
                self.driver.back()
                return True
            if action.action_type == 'refresh':
                self.driver.refresh()
                return True
            return False
        except Exception:
            return False

    def _simulate_test_execution(self, test_scenario: dict) -> dict:
        results = {
            'failed_assertions': 0,
            'javascript_errors': 0,
            'accessibility_issues': 0,
            'performance_issues': 0,
            'security_vulnerabilities': 0
        }
        if random.random() < 0.1:
            key = random.choice(list(results.keys()))
            results[key] = random.randint(1, 3)
        return results

    def _update_training_history(self, m: dict):
        self.training_history['episode_rewards'].append(m['total_reward'])
        self.training_history['coverage_history'].append(m['coverage_reward'])
        self.training_history['test_quality_history'].append(m['quality_reward'])
        self.training_history['bug_discovery_history'].append(m['bug_reward'])
        self.training_history['efficiency_history'].append(m['efficiency_reward'])

    def _log_progress(self, episode: int, m: dict):
        print(
            f"Ep {episode} | R={m['total_reward']:.2f} | Expl={m['exploration_reward']:.2f} | "
            f"Cov={m['coverage_reward']:.2f} | Qual={m['quality_reward']:.2f} | "
            f"Bug={m['bug_reward']:.2f} | Eff={m['efficiency_reward']:.2f} | "
            f"t={m['duration']:.1f}s"
        )

    def _generate_test_suite(self, episode: int):
        print(f"Generating test suite at episode {episode}...")
        scenarios = []
        for _ in range(10):
            scenarios.append(
                self.marl_system.test_generation_agent.generate_test({
                    'ui_state': np.random.random(200),
                    'coverage': self.reward_calculator.get_metrics_summary()['coverage'],
                    'quality': self.reward_calculator.get_metrics_summary()['quality']
                })
            )
        content = self.cypress_generator.generate_cypress_tests(scenarios)
        out = f"test/cypress/e2e/generated_tests_episode_{episode}.spec.ts"
        with open(out, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved generated tests to {out}")

    def _save_best_model(self):
        try:
            import torch
            torch.save({
                'exploration_agent': self.marl_system.exploration_agent.q_network.state_dict(),
                'test_generation_agent_actor': self.marl_system.test_generation_agent.actor.state_dict(),
                'test_generation_agent_critic': self.marl_system.test_generation_agent.critic.state_dict(),
                'training_history': self.training_history
            }, 'best_marl_model.pth')
        except Exception:
            # Torch optional for saving; skip if unavailable
            pass

    def _generate_final_test_suite(self):
        print("Generating final test suite...")
        scenarios = []
        for _ in range(30):
            scenarios.append(
                self.marl_system.test_generation_agent.generate_test({
                    'ui_state': np.random.random(200),
                    'coverage': self.reward_calculator.get_metrics_summary()['coverage'],
                    'quality': self.reward_calculator.get_metrics_summary()['quality']
                })
            )
        content = self.cypress_generator.generate_cypress_tests(scenarios)
        with open('test/cypress/e2e/final_generated_tests.spec.ts', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Saved final test suite to final_generated_tests.ts")

    def cleanup(self):
        if self.driver:
            self.driver.quit()


def main():
    config = {
        'state_size': 200,
        'action_size': 20,
        'learning_rate': 0.001,
        'max_episodes': 100
    }
    trainer = MARLTrainer(config)
    try:
        trainer.train(config['max_episodes'])
    finally:
        trainer.cleanup()


if __name__ == "__main__":
    main()


