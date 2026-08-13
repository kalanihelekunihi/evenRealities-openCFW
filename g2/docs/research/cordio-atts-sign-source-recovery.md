# Cordio ATT server signing partial-inclusion audit

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The stock `atts_sign.c` translation unit is only partially linked. Four
configuration/state functions contribute 370 code bytes inside the 408-byte
physical object `[0x0052DA58,0x0052DBF0)`, SHA-256
`b62a735715edb1214ec0e9f1a9dd30f72cc928a1ac993930947f9b34a88853a8`:

- `attsSignCcbByConnId [0x0052DA58,0x0052DB92)`;
- `AttsSetCsrk [0x0052DBB8,0x0052DBD6)`;
- `AttsSetSignCounter [0x0052DBD6,0x0052DBE4)`; and
- `AttsGetSignCounter [0x0052DBE4,0x0052DBF0)`.

The 38-byte owned gap contains alignment, trace-category/literal cells, the
retained `atts_sign.c` path, and the sole `attsSignCb` address literal. The
four source bodies concatenate to SHA-256
`ae182809d1df2204330f054459763a31c5ef66cea9854d869ea703d23c055e36`.
Nine exact-entry calls, no stored function pointer, no stored strict-interior
address, and no exterior direct branch to an interior close ingress.

The other four definitions are dead-stripped:
`attsSignedWriteStart`, `attsProcSignedWrite`, `attsSignMsgCback`, and
`AttsSignInit`. Thus the application can save and restore a peer CSRK and
sign counter, but this firmware does not install or execute ATT Signed Write
Command verification. Stock remains cut forward; no production byte changes.

## Processing-path exclusion

`AttsInit [0x005351DC,...]` stores `attEmptyHandler` at
`attsCb.signMsgCback` (`attsCb + 0x264`) and has one caller at `0x004B8062`.
There is no later signing-callback installation and no direct literal for the
slot at `0x2006E854`. The image's only two `SecCmac` calls are the already
bounded database-hash and SMP paths at `0x00535270` and `0x0056CEE2`; neither
belongs to `atts_sign.c`. The three processing-only diagnostics—`ATTS CSRK
not set`, `Signed write counter failed`, and `Signed write sig failed`—are
also absent.

This combination is stronger than absence of a public initializer call alone:
the callback remains the default empty handler, the signed-write parser and
CMAC provider edge are absent, and the object's source-order gap closes before
the surviving APIs. The retained path is expected because the assertion-heavy
connection-record helper survives.

## ABI and behavior

`attsSignCb` starts at `0x2007335C` and occupies 56 bytes: three 16-byte
connection records followed by an 8-byte queue. Each record contains
`signCounter +0`, `pCsrk +4`, `pBuf +8`, and `authenticated +0x0C`.
`attsSignCcbByConnId` validates a nonzero connection ID through the stock
trace/assert expansion and returns `base + (connId - 1) * 16`.

`AttsSetCsrk` stores both the CSRK pointer and the authentication flag;
`AttsSetSignCounter` and `AttsGetSignCounter` write/read the first word. The
two CSRK setters are called at `0x004B3852` and `0x00534594`, the two counter
setters at `0x004B3860` and `0x005345A4`, and the getter at `0x005346D6`.
The calls at `0x00534594/0x005345A4` are in
`appServerSetSigningInfo [0x0053456C,0x005345AA)`; the getter is consumed by
the server connection callback.

## Source lineage

AmbiqSuite R2.4.2/R2.5.1 and Packetcraft r19 expose a 12-byte connection
record and two-argument `AttsSetCsrk`. Packetcraft r20.05 through r20.05c
keeps that older API. Stock instead has a 16-byte record and a third
`authenticated` argument, exactly matching the later official AmbiqSuite
R4.4.1 import at AmbiqAI/neuralSPOT commit
`4264b9309e03064ffad13a0468d5d0c1110c5288`: Git blob
`c2f34343cd43e4633ec50f4899ab3e7af9bee820`, 13,134 bytes, SHA-256
`9a4b42b2e6cb0549eabfa4479a3a7516b8030c63f4497fcac227cb6a1bd7a81d`.

The individual file is Apache-2.0. The R4 import is an exact reconstruction
oracle for the linked ABI and behavior, not the unresolved historical commit
that produced G2. Stock's retained assertion line is two lines later than the
official import, so whole-file textual identity is not claimed.

## Reproduction

The source inventory, function bytes, literal pool, calls, global references,
callback default, CMAC closure, marker absence, and pointer/interior scans are
guarded by:

```sh
python3 tools/analyze_g2_cordio_atts_sign.py --json
python3 -m unittest tests.test_analyze_g2_cordio_atts_sign
```

The next bounded ATT server target is `atts_ind.c`, whose retained source path
and indication state connect directly to the now-evidenced `atts_main.c`
control-block fields.
