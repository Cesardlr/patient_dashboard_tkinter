#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Separate script to run avatar in webview window"""
import webview
import sys

AVATAR_URL = "https://stunning-crisp-51ccb2.netlify.app/"

if __name__ == "__main__":
    try:
        # Get position from command line arguments if provided
        x = int(sys.argv[1]) if len(sys.argv) > 1 else None
        y = int(sys.argv[2]) if len(sys.argv) > 2 else None
        width = int(sys.argv[3]) if len(sys.argv) > 3 else 700
        height = int(sys.argv[4]) if len(sys.argv) > 4 else 800
        
        window_config = {
            "title": "Avatar Medico - Asistente Virtual",
            "url": AVATAR_URL,
            "width": width,
            "height": height,
            "background_color": "#000000",
            "resizable": True,
            "min_size": (600, 600)
        }
        
        if x is not None and y is not None:
            window_config["x"] = x
            window_config["y"] = y
        
        webview.create_window(**window_config)
        webview.start(gui="edgechromium", debug=False)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

