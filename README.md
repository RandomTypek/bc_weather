# bc_weather

Usage:

1. change config.json
2. python fill_database.py
3. python fetch_weather.py

To run as a service:

1. edit paths in fetch_weather.service
2. cp fetch_weather.service ~/.config/systemd/user/
3. systemctl --user enable --now fetch_weather
