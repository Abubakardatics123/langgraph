# HR Workflow Frontend

This document provides instructions for using the HR Onboarding Workflow Frontend.

## Overview

The frontend is a web-based interface that allows HR staff to:
1. Input new employee information
2. Process the onboarding workflow
3. View the generated equipment needs, system access, and training plan

## Technical Details

The frontend consists of:
- A Flask API backend (`api.py`) that interfaces with the LangGraph workflow
- HTML/CSS/JS frontend for user interaction
- Bootstrap for styling
- No database required - all processing happens in memory

## Running the Frontend

1. Make sure you have Python 3 installed:
   ```
   python3 --version
   ```

2. Install the required dependencies:
   ```
   python3 -m pip install flask flask-cors
   ```

3. Start the Flask server using the provided script:
   ```
   ./run_frontend.sh
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Using the Application

1. Fill out the employee information form with:
   - Full name
   - Position
   - Department
   - Start date

2. Click "Start Onboarding Process" to begin

3. The system will process the information through the LangGraph workflow

4. Results will display in several sections:
   - Employee Information
   - Equipment Needs (generated by AI)
   - System Access (generated by AI)
   - Training Requirements (generated by AI)
   - HR Notes
   - IT Notes

5. Click "Start New Onboarding" to process another employee

## Troubleshooting

- If the server fails to start, ensure you're using Python 3 and have Flask installed
- If the workflow fails, check the console logs for error messages
- The workflow requires internet access to communicate with the Groq API

## API Endpoints

The following endpoints are available:

- `GET /` - Serves the frontend HTML
- `GET /api/health` - Health check endpoint
- `POST /api/start-onboarding` - Starts the onboarding workflow with employee data

## Extending the Frontend

The frontend can be extended with:
- User authentication
- Database storage for employees
- Additional workflow steps
- PDF generation of onboarding documents
- Email notifications 