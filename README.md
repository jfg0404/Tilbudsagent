# Cloud-based Price Monitoring Agent

This is a cloud-based price monitoring agent application with a dashboard implemented in Flask.

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/jfg0404/Tilbudsagent.git
   cd Tilbudsagent
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the environment variables based on `.env.example`.
5. Run the application:
   ```bash
   python main.py
   ```

## File Structure
- `main.py`: Entry point for the application.
- `price_tracker.py`: Contains the logic for tracking prices.
- `app.py`: Flask application setup.
- `templates/`: Contains HTML templates for the web dashboard.
- `static/`: Contains CSS and JavaScript files.
- `models.py`: Defines database models.
- `config.py`: Configuration management for the application.
- `Dockerfile`: Docker setup for containerization.
- `requirements.txt`: Python dependencies.
- `.env.example`: Example environment variables.
- `README.md`: Project documentation.

## License
This project is licensed under the MIT License.