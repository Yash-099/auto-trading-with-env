
source venv/bin/activate
PYTHONPATH=. python3 live_track/every_session.py --instrument NIFTY &
PYTHONPATH=. python3 live_track/detect_sims.py --instrument NIFTY --direction both &

echo 'started tracking of NIFTY'