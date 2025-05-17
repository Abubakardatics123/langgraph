#!/bin/bash

# Opens the frontend in a web browser

echo "Opening HR Workflow Frontend in your default browser..."

# Determine OS and open browser accordingly
case "$(uname -s)" in
   Darwin)
     # macOS
     open http://localhost:5000
     ;;
   Linux)
     # Linux
     xdg-open http://localhost:5000
     ;;
   CYGWIN*|MINGW*|MSYS*)
     # Windows
     start http://localhost:5000
     ;;
   *)
     echo "Unable to detect OS to open browser automatically"
     echo "Please open http://localhost:5000 in your browser"
     ;;
esac

echo "If the browser doesn't open, please manually navigate to: http://localhost:5000"
echo "Make sure the server is running with ./run_frontend.sh first" 