cd live_track

PYTHONPATH=../. python3 live_track_24hrs.py --instrument USOIL &

PYTHONPATH=../. python3 live_track_24hrs.py --instrument NIFTY &

echo 'started tracking of NIFTY and USOIL'