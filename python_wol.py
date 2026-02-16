#!/usr/bin/env python3
"""
Monitor LAN hosts via ping. Send Wake-on-LAN when a host is down.
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import List, Tuple

try:
    from ping3 import ping
    from wakeonlan import send_magic_packet
except ImportError:
    print("Missing dependencies. Install with: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

CONFIG_PATH = Path("/etc/python-WoL.conf")
LOG_PATH = Path("/var/log/python-WoL.log")
DEFAULT_PROBE_INTERVAL = 60
DEFAULT_CONFIG_CONTENT = """# python-WoL config: one host per line, format: IP MAC
# Example:
# 192.168.1.100 aa:bb:cc:dd:ee:ff
# 192.168.1.101 00:11:22:33:44:55

"""


def setup_logging(log_path: Path) -> None:
    """Configure logging to file and stdout."""
    fmt = "%(asctime)s [%(levelname)s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    handlers: List[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    try:
        handlers.insert(0, logging.FileHandler(log_path))
    except OSError:
        pass  # Fall back to stdout only if log file not writable
    logging.basicConfig(level=logging.INFO, format=fmt, datefmt=datefmt, handlers=handlers)


def ensure_config_exists() -> Path:
    """Create default config at /etc/python-WoL.conf if it doesn't exist."""
    if CONFIG_PATH.exists():
        return CONFIG_PATH

    try:
        CONFIG_PATH.write_text(DEFAULT_CONFIG_CONTENT)
        logging.info("Created default config at %s. Edit it with your hosts (IP MAC per line) and re-run.", CONFIG_PATH)
        sys.exit(0)
    except OSError as e:
        logging.error("Cannot create config at %s: %s. Run with sudo or create manually.", CONFIG_PATH, e)
        sys.exit(1)


def load_hosts(config_path: Path) -> List[Tuple[str, str]]:
    """Parse config file. Returns list of (ip, mac) tuples."""
    hosts = []
    for line in config_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            hosts.append((parts[0], parts[1]))
    return hosts


def probe_host(ip: str, timeout: float = 2.0) -> bool:
    """Return True if host responds to ping."""
    try:
        result = ping(ip, timeout=timeout)
        return result is not None
    except Exception:
        return False


def send_wol(mac: str) -> None:
    """Send Wake-on-LAN magic packet to the given MAC address."""
    try:
        send_magic_packet(mac)
        logging.info("Sent WoL to %s", mac)
    except Exception as e:
        logging.error("Failed to send WoL to %s: %s", mac, e)


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor hosts via ping, send WoL when down.")
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=CONFIG_PATH,
        help=f"Config file path (default: {CONFIG_PATH})",
    )
    parser.add_argument(
        "-i", "--interval",
        type=int,
        default=DEFAULT_PROBE_INTERVAL,
        help=f"Probe interval in seconds (default: {DEFAULT_PROBE_INTERVAL})",
    )
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=2.0,
        help="Ping timeout in seconds (default: 2.0)",
    )
    parser.add_argument(
        "-l", "--log",
        type=Path,
        default=LOG_PATH,
        help=f"Log file path (default: {LOG_PATH})",
    )
    args = parser.parse_args()

    setup_logging(args.log)
    log = logging.getLogger()

    log.info("Starting python-WoL")
    config_path = args.config
    if not config_path.exists():
        if config_path == CONFIG_PATH:
            ensure_config_exists()
        else:
            log.error("Config not found: %s", config_path)
            sys.exit(1)

    log.info("Reading config from %s", config_path)
    hosts = load_hosts(config_path)
    if not hosts:
        log.error("No hosts configured. Add lines in format: IP MAC")
        sys.exit(1)

    log.info("Loaded %d host(s) from config", len(hosts))
    log.info("Monitoring started, interval=%ds", args.interval)

    # Initial probe at start
    for ip, mac in hosts:
        if probe_host(ip, args.timeout):
            log.info("Ping %s (%s): up", ip, mac)
        else:
            log.info("Ping %s (%s): down, sending WoL", ip, mac)
            send_wol(mac)

    # Main loop
    while True:
        time.sleep(args.interval)
        for ip, mac in hosts:
            if probe_host(ip, args.timeout):
                log.info("Ping %s (%s): up", ip, mac)
            else:
                log.info("Ping %s (%s): down, sending WoL", ip, mac)
                send_wol(mac)


if __name__ == "__main__":
    main()
