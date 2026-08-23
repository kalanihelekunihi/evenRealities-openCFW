# Cordio DM security source recovery

Status date: 2026-08-23
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The stock `dm_sec.c` translation unit is completely accounted for at
`[0x004D2364,0x004D254C)`: eight linked functions contribute 462 code bytes,
and a 26-byte alignment/literal gap brings the physical interval to 488 bytes
with SHA-256
`4107b2f66ec33b888a5b4927b654ac6f69ac8ae29545bbfdfb0b2af211fba75f`.
Twenty-three direct calls, the three registered interface pointers, and zero
strict-interior pointers close ingress.

Four APIs have no stock body, caller, or pointer and are dead-stripped:
`dmSecApiLtkMsg`, `DmSecCancelReq`, `DmSecSetLocalCsrk`, and
`DmSecSetLocalIrk`. All 12 source functions are therefore classified. The
eight live functions are now compiled from the authenticated Packetcraft
r20.05c behavior and production-routed; the four absent APIs remain explicit
configuration exclusions.

## Production admission

`components/apollo_main/core_overlay/cordio_dm_sec.c` provides exactly the
eight live entries. Eight guarded full-span redirects replace all 462 stock
code bytes with 506 compiled Thumb bytes and six alignment bytes. The route
analyzer authenticates every stock span, the interface ingress, and all 19
external relocations. The implementation preserves the r20 LESC EDIV/Rand
rejection, STK fallback, connection busy/idle transitions, ATT-before-DM-before-
SMP completion order, bounded authentication-message copy, interface/control-
block initialization, key accessors, and SMP database reset. Initializing the
unused failure-event `using_ltk` byte to zero is a bounded deterministic safety
correction; it does not alter the failure event contract.

Host behavior tests, the exact target symbol/relocation surface, component
assembly, source manifest, package assembly, and flash-plan generation gate the
route. The canonical Apple overlay/component/package identities are
`167088/3690484/4468978` bytes with SHA-256
`63a2dab6221e9c6fcbae491442752d3d4bf3f1e9fe4a1bb8793e7a58493781ca`,
`1f4e39b37007da8a8e845bd653a29a3c251d9da22cfe574949f8f187f5a66e19`, and
`edd49b59043320fa1abfcbdc202eb1b03b575c887c500829205fa6af13ab1c5b`.
No hardware was accessed or flashed. Controller timing, pool pressure,
disconnect races, legacy/LESC peer interoperability, and encryption callback
ordering on a physical G2/EM9305 are explicitly blocked by unavailable
authorized physical evidence.

## Exact release discriminator

AmbiqSuite R2.4.2/R2.5.1 and Packetcraft r19 share Git blob
`dfb00b00ad7e663edb36bfecc3ee44002aba5b92`, 11,554 bytes, SHA-256
`9aeab241694285762574514b34038ca2939de21725b350a8b288e6be3af1b727`.
Packetcraft r20.05 through r20.05c and the official later AmbiqSuite R4.4.1
import share blob `7d66f73b3246b7735a07a5a7c4572c0f6d82cfcb`, 11,789 bytes,
SHA-256
`88ff7fdfac976a70eaa3e3457d8c7123675a39311ddb21480d6699d939ffa241`.
The file is Apache-2.0; Packetcraft r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6` is the public historical route.

Stock `dmSecHciHandler [0x004D2364,0x004D2440)` contains the r20/R4-only
branch that rejects a nonzero EDIV/Rand LTK request when
`SmpDmLescEnabled(connId)` is true. The older r19/AmbiqSuite 2.x body lacks
that branch. This is a behavioral lower bound, not merely a shifted message
constant. The later AmbiqAI R4.4.1 import is byte-identical corroboration, not
the unresolved historical producing commit.

## ABI and behavior

`dmSecFcnIf [0x0078A898,0x0078A8A4)` contains
`{dmSecReset, dmSecHciHandler, dmSecMsgHandler}` and hashes to
`480092e342ed56020f154b848f6f5b49b0ddcfbb3ed7f89e8366f979e8cf0403`.
`DmSecInit` installs it at component ID 5 and initializes the two-pointer
`dmSecCb` at `0x20074114` to `calc128Zeros` at `0x007856B0`. The connection
control block `dmConnCb` is at `0x200712A4`. The r20/R4 three-bit message
ABI assigns security events `0x28/0x29` and LESC events `0x40/0x41`.

The HCI handler routes short-term-key requests, positive/negative LTK replies,
and encryption completion. `dmSecMsgHandler` handles encryption and LTK reply
messages. `DmSmpCbackExec` forwards successful pair/encrypt events to the ATT
callback before the application callback. `DmSecAuthRsp` allocates a 22-byte
SMP message and copies up to 16 authentication bytes; its source assertion is
compiled out in stock. Reset calls `SmpDbInit`.

## Lorelei handoff

The repository preserves
`research/readiness/dm-sec/`, 6,171 bytes, SHA-256
`f447f92ed42f6c9049e033b1b3763be9e1b1a1232afa0e36d5a0d498ad9e5838`.
Its fifteen inner hashes cover all 12 public functions, a 21-input closure,
22 provider seams, Os/O1 objects, and two live zero-unresolved links. The
build uses the byte-identical public r20.05c source; the differing R4
`dm_api.h` is recorded identity-only, so no exact full R4 build configuration
is claimed. Firmware, source/header bytes, objects, ELFs, disassembly, and
caches are excluded.

Reproduce the guarded checks with:

```sh
python3 tools/analyze_g2_cordio_dm_sec.py --json
python3 tools/verify_research_corpus.py --json
```

`dm_sec_lesc.c` at component ID 8 is also production-routed. The remaining
small security-role dependencies are `dm_sec_slave.c` and `dm_sec_master.c`;
their hardware-facing validation shares the blocked Cordio controller row.
