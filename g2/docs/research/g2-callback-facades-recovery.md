# G2 charge and message callback-facade recovery

Two retained zero-anchor census paths resolve into structurally parallel
callback facades:

| Path | Physical interval | Bodies | Pool | Callback list/type |
|---|---|---:|---:|---|
| `cb_charge.c` | `[0x004AEA40,0x004AEB20)` | 5 / 190 B | 34 B | `0x20073F78` / `BAT_INFO` |
| `cb_msg_notif.c` | `[0x004E1A48,0x004E1B28)` | 5 / 190 B | 34 B | `0x20073F84` / `MSG_COUNT` |

For each object, Ghidra found only init and notify. Raw source-order recovery
adds deinit plus the retained-symbol register/unregister bodies. Both objects
pin all 78 instructions, 15 direct calls, seven direct entries, their two raw
path references, both boundaries, and zero indirect, stored, or
strict-interior ingress.

Each facade implements generic callback-list init, deinit, null-checked
register/unregister, and in/out-word notification. Ten calls per object are
already admitted EasyLogger diagnostics; the remaining five are the same
first-party generic callback-manager ABI. There is no CMSIS-FreeRTOS call or
embedded third-party definition. Exact public searches for the retained
symbols and filenames found no source candidates, so neither object adds a
version discriminator or reveals the private generating commit. Neither is
production-routed.
