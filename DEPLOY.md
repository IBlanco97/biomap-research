# VPS deployment

These commands assume the project lives at `/root/Lab/biomap-research`, as shown in the current VPS terminal.

## Update code

```bash
cd /root/Lab/biomap-research
git pull
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Run manually

```bash
BIOMAP_HOST=0.0.0.0 BIOMAP_PORT=8501 python3 server.py
```

From your laptop:

```text
http://VPS_PUBLIC_IP:8501
```

Health check:

```bash
curl http://127.0.0.1:8501/health
```

## Keep it running with systemd

```bash
sudo cp deploy/biomap-research.service.example /etc/systemd/system/biomap-research.service
sudo systemctl daemon-reload
sudo systemctl enable biomap-research
sudo systemctl start biomap-research
```

Check status and logs:

```bash
sudo systemctl status biomap-research --no-pager
sudo journalctl -u biomap-research -f
```

Restart after a code update:

```bash
cd /root/Lab/biomap-research
git pull
source .venv/bin/activate
python3 -m pip install -r requirements.txt
sudo systemctl restart biomap-research
```

## Firewall

If the page does not open from your laptop:

```bash
sudo ufw allow 8501/tcp
sudo ufw status
```

Also confirm that the VPS provider firewall/security group allows inbound TCP traffic on port `8501`.
