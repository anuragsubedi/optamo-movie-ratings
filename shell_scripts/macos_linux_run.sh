#!/bin/bash
# Run Script for macOS/Linux

# Change context to the project root directory regardless of where script is run
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/.." || exit

echo " Starting Movie Ratings Platform..."

# Function to cleanly shut down background processes on exit
cleanup() {
    echo ""
    echo " Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Catch CTRL+C (SIGINT) and call cleanup
trap cleanup SIGINT SIGTERM

# Start Backend
echo " Starting Flask backend on port 5001..."
cd backend || exit
source .venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Start Frontend
echo " Starting Angular frontend on port 4200..."
cd frontend || exit
NG_CLI_ANALYTICS=false npx ng serve &
FRONTEND_PID=$!
cd ..

echo ""
echo " Application is running!"
echo "   Frontend: http://localhost:4200"
echo "   Backend : http://localhost:5001"
echo "   API Docs: http://localhost:5001/apidocs/"
echo ""
echo "Press CTRL+C to stop both servers."

# Wait indefinitely until interrupted
wait
