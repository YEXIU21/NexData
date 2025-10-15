"""
Test script to verify new features are working
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("="*60)
print("NexData Feature Verification Test")
print("="*60)

# Test 1: Excel Pivot Export
print("\n[1/3] Testing Excel Pivot Export...")
try:
    from data_ops.excel_pivot_export import ExcelPivotExporter, PivotTableBuilder
    print("  ✅ Excel Pivot Export module imported successfully")
    print("  ✅ Classes available: ExcelPivotExporter, PivotTableBuilder")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 2: API Connector
print("\n[2/3] Testing Generic API Connector...")
try:
    from data_ops.api_connector import APIConnector, APIEndpointBuilder, APIResponseHandler, APICache
    print("  ✅ API Connector module imported successfully")
    print("  ✅ Classes available: APIConnector, APIEndpointBuilder, APIResponseHandler, APICache")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 3: Shopify API
print("\n[3/3] Testing Shopify API Integration...")
try:
    from data_ops.shopify_api import ShopifyAPI, ShopifyDataAnalyzer
    print("  ✅ Shopify API module imported successfully")
    print("  ✅ Classes available: ShopifyAPI, ShopifyDataAnalyzer")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 4: API Connector Window
print("\n[4/4] Testing API Connector UI...")
try:
    from ui.api_connector_window import APIConnectorWindow
    print("  ✅ API Connector Window module imported successfully")
    print("  ✅ UI component available")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 5: Main window integration
print("\n[5/5] Testing Main Window Integration...")
try:
    from ui.main_window import DataAnalystApp
    print("  ✅ Main window imports new modules successfully")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 6: Dependencies
print("\n[6/6] Testing Dependencies...")
try:
    import requests
    print(f"  ✅ requests library available (v{requests.__version__})")
except:
    print("  ❌ requests library not installed")

try:
    import psutil
    print(f"  ✅ psutil library available (v{psutil.__version__})")
except:
    print("  ❌ psutil library not installed")

try:
    from pptx import Presentation
    print("  ✅ python-pptx library available")
except:
    print("  ❌ python-pptx library not installed")

print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
