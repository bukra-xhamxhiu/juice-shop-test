"""
UI State Representation System for MARL-based UI Testing
Captures DOM structure, element properties, and user context for agent decision making.
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from bs4 import BeautifulSoup


@dataclass
class UIElement:
    """Represents a UI element with its properties and context."""
    tag: str
    text: str
    attributes: Dict[str, str]
    position: Dict[str, int]  # x, y, width, height
    is_visible: bool
    is_enabled: bool
    is_interactable: bool
    element_type: str  # button, input, link, etc.
    xpath: str
    css_selector: str


@dataclass
class PageState:
    """Represents the current state of a web page."""
    url: str
    title: str
    elements: List[UIElement]
    user_context: Dict[str, Any]  # logged in, user role, etc.
    page_type: str  # login, product, basket, etc.
    timestamp: float


class UIStateRepresentation:
    """Converts web page state into numerical representation for MARL agents."""
    
    def __init__(self, max_elements: int = 100):
        self.max_elements = max_elements
        self.element_types = [
            'button', 'input', 'link', 'select', 'textarea', 
            'checkbox', 'radio', 'image', 'div', 'span', 'other'
        ]
        self.attribute_types = [
            'id', 'class', 'type', 'value', 'placeholder', 'href', 'src'
        ]
    
    def extract_elements(self, driver) -> List[UIElement]:
        """Extract UI elements from the current page."""
        elements = []
        
        # Get all interactable elements
        interactable_selectors = [
            'button', 'input', 'select', 'textarea', 'a[href]',
            '[onclick]', '[role="button"]', '[tabindex]'
        ]
        
        for selector in interactable_selectors:
            try:
                web_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in web_elements:
                    if elem.is_displayed():
                        ui_element = self._create_ui_element(elem, driver)
                        elements.append(ui_element)
            except Exception as e:
                print(f"Error extracting elements with selector {selector}: {e}")
        
        return elements[:self.max_elements]
    
    def _create_ui_element(self, web_element: WebElement, driver) -> UIElement:
        """Convert Selenium WebElement to UIElement."""
        try:
            # Get element properties
            tag = web_element.tag_name.lower()
            text = web_element.text.strip()
            
            # Get attributes
            attributes = {}
            for attr in self.attribute_types:
                try:
                    value = web_element.get_attribute(attr)
                    if value:
                        attributes[attr] = value
                except:
                    pass
            
            # Get position
            location = web_element.location
            size = web_element.size
            position = {
                'x': location['x'],
                'y': location['y'],
                'width': size['width'],
                'height': size['height']
            }
            
            # Determine element type
            element_type = self._determine_element_type(web_element, attributes)
            
            # Get selectors
            xpath = self._get_xpath(web_element, driver)
            css_selector = self._get_css_selector(web_element)
            
            return UIElement(
                tag=tag,
                text=text,
                attributes=attributes,
                position=position,
                is_visible=web_element.is_displayed(),
                is_enabled=web_element.is_enabled(),
                is_interactable=self._is_interactable(web_element),
                element_type=element_type,
                xpath=xpath,
                css_selector=css_selector
            )
        except Exception as e:
            print(f"Error creating UI element: {e}")
            return None
    
    def _determine_element_type(self, element: WebElement, attributes: Dict) -> str:
        """Determine the type of UI element."""
        tag = element.tag_name.lower()
        
        if tag == 'button':
            return 'button'
        elif tag == 'input':
            input_type = attributes.get('type', 'text')
            if input_type in ['checkbox', 'radio']:
                return input_type
            else:
                return 'input'
        elif tag == 'select':
            return 'select'
        elif tag == 'textarea':
            return 'textarea'
        elif tag == 'a':
            return 'link'
        elif tag == 'img':
            return 'image'
        elif tag in ['div', 'span']:
            if attributes.get('onclick') or attributes.get('role') == 'button':
                return 'button'
            return tag
        else:
            return 'other'
    
    def _is_interactable(self, element: WebElement) -> bool:
        """Check if element is interactable."""
        try:
            return (element.is_displayed() and 
                   element.is_enabled() and 
                   element.size['width'] > 0 and 
                   element.size['height'] > 0)
        except:
            return False
    
    def _get_xpath(self, element: WebElement, driver) -> str:
        """Get XPath for element."""
        try:
            return driver.execute_script("""
                function getXPath(element) {
                    if (element.id !== '') {
                        return 'id("' + element.id + '")';
                    }
                    if (element === document.body) {
                        return element.tagName;
                    }
                    var ix = 0;
                    var siblings = element.parentNode.childNodes;
                    for (var i = 0; i < siblings.length; i++) {
                        var sibling = siblings[i];
                        if (sibling === element) {
                            return getXPath(element.parentNode) + '/' + element.tagName + '[' + (ix + 1) + ']';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            ix++;
                        }
                    }
                }
                return getXPath(arguments[0]);
            """, element)
        except:
            return ""
    
    def _get_css_selector(self, element: WebElement) -> str:
        """Get CSS selector for element."""
        try:
            # Simple CSS selector generation
            if element.get_attribute('id'):
                return f"#{element.get_attribute('id')}"
            elif element.get_attribute('class'):
                classes = element.get_attribute('class').split()
                return f".{'.'.join(classes)}"
            else:
                return element.tag_name
        except:
            return element.tag_name
    
    def state_to_vector(self, page_state: PageState) -> np.ndarray:
        """Convert page state to numerical vector for neural network input."""
        vector_size = (
            len(self.element_types) * 10 +  # Element type features
            len(self.attribute_types) * 5 +  # Attribute features
            20 +  # Page context features
            10    # User context features
        )
        
        vector = np.zeros(vector_size)
        idx = 0
        
        # Element type distribution
        element_counts = {elem_type: 0 for elem_type in self.element_types}
        for element in page_state.elements:
            if element.element_type in element_counts:
                element_counts[element.element_type] += 1
        
        for elem_type in self.element_types:
            vector[idx:idx+10] = [element_counts[elem_type] / len(page_state.elements)] * 10
            idx += 10
        
        # Attribute presence
        for attr_type in self.attribute_types:
            attr_count = sum(1 for elem in page_state.elements if attr_type in elem.attributes)
            vector[idx:idx+5] = [attr_count / len(page_state.elements)] * 5
            idx += 5
        
        # Page context features
        page_features = [
            len(page_state.elements) / self.max_elements,
            1.0 if 'login' in page_state.page_type else 0.0,
            1.0 if 'product' in page_state.page_type else 0.0,
            1.0 if 'basket' in page_state.page_type else 0.0,
            1.0 if 'admin' in page_state.page_type else 0.0,
            len(page_state.url) / 100.0,  # URL length
            1.0 if page_state.user_context.get('logged_in', False) else 0.0,
            1.0 if page_state.user_context.get('is_admin', False) else 0.0,
            1.0 if page_state.user_context.get('has_items_in_basket', False) else 0.0,
            1.0 if page_state.user_context.get('is_deluxe_user', False) else 0.0,
        ]
        vector[idx:idx+10] = page_features
        idx += 10
        
        # User context features
        user_features = [
            page_state.user_context.get('user_id', 0) / 1000.0,
            page_state.user_context.get('session_duration', 0) / 3600.0,
            page_state.user_context.get('page_views', 0) / 100.0,
            page_state.user_context.get('failed_logins', 0) / 10.0,
            page_state.user_context.get('successful_actions', 0) / 50.0,
        ]
        vector[idx:idx+5] = user_features
        idx += 5
        
        return vector
    
    def get_page_type(self, url: str, title: str, elements: List[UIElement]) -> str:
        """Determine the type of page based on URL, title, and elements."""
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Check for specific page types
        if 'login' in url_lower or 'login' in title_lower:
            return 'login'
        elif 'register' in url_lower or 'register' in title_lower:
            return 'register'
        elif 'basket' in url_lower or 'cart' in url_lower:
            return 'basket'
        elif 'product' in url_lower or any('product' in elem.text.lower() for elem in elements):
            return 'product'
        elif 'admin' in url_lower or 'administration' in title_lower:
            return 'admin'
        elif 'profile' in url_lower or 'account' in url_lower:
            return 'profile'
        elif 'search' in url_lower:
            return 'search'
        else:
            return 'general'

