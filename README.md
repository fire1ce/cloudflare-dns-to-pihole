# sync-pihole-cloudfalre-dns

## Installation

check if python venv ins installed

```bash
python3 -m venv
```

Clone the repo to main Pihole

```bash
cd sync-pihole-cloudflare-dns
```

```bash
python3 -m venv python-env
```

```bash
source python-env/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
which python
```

should print something like that:

/root/sync-pihole-cloudflare-dns/python-env/bin/python

## Cron

Run every 3 hours example

```bash
0 */3 * * * /root/sync-pihole-cloudflare-dns/python-env/bin/python /root/sync-pihole-cloudflare-dns/sync.py
```

Run Every 5 minuts

```bash
*/5 * * * * /root/sync-pihole-cloudflare-dns/python-env/bin/python /root/sync-pihole-cloudflare-dns/sync.py
```
