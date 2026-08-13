# G2 Ring-connect policy dependency boundary

Status: complete stock-object and provider closure over G2 2.2.6.10. No device
or flash operation is performed.

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

## OpenCFW implication

The object remains first-party policy rather than reusable third-party code.
Its behavior is now bounded well enough for a later clean-room replacement,
but it does not block dependency provenance closure. No public source or stock
artifact identifies the private G2 commit that produced it.

## Reproduction

```sh
python3 openCFW/tools/analyze_g2_ring_connect_policy.py
python3 -m unittest openCFW.tests.test_analyze_g2_ring_connect_policy
```

The analyzer authenticates every function, boundary pool, retained path
reference, call provider, ingress site, stored pointer, and selected upstream
commit.
