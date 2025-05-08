#!/usr/bin/env python3
import sys
import webview

def main():
    url = sys.argv[1]
    # create the pop-up with no confirm-on-close
    webview.create_window(
        'Zoom Authorization',
        url,
        width=600,
        height=600,
        resizable=True,
        text_select=True,
        confirm_close=False,
        min_size=(400, 400)
    )
    webview.start(debug=True)

if __name__ == '__main__':
    main()
