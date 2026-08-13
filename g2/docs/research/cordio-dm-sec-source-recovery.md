# Cordio DM security source recovery

Status date: 2026-08-09  
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
stock object remains cut forward and no production byte is replaced.

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

The next small linked dependency is `dm_sec_lesc.c` at component ID 8;
closing it precedes the retained Ambiq HCI event producer.
