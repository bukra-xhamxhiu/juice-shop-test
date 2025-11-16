"""
Multi-Agent Reinforcement Learning System for UI Test Generation
Implements two agents: UI Exploration Agent and Test Generation Agent
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from collections import deque
import random
from ui_state_representation import PageState, UIElement, UIStateRepresentation


@dataclass
class Action:
    """Represents an action that can be taken by an agent."""
    action_type: str
    target_element: Optional[UIElement] = None
    value: Optional[str] = None
    parameters: Dict[str, Any] = None


@dataclass
class Reward:
    """Represents a reward signal for agent learning."""
    exploration_reward: float = 0.0
    coverage_reward: float = 0.0
    quality_reward: float = 0.0
    bug_discovery_reward: float = 0.0
    total_reward: float = 0.0


class ExplorationAgent:
    """
    Agent responsible for exploring the UI and discovering elements.
    Uses Deep Q-Network (DQN) for learning optimal exploration strategies.
    """
    
    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.memory = deque(maxlen=10000)
        self.batch_size = 32
        
        # Neural network for Q-value estimation
        self.q_network = self._build_network()
        self.target_network = self._build_network()
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        
        # Action space for UI exploration
        self.action_types = [
            'click', 'type', 'scroll_up', 'scroll_down', 'wait', 
            'navigate_back', 'navigate_forward', 'refresh', 'hover'
        ]
        
        # Exploration history
        self.visited_pages = set()
        self.discovered_elements = set()
        self.interaction_history = []
    
    def _build_network(self) -> nn.Module:
        """Build the neural network for Q-value estimation."""
        return nn.Sequential(
            nn.Linear(self.state_size, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, self.action_size)
        )
    
    def get_action(self, state: np.ndarray, available_actions: List[Action]) -> Action:
        """Select an action based on current state using epsilon-greedy policy."""
        if np.random.random() <= self.epsilon:
            # Random exploration
            return random.choice(available_actions)
        else:
            # Exploitation using neural network
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.q_network(state_tensor)
            
            # Map Q-values to available actions
            action_scores = []
            for action in available_actions:
                action_idx = self.action_types.index(action.action_type)
                action_scores.append(q_values[0][action_idx].item())
            
            best_action_idx = np.argmax(action_scores)
            return available_actions[best_action_idx]
    
    def remember(self, state: np.ndarray, action: Action, reward: float, 
                next_state: np.ndarray, done: bool):
        """Store experience in replay memory."""
        self.memory.append((state, action, reward, next_state, done))
    
    def replay(self):
        """Train the neural network on a batch of experiences."""
        if len(self.memory) < self.batch_size:
            return
        
        batch = random.sample(self.memory, self.batch_size)
        states = torch.FloatTensor([e[0] for e in batch])
        actions = [e[1] for e in batch]
        rewards = torch.FloatTensor([e[2] for e in batch])
        next_states = torch.FloatTensor([e[3] for e in batch])
        dones = torch.BoolTensor([e[4] for e in batch])
        
        current_q_values = self.q_network(states)
        next_q_values = self.target_network(next_states)
        
        target_q_values = rewards + (0.95 * torch.max(next_q_values, dim=1)[0] * ~dones)
        
        # Calculate loss
        action_indices = torch.LongTensor([self.action_types.index(a.action_type) for a in actions])
        current_q_values = current_q_values.gather(1, action_indices.unsqueeze(1))
        
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)
        
        # Backpropagation
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def update_target_network(self):
        """Update target network with current network weights."""
        self.target_network.load_state_dict(self.q_network.state_dict())
    
    def get_available_actions(self, page_state: PageState) -> List[Action]:
        """Get list of available actions based on current page state."""
        actions = []
        
        # Add click actions for interactable elements
        for element in page_state.elements:
            if element.is_interactable:
                if element.element_type == 'button':
                    actions.append(Action('click', element))
                elif element.element_type == 'input':
                    actions.append(Action('type', element, 'test_input'))
                elif element.element_type == 'link':
                    actions.append(Action('click', element))
        
        # Add navigation actions
        actions.extend([
            Action('scroll_up'),
            Action('scroll_down'),
            Action('wait'),
            Action('navigate_back'),
            Action('refresh')
        ])
        
        return actions


class TestGenerationAgent:
    """
    Agent responsible for generating test scenarios based on discovered UI patterns.
    Uses Actor-Critic method for learning test generation policies.
    """
    
    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        
        # Actor network (policy)
        self.actor = self._build_actor()
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=learning_rate)
        
        # Critic network (value function)
        self.critic = self._build_critic()
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=learning_rate)
        
        # Test generation patterns
        self.test_patterns = [
            'login_flow', 'registration_flow', 'product_search', 'add_to_basket',
            'checkout_flow', 'user_profile', 'admin_functions', 'error_handling',
            'security_tests', 'accessibility_tests'
        ]
        
        # Generated tests storage
        self.generated_tests = []
        self.test_quality_scores = []
    
    def _build_actor(self) -> nn.Module:
        """Build actor network for policy learning."""
        return nn.Sequential(
            nn.Linear(self.state_size, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, self.action_size),
            nn.Softmax(dim=-1)
        )
    
    def _build_critic(self) -> nn.Module:
        """Build critic network for value estimation."""
        return nn.Sequential(
            nn.Linear(self.state_size, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
    
    def generate_test(self, exploration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a test scenario based on exploration data."""
        state = self._prepare_state(exploration_data)
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        # Get action probabilities from actor
        action_probs = self.actor(state_tensor)
        action_dist = torch.distributions.Categorical(action_probs)
        action = action_dist.sample()
        
        # Generate test based on selected action
        test_scenario = self._create_test_scenario(action.item(), exploration_data)
        
        return test_scenario
    
    def _prepare_state(self, exploration_data: Dict[str, Any]) -> np.ndarray:
        """Prepare state vector from exploration data."""
        # Combine UI state, exploration history, and test patterns
        ui_state = exploration_data.get('ui_state', np.zeros(100))
        coverage_data = exploration_data.get('coverage', {})
        quality_metrics = exploration_data.get('quality', {})
        
        # Create comprehensive state vector
        state_vector = np.concatenate([
            ui_state,
            [coverage_data.get('page_coverage', 0.0)],
            [coverage_data.get('element_coverage', 0.0)],
            [quality_metrics.get('test_diversity', 0.0)],
            [quality_metrics.get('bug_discovery_rate', 0.0)],
        ])
        
        # Pad or truncate to fixed size
        if len(state_vector) < self.state_size:
            state_vector = np.pad(state_vector, (0, self.state_size - len(state_vector)))
        else:
            state_vector = state_vector[:self.state_size]
        
        return state_vector
    
    def _create_test_scenario(self, action: int, exploration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a test scenario based on the selected action."""
        pattern = self.test_patterns[action % len(self.test_patterns)]
        
        test_scenario = {
            'name': f"marl_generated_{pattern}_{len(self.generated_tests)}",
            'pattern': pattern,
            'steps': [],
            'assertions': [],
            'test_data': {},
            'expected_outcome': '',
            'priority': 'medium'
        }
        
        # Generate test steps based on pattern
        if pattern == 'login_flow':
            test_scenario['steps'] = [
                {'action': 'navigate', 'target': '/login'},
                {'action': 'type', 'target': 'email', 'value': 'test@example.com'},
                {'action': 'type', 'target': 'password', 'value': 'password123'},
                {'action': 'click', 'target': 'login_button'}
            ]
            test_scenario['assertions'] = [
                {'type': 'url_contains', 'value': '/search'},
                {'type': 'element_visible', 'target': 'user_menu'}
            ]
        
        elif pattern == 'product_search':
            test_scenario['steps'] = [
                {'action': 'navigate', 'target': '/search'},
                {'action': 'type', 'target': 'search_input', 'value': 'apple'},
                {'action': 'click', 'target': 'search_button'},
                {'action': 'wait', 'duration': 2}
            ]
            test_scenario['assertions'] = [
                {'type': 'element_count', 'target': '.product-card', 'min': 1},
                {'type': 'text_contains', 'target': '.search-results', 'value': 'apple'}
            ]
        
        elif pattern == 'add_to_basket':
            test_scenario['steps'] = [
                {'action': 'navigate', 'target': '/search'},
                {'action': 'click', 'target': '.product-card:first-child'},
                {'action': 'click', 'target': '.add-to-basket-button'},
                {'action': 'click', 'target': '.basket-button'}
            ]
            test_scenario['assertions'] = [
                {'type': 'element_visible', 'target': '.basket-item'},
                {'type': 'text_contains', 'target': '.basket-count', 'value': '1'}
            ]
        
        # Add more patterns as needed...
        
        return test_scenario
    
    def update_policy(self, states: List[np.ndarray], actions: List[int], 
                     rewards: List[float], next_states: List[np.ndarray]):
        """Update actor-critic networks using collected experiences."""
        states_tensor = torch.FloatTensor(states)
        actions_tensor = torch.LongTensor(actions)
        rewards_tensor = torch.FloatTensor(rewards)
        next_states_tensor = torch.FloatTensor(next_states)
        
        # Update critic
        values = self.critic(states_tensor).squeeze()
        next_values = self.critic(next_states_tensor).squeeze()
        target_values = rewards_tensor + 0.95 * next_values
        
        critic_loss = nn.MSELoss()(values, target_values.detach())
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()
        
        # Update actor
        action_probs = self.actor(states_tensor)
        action_dist = torch.distributions.Categorical(action_probs)
        log_probs = action_dist.log_prob(actions_tensor)
        
        advantages = target_values - values
        actor_loss = -(log_probs * advantages.detach()).mean()
        
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()


class MARLSystem:
    """
    Main MARL system that coordinates the two agents and manages the learning process.
    """
    
    def __init__(self, state_size: int = 200, action_size: int = 20):
        self.state_representation = UIStateRepresentation()
        self.exploration_agent = ExplorationAgent(state_size, action_size)
        self.test_generation_agent = TestGenerationAgent(state_size, action_size)
        
        # Training parameters
        self.episode_count = 0
        self.max_episodes = 1000
        self.update_frequency = 10
        
        # Metrics tracking
        self.episode_rewards = []
        self.coverage_history = []
        self.test_quality_history = []
    
    def train_episode(self, driver) -> Dict[str, float]:
        """Train both agents for one episode."""
        self.episode_count += 1
        
        # Start exploration
        current_state = self._get_initial_state(driver)
        episode_reward = 0.0
        exploration_data = {
            'ui_state': current_state,
            'coverage': {'page_coverage': 0.0, 'element_coverage': 0.0},
            'quality': {'test_diversity': 0.0, 'bug_discovery_rate': 0.0}
        }
        
        # Exploration phase
        for step in range(50):  # Max 50 steps per episode
            page_state = self._get_page_state(driver)
            available_actions = self.exploration_agent.get_available_actions(page_state)
            
            if not available_actions:
                break
            
            action = self.exploration_agent.get_action(current_state, available_actions)
            reward = self._execute_action(driver, action)
            
            next_state = self._get_current_state(driver)
            done = self._is_episode_done(driver, step)
            
            self.exploration_agent.remember(current_state, action, reward, next_state, done)
            episode_reward += reward
            
            current_state = next_state
            
            if done:
                break
        
        # Test generation phase
        test_scenario = self.test_generation_agent.generate_test(exploration_data)
        test_quality = self._evaluate_test_quality(test_scenario)
        
        # Update agents
        if self.episode_count % self.update_frequency == 0:
            self.exploration_agent.replay()
            self.exploration_agent.update_target_network()
        
        # Store metrics
        self.episode_rewards.append(episode_reward)
        self.test_quality_history.append(test_quality)
        
        return {
            'episode_reward': episode_reward,
            'test_quality': test_quality,
            'coverage': exploration_data['coverage']['page_coverage']
        }
    
    def _get_initial_state(self, driver) -> np.ndarray:
        """Get initial state of the application."""
        driver.get("http://localhost:3000")
        return self._get_current_state(driver)
    
    def _get_current_state(self, driver) -> np.ndarray:
        """Get current state representation."""
        page_state = self._get_page_state(driver)
        return self.state_representation.state_to_vector(page_state)
    
    def _get_page_state(self, driver) -> PageState:
        """Get current page state from driver."""
        elements = self.state_representation.extract_elements(driver)
        page_type = self.state_representation.get_page_type(
            driver.current_url, driver.title, elements
        )
        
        return PageState(
            url=driver.current_url,
            title=driver.title,
            elements=elements,
            user_context={},  # Will be populated based on application state
            page_type=page_type,
            timestamp=0.0
        )
    
    def _execute_action(self, driver, action: Action) -> float:
        """Execute action and return reward."""
        try:
            if action.action_type == 'click' and action.target_element:
                element = driver.find_element("xpath", action.target_element.xpath)
                element.click()
                return 1.0  # Successful click reward
            
            elif action.action_type == 'type' and action.target_element:
                element = driver.find_element("xpath", action.target_element.xpath)
                element.clear()
                element.send_keys(action.value)
                return 0.5  # Successful type reward
            
            elif action.action_type == 'scroll_up':
                driver.execute_script("window.scrollBy(0, -300);")
                return 0.1
            
            elif action.action_type == 'scroll_down':
                driver.execute_script("window.scrollBy(0, 300);")
                return 0.1
            
            elif action.action_type == 'wait':
                import time
                time.sleep(1)
                return 0.0
            
            else:
                return -0.1  # Invalid action penalty
                
        except Exception as e:
            return -0.5  # Action failed penalty
    
    def _is_episode_done(self, driver, step: int) -> bool:
        """Check if episode should end."""
        return step >= 50 or "error" in driver.current_url.lower()
    
    def _evaluate_test_quality(self, test_scenario: Dict[str, Any]) -> float:
        """Evaluate the quality of a generated test scenario."""
        quality_score = 0.0
        
        # Check test completeness
        if len(test_scenario['steps']) > 0:
            quality_score += 0.3
        
        if len(test_scenario['assertions']) > 0:
            quality_score += 0.3
        
        # Check test diversity
        if test_scenario['pattern'] not in [t.get('pattern') for t in self.test_generation_agent.generated_tests]:
            quality_score += 0.2
        
        # Check test complexity
        if len(test_scenario['steps']) >= 3:
            quality_score += 0.2
        
        return quality_score

