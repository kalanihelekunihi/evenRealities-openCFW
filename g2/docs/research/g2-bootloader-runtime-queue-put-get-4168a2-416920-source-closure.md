# G2 bootloader message-queue put/get source closure

Status date: 2026-08-26  
Target: official G2 `s200_v2.2.6.10` Apollo bootloader

## Authenticated boundary

The complete message-queue put body `[0x004168A2,0x00416920)` is 126 bytes
with SHA-256
`91e5690abdb827a51e097c4a062fe375df5157e3f2039d736b298b22e04868be`.
Its two direct callers are `0x0042DCDA` and `0x0042E6C8`. The adjacent
message-queue get body `[0x00416920,0x0041699A)` is 122 bytes with SHA-256
`314c0a49b1cd6147c22638e354ac5e1fc82bf310547a5fb38a897f4f263c784e`;
its direct callers are `0x0042DEA8` and `0x0042E65E`. No stored entry pointer
was found for either wrapper.

The ten bytes `[0x0041699A,0x004169A4)` are authenticated alignment and the
shared `0xE000ED04` SCB ICSR literal pool, SHA-256
`cee9e0dc13ea1c82bfb1368348df84ffab973c1fe17cce15036de271d685d310`.
They remain official data and are not redirected. The next distinct
executable body starts at `0x004169A4`.

## Recovered contract

`runtime_queue_put_4168a2.c` and `runtime_queue_get_416920.c` are bounded
Apache-2.0 adaptations of CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Both ignore the CMSIS message
priority argument, reject null queue/message arguments, and split on the
source-owned critical-context predicate. Interrupt context additionally
requires a zero timeout, maps retained backend failure to `osErrorResource`,
and requests PendSV only when the retained ISR backend reports a woken task.
Task context maps a failed zero-timeout operation to `osErrorResource` and a
failed nonzero-timeout operation to `osErrorTimeout`.

The put wrapper binds to retained queue-send providers `0x0041A024` (ISR) and
`0x00419EC0` (task). The get wrapper binds to retained queue-receive providers
`0x0041A3B0` (ISR) and `0x0041A114` (task). Those dependency addresses and the
source-owned critical-context edge are strict relocations; no semantic claim
is made beyond the recovered ABI and observed status contract.

## Production evidence

Apple clang 21 and Homebrew clang 22.1.8 emit identical unrelocated bodies:
112 bytes / `ecf8254fadacf5b00aff7b45b21aaa2faf1dbedfabaa598aa0149f89cb29d4fc`
for put and 108 bytes /
`0a8e9bd91c5244cf3afa1e3a88800380279879f12801354b2384ff6a3a8abf83`
for get. Profile-specific linked hashes are pinned at Apple offsets 4680/4792
and Linux offsets 4664/4776. Hosted tests cover validation order, status
mapping, ignored priority, exact retained arguments, and conditional PendSV.
Target compilation, exact stock redirects, mutation-set checks, dual-profile
providers, manifest ownership, and both unsigned packages pass offline.

Canonical accounting after this closure is 4,889 source-owned bytes, 5,850
generated patch bytes, 12 generated alignment bytes, and 142,749 retained
official bytes. The 4,900-byte overlay hashes to
`9148e6922a8429dda593f96cd3a50f646c2f27775d1c5ea02e319c738c914ea4`;
the 153,500-byte provider hashes to
`e622cfe1f730b914391a8f573bab6e7677d88d05613d9e37cc93e8fad0d6c050`.
The Apple and Linux unsigned packages are respectively 4,735,078 bytes /
`fb4926da0fc14bf9b17dd90aebfdb6a8b5a42df82e7a042bbbcd2de91970c15d`
and 4,511,072 bytes /
`13239814a78f0112b011b265998a45edb012962e618daa307fe22a137f841564`.

No image was signed, flashed, installed, reset, or booted. Live queue,
scheduler, PendSV, timing, and caller-path validation is explicitly blocked by
the absence of an authorized responsive G2 right temple. This closure advances
the software frontier; it does not declare firmware-wide completeness.
