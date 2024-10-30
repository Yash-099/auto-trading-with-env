cd live_track

# PYTHONPATH=../. python3 live_track_24hrs.py --instrument USOIL &

PYTHONPATH=../. python3 detect_sims.py --instrument USOIL --direction up &
PYTHONPATH=../. python3 detect_sims.py --instrument USOIL --direction down &

# PYTHONPATH=../. python3 live_track_24hrs.py --instrument NIFTY &

PYTHONPATH=../. python3 detect_sims.py --instrument NIFTY --direction up &
PYTHONPATH=../. python3 detect_sims.py --instrument NIFTY --direction down &

echo 'started tracking of NIFTY and USOIL'