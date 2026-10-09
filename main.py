#!/usr/bin/env python3
import asyncio
import json
import os
import platform
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlencode

import websockets

DISCOVERY_URL = "https://api.fluxer.app/.well-known/fluxer"


def discover_gateway():
    req = urllib.request.Request(DISCOVERY_URL)
    with urllib.request.urlopen(req, timeout=15) as response:
        document = json.load(response)

    gateway = document["endpoints"]["gateway"]
    return gateway


async def main():
    token = os.environ.get("FLUXER_TOKEN")
    if not token:
        raise SystemExit("Set FLUXER_TOKEN to your raw Fluxer token.")

    gateway = await asyncio.to_thread(discover_gateway)
    separator = "&" if "?" in gateway else "?"
    uri = gateway + separator + urlencode({
        "v": "1",
        "encoding": "json",
    })

    sequence = None
    session_id = None
    heartbeat_interval = None
    last_heartbeat_ack = None
    ready_dumped = False

    async with websockets.connect(
        uri,
        ping_interval=None,
        open_timeout=20,
        max_size=None,
    ) as ws:
        async def heartbeat():
            await ws.send(json.dumps({
                "op": 1,
                "d": sequence,
            }))

        async def heartbeat_loop():
            nonlocal last_heartbeat_ack
            while True:
                await asyncio.sleep(heartbeat_interval / 1000)
                await heartbeat()

        async for raw in ws:
            message = json.loads(raw)
            op = message.get("op")
            data = message.get("d")

            if op == 10:
                heartbeat_interval = data["heartbeat_interval"]

                await ws.send(json.dumps({
                    "op": 2,
                    "d": {
                        "token": token,
                        "properties": {
                            "os": platform.system(),
                            "browser": "Fluxer Client",
                            "device": "desktop",
                        },
                        "presence": {
                            "status": "offline"
                        }
                    },
                }))

                asyncio.create_task(heartbeat_loop())

            elif op == 0:
                sequence = message.get("s", sequence)
                event = message.get("t")

                if event == "READY" and not ready_dumped:
                    session_id = data.get("session_id")

                    filename = "ready.json"
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(message, f, indent=2, ensure_ascii=False)
                        f.write("\n")

                    ready_dumped = True
                    print(f"READY saved to {filename}")
                    print(f"Session ID: {session_id}")
                    print(f"Sequence: {sequence}")

                else:
                    print(f"Dispatch: {event} (seq={sequence}): {json.dumps(message, ensure_ascii=False)}")

            elif op == 1:
                await heartbeat()

            elif op == 11:
                last_heartbeat_ack = datetime.now(timezone.utc)
                print(f"Heartbeat ACK: {last_heartbeat_ack.isoformat()}")

            else:
                print(json.dumps(message, ensure_ascii=False))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Disconnected.")
