# R1 Peer Manager event policy

## Decision

`0x0007F2B0` is a 1,052-byte R1 product callback around Nordic nRF5 SDK 17.1.0 Peer Manager. It is
admitted as `r1_product_specific` / `clean_room_behavior_only`; the Peer Manager, security
dispatcher, bond database, FDS storage, rank management, and flash garbage collection remain
Nordic provider code.

The R1 security/configuration initializer at `0x0004E4B4` calls Nordic `pm_register` at
`0x0004E50E`. Word `0x0004E51C` is exact Thumb pointer `0x0007F2B1`, establishing the otherwise
indirect callback edge. The body has two executable segments:

- `0x0007F2B0..<0x0007F6AA`: 1,018 bytes
- `0x0007F9EC..<0x0007FA0E`: 34 bytes

Their concatenated SHA-256 is
`b0521a6e459b45cdca31158563487448bf5a260bd5140a6398845507bcb5087b`.
The intervening bytes are strings, pointers, and literal data and are not counted as executable
ownership.

## Provider split and recovered behavior

Every event first calls Nordic `pm_handler_on_pm_evt` at `0x0007F2B8` and
`pm_handler_flash_clean` at `0x0007F2BE`. OpenR1 preserves those calls from the pinned SDK rather
than copying their implementations. The remaining product callback applies these policies:

| Peer Manager event | R1 product policy |
| --- | --- |
| `PM_EVT_CONN_SEC_SUCCEEDED` (`3`) | Record the secured connection, clear/schedule product connection events, distinguish a loaded bond from a first connection, and update advertising/role state. |
| `PM_EVT_CONN_SEC_FAILED` (`4`) | Clear pending connection work, set the security-failure event, record the procedure/error/origin, and preserve the special `0x1101` diagnostic path. |
| `PM_EVT_CONN_SEC_CONFIG_REQ` (`5`) | Reply through Nordic `pm_conn_sec_config_reply` with `allow_repairing = true`; exact callsite `0x0007F66E`. |
| `PM_EVT_STORAGE_FULL` (`7`) | Leave flash recovery to Nordic's standard flash-clean handler and emit diagnostics only. |
| `PM_EVT_PEER_DATA_UPDATE_SUCCEEDED` (`9`) | Recognize newly stored bonding data; the recovered message says a new bond may be added to a whitelist, but the body contains no whitelist mutation. |
| peer/peers deletion success (`13`/`15`) | Update product advertising/connection state. |
| flash garbage collection success (`20`) | Emit completion diagnostics; Nordic owns the collection state machine. |

Nordic `pm_peer_data_bonding_load` is called at `0x0007F440` to distinguish a reconnect from a new
peer. The strings “This is a new device connecting for the first time,” “encrypted get sec auth
flag will notify,” and “encrypted not get sec auth flag will wait” corroborate the product event
policy; they are not evidence that a bond grants application authorization.

## Security-audit consequence

OpenR1 intentionally keeps three hardening properties while reproducing the functional policy:

- repairing is allowed through the Nordic API, but a bond remains transport identity and does not
  set the independent product-authorization bit;
- the stock “New Bond, add the peer to the whitelist if possible” branch logs only and performs no
  whitelist mutation, so OpenR1 performs no whitelist mutation and does not invent one;
- recovered helper `0x0008216C` loads bonding data and prints the LTK. Calls at `0x0007F488` and
  `0x0007F632` are retained as audit evidence only. OpenR1 never calls this helper and never logs,
  exports, or reconstructs bond keys.

The clean-room SDK adapter is
`openr1_peer.c`. It invokes the two Nordic
standard handlers, replies to repairing requests through Peer Manager, synchronizes encrypted and
bonded state into the runtime without granting authorization, and records provider errors. It does
not recreate Nordic internals or the recovered secret-bearing diagnostic helper.

## Verification

```sh
python3 tools/summarize_r1_peer_manager_event_policy.py
python3 tools/verify_openr1.py
```

The summarizer pins the image, exact executable segments, body hash, callback registration pointer,
Nordic-provider edges, event markers, and excluded key-logging path. It performs no BLE operation
and accesses no live peer database.
