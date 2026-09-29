#!/data/data/com.termux/files/usr/bin/bash
set -e
pkg update
pkg install -y python nodejs-lts php
echo
echo "Runtimes installed. Start LocalCodeEditor with:"
echo "  python server.py"
echo "Then open http://127.0.0.1:8765 in your browser."
