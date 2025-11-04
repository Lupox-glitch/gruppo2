import sys
import time
import urllib.request
import urllib.parse
from threading import Thread

# Import the server module to check for syntax errors
try:
    import server
    print("✓ Server module imported successfully")
except Exception as e:
    print(f"✗ Error importing server: {e}")
    sys.exit(1)

# Test that the main components exist
try:
    assert hasattr(server, 'CVHandler'), "CVHandler class not found"
    assert hasattr(server, 'init_database'), "init_database function not found"
    assert hasattr(server, 'main'), "main function not found"
    print("✓ Server components verified")
except AssertionError as e:
    print(f"✗ {e}")
    sys.exit(1)

print("\n✓ All checks passed!")
print("\nTo start the server, run:")
print("  python server.py")
print("\nThen open: http://localhost:8000")
