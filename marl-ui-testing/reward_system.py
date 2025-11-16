"""
Reward System for MARL-based UI Testing
Implements comprehensive reward functions for exploration and test generation agents.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from ui_state_representation import PageState, UIElement
import time
import hashlib


@dataclass
class CoverageMetrics:
    """Tracks coverage metrics for UI elements and pages."""
    pages_visited: set
    elements_discovered: set
    interactions_performed: set
    unique_paths: set
    page_coverage: float = 0.0
    element_coverage: float = 0.0
    interaction_coverage: float = 0.0


@dataclass
class QualityMetrics:
    """Tracks quality metrics for generated tests."""
    test_diversity: float = 0.0
    test_complexity: float = 0.0
    assertion_coverage: float = 0.0
    edge_case_coverage: float = 0.0
    bug_discovery_rate: float = 0.0


class RewardCalculator:
    """
    Calculates rewards for both exploration and test generation agents.
    Implements multiple reward components to guide learning.
    """
    
    def __init__(self):
        self.coverage_metrics = CoverageMetrics(
            pages_visited=set(),
            elements_discovered=set(),
            interactions_performed=set(),
            unique_paths=set()
        )
        self.quality_metrics = QualityMetrics()
        
        # Reward weights
        self.weights = {
            'exploration': 0.3,
            'coverage': 0.25,
            'quality': 0.2,
            'bug_discovery': 0.15,
            'efficiency': 0.1
        }
        
        # Baseline metrics for normalization
        self.baseline_metrics = {
            'total_pages': 50,  # Estimated total pages in Juice Shop
            'total_elements': 1000,  # Estimated total interactable elements
            'total_interactions': 100  # Estimated total interaction types
        }
    
    def calculate_exploration_reward(self, page_state: PageState, 
                                   action: str, success: bool) -> float:
        """Calculate reward for UI exploration actions."""
        reward = 0.0
        
        # Base reward for successful actions
        if success:
            reward += 1.0
        else:
            reward -= 0.5
        
        # Reward for discovering new pages
        page_hash = self._hash_page(page_state)
        if page_hash not in self.coverage_metrics.pages_visited:
            self.coverage_metrics.pages_visited.add(page_hash)
            reward += 2.0  # High reward for new page discovery
        
        # Reward for discovering new elements
        new_elements = 0
        for element in page_state.elements:
            element_hash = self._hash_element(element)
            if element_hash not in self.coverage_metrics.elements_discovered:
                self.coverage_metrics.elements_discovered.add(element_hash)
                new_elements += 1
        
        if new_elements > 0:
            reward += new_elements * 0.5  # Reward for each new element
        
        # Reward for meaningful interactions
        if action in ['click', 'type', 'select'] and success:
            interaction_key = f"{page_hash}_{action}_{element_hash if hasattr(locals(), 'element_hash') else 'unknown'}"
            if interaction_key not in self.coverage_metrics.interactions_performed:
                self.coverage_metrics.interactions_performed.add(interaction_key)
                reward += 1.0
        
        # Penalty for repetitive actions
        if action in ['wait', 'scroll_up', 'scroll_down']:
            reward -= 0.1
        
        return reward
    
    def calculate_coverage_reward(self) -> float:
        """Calculate reward based on overall coverage metrics."""
        # Update coverage percentages
        self.coverage_metrics.page_coverage = (
            len(self.coverage_metrics.pages_visited) / self.baseline_metrics['total_pages']
        )
        self.coverage_metrics.element_coverage = (
            len(self.coverage_metrics.elements_discovered) / self.baseline_metrics['total_elements']
        )
        self.coverage_metrics.interaction_coverage = (
            len(self.coverage_metrics.interactions_performed) / self.baseline_metrics['total_interactions']
        )
        
        # Calculate weighted coverage score
        coverage_score = (
            self.coverage_metrics.page_coverage * 0.4 +
            self.coverage_metrics.element_coverage * 0.4 +
            self.coverage_metrics.interaction_coverage * 0.2
        )
        
        # Reward for coverage improvement
        coverage_reward = coverage_score * 10.0
        
        # Bonus for reaching coverage milestones
        if self.coverage_metrics.page_coverage >= 0.8:
            coverage_reward += 5.0
        if self.coverage_metrics.element_coverage >= 0.7:
            coverage_reward += 5.0
        
        return coverage_reward
    
    def calculate_test_quality_reward(self, test_scenario: Dict[str, Any]) -> float:
        """Calculate reward for test generation quality."""
        quality_reward = 0.0
        
        # Test completeness
        if len(test_scenario.get('steps', [])) >= 3:
            quality_reward += 2.0
        if len(test_scenario.get('assertions', [])) >= 2:
            quality_reward += 2.0
        
        # Test diversity (based on pattern uniqueness)
        pattern = test_scenario.get('pattern', '')
        if pattern in ['login_flow', 'registration_flow', 'checkout_flow']:
            quality_reward += 1.5  # High-value test patterns
        elif pattern in ['security_tests', 'error_handling']:
            quality_reward += 2.0  # Critical test patterns
        
        # Test complexity
        steps = test_scenario.get('steps', [])
        complexity_score = self._calculate_test_complexity(steps)
        quality_reward += complexity_score * 0.5
        
        # Assertion quality
        assertions = test_scenario.get('assertions', [])
        assertion_quality = self._calculate_assertion_quality(assertions)
        quality_reward += assertion_quality * 0.3
        
        # Edge case coverage
        edge_case_score = self._calculate_edge_case_coverage(test_scenario)
        quality_reward += edge_case_score * 0.4
        
        return quality_reward
    
    def calculate_bug_discovery_reward(self, test_results: Dict[str, Any]) -> float:
        """Calculate reward for discovering bugs or issues."""
        bug_reward = 0.0
        
        # Check for various types of issues
        if test_results.get('failed_assertions', 0) > 0:
            bug_reward += 3.0  # High reward for finding assertion failures
        
        if test_results.get('javascript_errors', 0) > 0:
            bug_reward += 2.0  # Reward for finding JS errors
        
        if test_results.get('accessibility_issues', 0) > 0:
            bug_reward += 1.5  # Reward for accessibility issues
        
        if test_results.get('performance_issues', 0) > 0:
            bug_reward += 1.0  # Reward for performance issues
        
        # Security-related discoveries
        if test_results.get('security_vulnerabilities', 0) > 0:
            bug_reward += 5.0  # Very high reward for security issues
        
        return bug_reward
    
    def calculate_efficiency_reward(self, episode_data: Dict[str, Any]) -> float:
        """Calculate reward for efficient exploration and test generation."""
        efficiency_reward = 0.0
        
        # Time efficiency
        episode_duration = episode_data.get('duration', 0)
        if episode_duration < 60:  # Less than 1 minute
            efficiency_reward += 1.0
        elif episode_duration > 300:  # More than 5 minutes
            efficiency_reward -= 0.5
        
        # Action efficiency
        total_actions = episode_data.get('total_actions', 0)
        successful_actions = episode_data.get('successful_actions', 0)
        
        if total_actions > 0:
            success_rate = successful_actions / total_actions
            if success_rate >= 0.8:
                efficiency_reward += 1.0
            elif success_rate < 0.5:
                efficiency_reward -= 0.5
        
        # Coverage efficiency
        coverage_per_action = (
            self.coverage_metrics.page_coverage / max(total_actions, 1)
        )
        if coverage_per_action > 0.01:  # Good coverage per action
            efficiency_reward += 0.5
        
        return efficiency_reward
    
    def calculate_total_reward(self, exploration_reward: float, coverage_reward: float,
                             quality_reward: float, bug_reward: float, 
                             efficiency_reward: float) -> float:
        """Calculate weighted total reward."""
        total_reward = (
            exploration_reward * self.weights['exploration'] +
            coverage_reward * self.weights['coverage'] +
            quality_reward * self.weights['quality'] +
            bug_reward * self.weights['bug_discovery'] +
            efficiency_reward * self.weights['efficiency']
        )
        
        return total_reward
    
    def _hash_page(self, page_state: PageState) -> str:
        """Create a hash for page identification."""
        page_info = f"{page_state.url}_{page_state.title}_{page_state.page_type}"
        return hashlib.md5(page_info.encode()).hexdigest()
    
    def _hash_element(self, element: UIElement) -> str:
        """Create a hash for element identification."""
        element_info = f"{element.tag}_{element.element_type}_{element.xpath}"
        return hashlib.md5(element_info.encode()).hexdigest()
    
    def _calculate_test_complexity(self, steps: List[Dict[str, Any]]) -> float:
        """Calculate complexity score for test steps."""
        complexity = 0.0
        
        for step in steps:
            action = step.get('action', '')
            
            # Base complexity by action type
            if action in ['click', 'type']:
                complexity += 1.0
            elif action in ['navigate', 'wait']:
                complexity += 0.5
            elif action in ['scroll', 'hover']:
                complexity += 0.3
            
            # Additional complexity for conditional logic
            if 'condition' in step:
                complexity += 0.5
            
            # Additional complexity for data-driven tests
            if 'value' in step and step['value'].startswith('${'):
                complexity += 0.3
        
        return min(complexity, 10.0)  # Cap at 10
    
    def _calculate_assertion_quality(self, assertions: List[Dict[str, Any]]) -> float:
        """Calculate quality score for test assertions."""
        quality = 0.0
        
        for assertion in assertions:
            assertion_type = assertion.get('type', '')
            
            # Quality by assertion type
            if assertion_type in ['element_visible', 'text_contains']:
                quality += 1.0
            elif assertion_type in ['url_contains', 'element_count']:
                quality += 1.5
            elif assertion_type in ['attribute_equals', 'css_property']:
                quality += 2.0
            elif assertion_type in ['performance_metric', 'accessibility_check']:
                quality += 2.5
        
        return min(quality, 10.0)  # Cap at 10
    
    def _calculate_edge_case_coverage(self, test_scenario: Dict[str, Any]) -> float:
        """Calculate edge case coverage score."""
        edge_case_score = 0.0
        
        steps = test_scenario.get('steps', [])
        
        # Check for edge case patterns
        for step in steps:
            value = step.get('value', '')
            
            # Empty/null values
            if value in ['', 'null', 'undefined']:
                edge_case_score += 1.0
            
            # Special characters
            if any(char in value for char in ['<', '>', '"', "'", '&']):
                edge_case_score += 1.0
            
            # Long strings
            if len(value) > 100:
                edge_case_score += 1.0
            
            # SQL injection patterns
            if any(pattern in value.lower() for pattern in ['union', 'select', 'drop', 'insert']):
                edge_case_score += 2.0
        
        return min(edge_case_score, 5.0)  # Cap at 5
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        return {
            'coverage': {
                'pages_visited': len(self.coverage_metrics.pages_visited),
                'elements_discovered': len(self.coverage_metrics.elements_discovered),
                'interactions_performed': len(self.coverage_metrics.interactions_performed),
                'page_coverage': self.coverage_metrics.page_coverage,
                'element_coverage': self.coverage_metrics.element_coverage,
                'interaction_coverage': self.coverage_metrics.interaction_coverage
            },
            'quality': {
                'test_diversity': self.quality_metrics.test_diversity,
                'test_complexity': self.quality_metrics.test_complexity,
                'assertion_coverage': self.quality_metrics.assertion_coverage,
                'edge_case_coverage': self.quality_metrics.edge_case_coverage,
                'bug_discovery_rate': self.quality_metrics.bug_discovery_rate
            }
        }
    
    def reset_metrics(self):
        """Reset all metrics for a new training session."""
        self.coverage_metrics = CoverageMetrics(
            pages_visited=set(),
            elements_discovered=set(),
            interactions_performed=set(),
            unique_paths=set()
        )
        self.quality_metrics = QualityMetrics()

