"""
Generic REST API Connector
Flexible connector for various REST APIs with authentication and error handling

SEPARATION OF CONCERNS: API connection and data fetching only
"""

import requests
import pandas as pd
import json
from datetime import datetime
import time


class APIConnector:
    """Generic REST API connector with authentication and error handling"""
    
    def __init__(self, base_url, api_key=None, headers=None):
        """
        Initialize API connector
        
        Parameters:
        -----------
        base_url : str
            Base URL for the API
        api_key : str
            API key for Bearer token authentication (optional)
        headers : dict
            Custom headers (optional) - if provided with auth headers, api_key is ignored
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        
        # Start with provided headers or empty dict
        if headers:
            self.headers = headers.copy()  # Use provided headers
        else:
            self.headers = {}
        
        # Only add Bearer auth if api_key provided AND no conflicting auth header exists
        # Check for Shopify, standard Bearer, or other auth headers
        has_auth = any(key in self.headers for key in ['Authorization', 'X-Shopify-Access-Token'])
        if api_key and not has_auth:
            self.headers['Authorization'] = f'Bearer {api_key}'
        
        # Default headers (only if not already set)
        self.headers.setdefault('Content-Type', 'application/json')
        self.headers.setdefault('Accept', 'application/json')
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # seconds between requests
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        
        self.last_request_time = time.time()
    
    def get(self, endpoint, params=None, timeout=30):
        """
        Make GET request
        
        Parameters:
        -----------
        endpoint : str
            API endpoint (will be appended to base_url)
        params : dict
            Query parameters
        timeout : int
            Request timeout in seconds
        
        Returns:
        --------
        success : bool
        data : dict or None
        error : str or None
        """
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.get(url, params=params, timeout=timeout)
            
            # Check for errors
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            return True, data, None
        
        except requests.exceptions.HTTPError as e:
            return False, None, f"HTTP Error: {e.response.status_code} - {e.response.text}"
        except requests.exceptions.ConnectionError:
            return False, None, "Connection Error: Unable to connect to API"
        except requests.exceptions.Timeout:
            return False, None, f"Timeout Error: Request took longer than {timeout} seconds"
        except requests.exceptions.RequestException as e:
            return False, None, f"Request Error: {str(e)}"
        except json.JSONDecodeError:
            return False, None, "JSON Decode Error: Invalid JSON response"
        except Exception as e:
            return False, None, f"Unexpected Error: {str(e)}"
    
    def post(self, endpoint, data=None, json_data=None, timeout=30):
        """
        Make POST request
        
        Parameters:
        -----------
        endpoint : str
            API endpoint
        data : dict
            Form data
        json_data : dict
            JSON data
        timeout : int
            Request timeout
        
        Returns:
        --------
        success : bool
        data : dict or None
        error : str or None
        """
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.post(url, data=data, json=json_data, timeout=timeout)
            
            response.raise_for_status()
            
            data = response.json()
            return True, data, None
        
        except requests.exceptions.RequestException as e:
            return False, None, f"Request Error: {str(e)}"
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def fetch_paginated(self, endpoint, params=None, max_pages=None, page_param='page', per_page_param='per_page', per_page=100):
        """
        Fetch paginated data from API
        Supports both traditional page-based and Shopify cursor-based pagination
        
        Parameters:
        -----------
        endpoint : str
            API endpoint
        params : dict
            Base query parameters
        max_pages : int
            Maximum number of pages to fetch (None = all)
        page_param : str
            Name of the page parameter (ignored for Shopify)
        per_page_param : str
            Name of the per_page parameter
        per_page : int
            Items per page
        
        Returns:
        --------
        success : bool
        all_data : list
        error : str or None
        """
        try:
            all_data = []
            params = params or {}
            
            # Check if this is Shopify (uses cursor-based pagination)
            is_shopify = 'shopify' in self.base_url.lower()
            
            if is_shopify:
                # Shopify cursor-based pagination using Link headers
                page_info = None
                page_count = 0
                
                while True:
                    # Set limit parameter
                    request_params = params.copy()
                    request_params[per_page_param] = per_page
                    
                    # Add page_info for subsequent pages
                    if page_info:
                        request_params['page_info'] = page_info
                    
                    # Make request
                    url = f"{self.base_url}/{endpoint}"
                    response = self.session.get(url, params=request_params, timeout=30)
                    
                    if response.status_code != 200:
                        error_text = response.text if response.text else f"HTTP {response.status_code}"
                        return False, all_data, f"HTTP Error {response.status_code} - {error_text}"
                    
                    data = response.json()
                    
                    # Extract items from response
                    if isinstance(data, dict):
                        # Shopify wraps data in resource name (e.g., {'orders': [...]})  
                        items = None
                        for key in data.keys():
                            if isinstance(data[key], list):
                                items = data[key]
                                break
                        if items is None:
                            items = []
                    elif isinstance(data, list):
                        items = data
                    else:
                        items = []
                    
                    if not items:
                        break
                    
                    all_data.extend(items)
                    page_count += 1
                    
                    # Check max pages limit
                    if max_pages and page_count >= max_pages:
                        break
                    
                    # Extract next page_info from Link header
                    link_header = response.headers.get('Link', '')
                    page_info = self._extract_page_info(link_header, 'next')
                    
                    # No more pages
                    if not page_info:
                        break
                
                return True, all_data, None
            
            else:
                # Traditional page-based pagination for non-Shopify APIs
                page = 1
                
                while True:
                    # Add pagination parameters
                    params[page_param] = page
                    params[per_page_param] = per_page
                    
                    # Fetch page
                    success, data, error = self.get(endpoint, params)
                    
                    if not success:
                        return False, all_data, error
                    
                    # Handle different response formats
                    if isinstance(data, list):
                        items = data
                    elif isinstance(data, dict):
                        items = data.get('data', data.get('results', data.get('items', [])))
                    else:
                        items = []
                    
                    if not items:
                        break
                    
                    all_data.extend(items)
                    
                    # Check if we should continue
                    if max_pages and page >= max_pages:
                        break
                    
                    if len(items) < per_page:
                        break
                    
                    page += 1
                
                return True, all_data, None
        
        except Exception as e:
            return False, all_data, f"Pagination Error: {str(e)}"
    
    def _extract_page_info(self, link_header, rel='next'):
        """
        Extract page_info parameter from Link header for cursor-based pagination
        
        Parameters:
        -----------
        link_header : str
            Link header value from API response
        rel : str
            Relationship type to extract ('next' or 'previous')
        
        Returns:
        --------
        page_info : str or None
            Extracted page_info parameter or None if not found
        """
        import re
        from urllib.parse import urlparse, parse_qs
        
        if not link_header:
            return None
        
        # Parse Link header (format: <url>; rel="next", <url>; rel="previous")
        links = link_header.split(',')
        
        for link in links:
            # Check if this is the requested relationship
            if f'rel="{rel}"' in link or f"rel='{rel}'" in link:
                # Extract URL from <url>
                url_match = re.search(r'<([^>]+)>', link)
                if url_match:
                    url = url_match.group(1)
                    # Parse URL and extract page_info parameter
                    parsed = urlparse(url)
                    query_params = parse_qs(parsed.query)
                    page_info = query_params.get('page_info', [None])[0]
                    return page_info
        
        return None
    
    def to_dataframe(self, data):
        """
        Convert API response to pandas DataFrame
        
        Parameters:
        -----------
        data : list or dict
            API response data
        
        Returns:
        --------
        df : DataFrame or None
        error : str or None
        """
        try:
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # Try to extract data array
                if 'data' in data:
                    df = pd.DataFrame(data['data'])
                elif 'results' in data:
                    df = pd.DataFrame(data['results'])
                elif 'items' in data:
                    df = pd.DataFrame(data['items'])
                else:
                    # Convert single record to DataFrame
                    df = pd.DataFrame([data])
            else:
                return None, "Invalid data format for DataFrame conversion"
            
            return df, None
        
        except Exception as e:
            return None, f"DataFrame Conversion Error: {str(e)}"
    
    def save_response(self, data, file_path):
        """
        Save API response to JSON file
        
        Parameters:
        -----------
        data : dict or list
            API response data
        file_path : str
            Output file path
        
        Returns:
        --------
        success : bool
        error : str or None
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True, None
        except Exception as e:
            return False, f"File Save Error: {str(e)}"


class APIEndpointBuilder:
    """Helper class to build API endpoints with parameters"""
    
    @staticmethod
    def build_query_string(params):
        """Build URL query string from parameters"""
        if not params:
            return ""
        
        query_parts = []
        for key, value in params.items():
            if value is not None:
                if isinstance(value, (list, tuple)):
                    for item in value:
                        query_parts.append(f"{key}={item}")
                else:
                    query_parts.append(f"{key}={value}")
        
        return "?" + "&".join(query_parts) if query_parts else ""
    
    @staticmethod
    def build_filter_params(filters):
        """Build filter parameters for API queries"""
        params = {}
        
        for key, value in filters.items():
            if value:
                params[key] = value
        
        return params


class APIResponseHandler:
    """Handle and parse different API response formats"""
    
    @staticmethod
    def extract_data(response, data_path=None):
        """
        Extract data from nested response
        
        Parameters:
        -----------
        response : dict
            API response
        data_path : str
            Dot-separated path to data (e.g., 'data.items.records')
        
        Returns:
        --------
        extracted_data : any
        """
        if data_path is None:
            return response
        
        current = response
        for key in data_path.split('.'):
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and key.isdigit():
                current = current[int(key)]
            else:
                return None
        
        return current
    
    @staticmethod
    def flatten_nested_data(data, separator='_'):
        """Flatten nested dictionaries for DataFrame conversion"""
        if not isinstance(data, (dict, list)):
            return data
        
        if isinstance(data, list):
            return [APIResponseHandler.flatten_nested_data(item, separator) for item in data]
        
        flat_dict = {}
        
        def flatten(obj, parent_key=''):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{parent_key}{separator}{key}" if parent_key else key
                    flatten(value, new_key)
            elif isinstance(obj, list):
                flat_dict[parent_key] = json.dumps(obj)
            else:
                flat_dict[parent_key] = obj
        
        flatten(data)
        return flat_dict


class APICache:
    """Simple in-memory cache for API responses"""
    
    def __init__(self, ttl=300):
        """
        Initialize cache
        
        Parameters:
        -----------
        ttl : int
            Time to live in seconds (default 5 minutes)
        """
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key):
        """Get cached value if not expired"""
        if key in self.cache:
            timestamp, value = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        """Set cached value with timestamp"""
        self.cache[key] = (time.time(), value)
    
    def clear(self):
        """Clear all cached values"""
        self.cache.clear()
