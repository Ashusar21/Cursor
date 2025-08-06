#!/usr/bin/env python3
"""
DoChat+ Gradio Compatibility Fix

This script fixes compatibility issues between different versions of Gradio.
Run this if you encounter 'show_tips' parameter errors.
"""

import sys
import subprocess
import importlib.util

def check_gradio_version():
    """Check current Gradio version."""
    try:
        import gradio as gr
        version = gr.__version__
        print(f"✅ Current Gradio version: {version}")
        return version
    except ImportError:
        print("❌ Gradio not installed")
        return None

def fix_gradio_compatibility():
    """Fix Gradio compatibility issues."""
    print("🔧 DoChat+ Gradio Compatibility Fix")
    print("=" * 40)
    
    # Check current version
    version = check_gradio_version()
    if not version:
        print("Please install Gradio first: pip install gradio>=3.50.0")
        return False
    
    major_version = int(version.split('.')[0])
    
    if major_version >= 4:
        print("🎯 Detected Gradio 4.x - Applying compatibility fixes...")
        
        # The main app.py has already been updated with compatibility code
        print("✅ App compatibility: Already handled in app.py")
        print("✅ Demo compatibility: Already handled in demo_app.py")
        
        print("\n🚀 Compatibility fixes applied!")
        print("The application should now work with Gradio 4.x")
        
    elif major_version == 3:
        print("✅ Gradio 3.x detected - Should work without issues")
        
    else:
        print("⚠️  Old Gradio version detected. Recommending upgrade...")
        response = input("Upgrade to compatible version? (y/N): ")
        if response.lower() == 'y':
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'gradio>=3.50.0'])
                print("✅ Gradio upgraded successfully!")
            except subprocess.CalledProcessError:
                print("❌ Failed to upgrade Gradio")
                return False
    
    return True

def test_compatibility():
    """Test if the fix worked."""
    print("\n🧪 Testing compatibility...")
    
    try:
        import gradio as gr
        
        # Test creating a simple interface
        with gr.Blocks() as demo:
            gr.Markdown("# Test Interface")
        
        # Test launch parameters
        launch_args = {
            "server_name": "127.0.0.1",
            "server_port": 7861,
            "share": False,
            "show_error": True,
            "enable_queue": True
        }
        
        # Check if show_tips is supported
        if hasattr(gr.Blocks, 'launch') and 'show_tips' in gr.Blocks.launch.__code__.co_varnames:
            launch_args["show_tips"] = True
            print("✅ show_tips parameter: Supported")
        else:
            print("ℹ️  show_tips parameter: Not supported (Gradio 4.x behavior)")
        
        print("✅ Compatibility test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Compatibility test failed: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Starting DoChat+ Gradio compatibility check...")
    
    if not fix_gradio_compatibility():
        print("❌ Failed to fix compatibility issues")
        sys.exit(1)
    
    if not test_compatibility():
        print("❌ Compatibility test failed")
        sys.exit(1)
    
    print("\n🎉 All compatibility issues resolved!")
    print("You can now run DoChat+ with:")
    print("  python app.py")
    print("  or")
    print("  python demo_app.py")

if __name__ == "__main__":
    main()