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
version discriminator or reveals the private generating commit.

## Production closure

`components/apollo_main/core_overlay/callback_facades.c` independently
implements all ten linked entries as GPL-3.0-only, selector-isolated C. Ten
guarded redirects replace all 380 stock body bytes with 208 compiled Thumb
bytes plus six alignment bytes. Ten strict relocations bind only the recovered
generic callback-manager init, deinit, register, unregister, and notify
providers. Both directly addressed 34-byte diagnostic/type pools remain
authenticated official data.

Host contracts cover both callback-list and type identities, init/deinit,
null rejection, provider return propagation, unregister suppression, and the
notification in/out value word. Canonical overlay/component/package sizes are
193,488 / 3,716,884 / 4,495,378 bytes with SHA-256 values
`a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`,
`026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`,
and `03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`.
The 1,963,573-byte flash plan hashes to
`ef7a204c200024422defd2cb9e0064a5aa4278bb14533e4007bd0daf2db1e67f`.
These facades introduce no direct hardware operation, so their software
closure does not require a physical validation claim. Wider callback-manager
and device behavior remain separate ledger capabilities.
