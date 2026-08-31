# G2 Ring-connect policy dependency boundary

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status: complete stock-object/provider closure and production source routing
over G2 2.2.6.10. No device or flash operation is performed. Physical
paired-G2 validation is explicitly blocked by unavailable authorized evidence.

## Result

`platform\protocols\ring_service\ring_connect_policy.c` occupies
`[0x0049F020,0x0049F828)`: 15 functions / 1,828 executable bytes followed by a
228-byte literal pool, totaling 2,056 physical bytes. The true start is 60
bytes earlier than the first retained-path anchor. Three pathless helpers at
`0x0049F020`, `0x0049F028`, and `0x0049F040` provide the kernel tick, elapsed
tick, and policy-mode timeout operations. The preceding
`ux_wear_detect.c` pool ends exactly at `0x0049F020`, and the following closed
BLE-central object begins exactly at `0x0049F828`.

Ghidra found 11 functions. Complete source order, direct-call topology, and a
stored Thumb callback at `0x0049F7EC` restore four more: the three helpers and
`_ringReconnectTimeoutFire` at `0x0049F500`. All 15 bodies are instruction
closed. Nineteen raw path references cover all 12 diagnostic-bearing policy
functions.

The retained function strings recover exact names for the public surface and
show dominant-hand switch-window handling, `RING_CONNECT_INFO` throttling,
connect/reconnect timeout scheduling, success/failure notification, and two
reset scopes.

## Provider closure

The 120 direct calls split into 12 local and 108 external calls:

| Provider | Calls | Provenance |
|---|---:|---|
| EasyLogger | 95 | selected source-equivalent commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| CMSIS-FreeRTOS | 1 | exact `osKernelGetTickCount` from v10.5.1 commit `d213f261b5be6bb29a7cce8b84071706b72f4d53` over kernel `def7d2df…` and CMSIS_5 `2b7495b…` |
| closed firmware event loop | 10 | all six entries are already source-routed in OpenCFW |
| closed protobuf pair manager | 1 | first-party ring-connect facade over admitted nanopb |
| closed BLE central | 1 | first-party Ring-owner predicate over admitted Cordio |

There are no direct Cordio, nanopb, allocator, scheduler-core, or other opaque
utility calls. Thus this high-ranked object does not add a third-party family,
version discriminator, or producing-commit clue. Its Cordio and nanopb
relationships terminate at independently closed first-party facades.

The image contains 29 direct entry sites, one stored callback pointer, no
indirect body call, and no strict-interior ingress. One unaligned word at
`0x004F468A` happens to encode interior address `0x0049F640`; it is not an
aligned callback or control-flow edge.

## Production routing

`components/apollo_main/core_overlay/ring_connect_policy.c` is the complete
15-function clean-room implementation. Host oracles cover state windows,
dominant-hand decisions, connect-info throttling, idempotent timeout scheduling,
reconnect failure, owner-gated delayed success, cancellation, and both reset
scopes. All fifteen selector-isolated Cortex-M55 builds pass `-Wall -Wextra
-Werror`.

Fifteen guarded `B.W` redirects replace all 1,828 authenticated stock body
bytes. The reviewed Apple-clang build emits 570 bytes of Thumb text plus 14
alignment bytes with 24 strict relocations; the authenticated 228-byte literal
pool remains official. The aggregate overlay is 252,162 bytes (SHA-256
`2def566dbf70594c89471066a7cd17f6d1fa94196f65ff48237385396e9cfd19`),
the Apollo component is 3,775,558 bytes (SHA-256
`7228edb650fe39bda63480691fe94ed59d0807ca5e30846d35ec08e134e08350`),
and the 4,554,052-byte EVENOTA package has SHA-256
`c146ea7977a5521aa1df24a1a285768d7e2396fab96f117315a5baa2dcb65998`.
Its flash plan contains 4,057 placed, two unresolved evidence-only, five
container-only, and six protected regions.

No public source or stock artifact identifies the private G2 commit that
produced the original object. Live Cordio/WSF timing, dual-temple role changes,
reconnect behavior, and peer-visible notification ordering cannot be validated:
the authorized right temple is nonresponsive, the authorized left temple must
remain stock, and no responsive authorized pair or golden Ring/BLE capture is
available.

## Reproduction

```sh
python3 openCFW/tools/analyze_g2_ring_connect_policy.py
python3 -m unittest openCFW.tests.test_ring_connect_policy_candidate
python3 -m unittest openCFW.tests.test_analyze_g2_ring_connect_policy
```

The analyzer authenticates every stock function, boundary pool, retained path
reference, provider, ingress site, stored pointer, source leaf, relocation,
guarded redirect, manifest region, package, and flash-plan identity.
