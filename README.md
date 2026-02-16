# python-WoL

A Python script that monitors LAN hosts via ping and sends Wake-on-LAN when they are down.

## Features

- Pings configured hosts at a configurable interval
- Sends WoL magic packet when a host does not respond
- Initial probe at script start
- Logging to `/var/log/python-WoL.log`
- Runs as a systemd service

## Requirements

- Python 3.8+
- `ping3` and `wakeonlan` (see requirements.txt)

## Installation

```bash
pip install -r requirements.txt
```

### As systemd service

```bash
./install.sh
```

This installs the script to `/opt/python-WoL/`, installs dependencies, and registers the systemd service.

## Configuration

Config file: `/etc/python-WoL.conf`

Format: one host per line, `IP MAC`

```
# python-WoL config
192.168.1.100 aa:bb:cc:dd:ee:ff
192.168.1.101 00:11:22:33:44:55
```

If the config does not exist, run once with sudo to create a template:

```bash
sudo python_wol.py
```

Then edit `/etc/python-WoL.conf` with your hosts.

## Usage

### Command line

```bash
python_wol.py                    # Use default config and interval (60s)
python_wol.py -c /path/to.conf   # Custom config file
python_wol.py -i 120             # Probe every 120 seconds
python_wol.py -t 3.0            # Ping timeout 3 seconds
python_wol.py -l /var/log/wol.log  # Custom log file
```

### Systemd service

```bash
sudo systemctl enable python-wol   # Start on boot
sudo systemctl start python-wol    # Start now
sudo systemctl status python-wol   # Check status
```

### View logs

```bash
tail -f /var/log/python-WoL.log
# or
journalctl -u python-wol -f
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `-c`, `--config` | `/etc/python-WoL.conf` | Config file path |
| `-i`, `--interval` | 60 | Probe interval in seconds |
| `-t`, `--timeout` | 2.0 | Ping timeout in seconds |
| `-l`, `--log` | `/var/log/python-WoL.log` | Log file path |
