# fluxer-gateway-bug-missing-sessions-replace

There is no `SESSIONS_REPLACE` even when opening a Fluxer desktop or web client (both of the following ones were triggered by closing the same client):

```
$ export FLUXER_TOKEN=flx_12345
$ python3 main.py
READY saved to ready.json
Session ID: 12345
Sequence: 1
Dispatch: SESSIONS_REPLACE (seq=2): {"d": [{"afk": false, "mobile": false, "session_id": "all", "status": "offline"}, {"afk": false, "mobile": false, "session_id": "12345", "status": "offline"}], "op": 0, "s": 2, "t": "SESSIONS_REPLACE"}
Dispatch: SESSIONS_REPLACE (seq=3): {"d": [{"afk": false, "mobile": false, "session_id": "all", "status": "offline"}, {"afk": false, "mobile": false, "session_id": "12345", "status": "offline"}], "op": 0, "s": 3, "t": "SESSIONS_REPLACE"}
```
