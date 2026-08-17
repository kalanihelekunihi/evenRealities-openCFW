# R1 nonvolatile recovery correlation

## Decision

The recovered `nvRecover` path is R1 product behavior, not Nordic SDK or third-party library code.
Six functions / 1,954 executable bytes are closed as `r1_product_specific` with disposition
`clean_room_behavior_only_security_preserving`. Two functions / 1,458 bytes are in Ghidra's
inventory; four valid functions / 496 bytes were omitted because inline diagnostic strings or
table-only registration interrupted automatic discovery.

| Entry | Bytes | Role |
| --- | ---: | --- |
| `0x0007B634` | 474 | build and validate the local 116-byte report body |
| `0x0007BBE8` | 174 | allocate, checksum, and send the identity-bearing report |
| `0x0007BD68` | 984 | CRC-check and fill-only merge into three KV records |
| `0x0007C450` | 108 | command/length/CRC dispatcher |
| `0x000839B4` | 38 | current-phone-session outbound response wrapper |
| `0x00084150` | 176 | registered system-`0x11` envelope handler |

The system table record at `0x0009A53C` is raw `1100000051410800`, registering Thumb handler
`0x00084151` for subcommand `0x11`. That handler extracts command UInt8, body-length UInt16LE,
body-CRC UInt16LE, and the body pointer, then takes the exact direct route
`0x000841FA -> 0x0007C450`. Commands 0 and 1 return without effect.
Command 2 tail-calls `0x0007BD68` at `0x0007C46E` only for an exact 116-byte body and nonzero CRC;
otherwise it calls the local report sender at `0x0007C4B6`. The sender invokes report builder
`0x0007B634` at `0x0007BC02`, computes CRC-16/MODBUS, and calls the outbound wrapper at
`0x0007BC22`. The wrapper reads the current phone session and passes identifier `0x11`, response
type 1, serial 0, and envelope length `body_length + 5` to the existing system response path.

## Recovery body and records

The five-byte envelope is command UInt8, body length UInt16LE, and body CRC UInt16LE. The checksum
uses reflected polynomial `0xA001`, initial value `0xFFFF`, and no final XOR. The body is:

| Offset | Bytes | Field |
| ---: | ---: | --- |
| `0x00` | 30 | product BSN bytes |
| `0x1E` | 1 | product BSN length |
| `0x1F` | 30 | product serial-number bytes |
| `0x3D` | 1 | product serial-number length |
| `0x3E` | 6 | temperature calibration |
| `0x44` | 6 | three signed Int16LE accelerometer offsets |
| `0x4A` | 18 | reserved, zero in a local report |
| `0x5C` | 1 | battery type |
| `0x5D` | 1 | reserved |
| `0x5E` | 2 | signed Int16LE voltage compensation |
| `0x60` | 1 | ring size |
| `0x61` | 19 | reserved, zero in a local report |

The fields map to separately persisted `nv_r1` (124 bytes), `power` (4 bytes), and `r_size`
(1 byte) records. The local report is considered valid only when battery type is 1...4, voltage
compensation is -500...500 except -1, ring size is 6...15, and BSN length is 1...30. Zero voltage
compensation is report-valid.

## Fill-only merge

The merge independently recomputes the body CRC before changing its output. It never replaces a
locally valid field:

- battery type imports only when local is outside 1...4 and incoming is inside 1...4;
- ring size imports only when local is outside 6...15 and incoming is inside 6...15;
- BSN and serial import only when the local length is `0xFF` and incoming length is 1...30;
- all six temperature-calibration bytes import only when the local first byte is `0xFF` and the
  incoming first byte is not `0xFF`;
- all three accelerometer offsets import only when the local first Int16 is -1 and the incoming
  first Int16 is not -1; and
- voltage compensation imports only when local is outside -500...500, -1, or zero, and incoming is
  inside that range but neither -1 nor zero.

The last rule intentionally preserves the stock asymmetry: zero may be reported but is never
restored. Configuration, power, and ring-size changes are tracked independently.

## Clean-room implementation and security boundary

`r1_nv_recovery.c` implements a bounded pure report builder
and fill-only merge planner over caller-owned state. It performs no flash write, commit, BLE send,
allocation, logging, or device access. Tests cover null/length/CRC rejection, all-field recovery,
valid-local preservation, invalid-incoming rejection, reserved-byte behavior, and the zero-voltage
asymmetry.

`r1_nv_recovery_command_handler_plan_decode` additionally provides the strict clean form of the
registered handler and command dispatcher. It requires a complete five-byte envelope plus exactly
the declared backing body, ignores commands other than 2, reports the withheld local-report intent
for command 2 with a non-116-byte body or zero CRC, and reports merge-dispatch intent only for the
116-byte/nonzero-CRC route. It copies the bounded body for composition with the existing
CRC-validating merge planner but invokes neither report nor merge itself. The stock short-backing
read is not reproduced.

`r1_nv_recovery_outbound_response_plan_build` binds the 38-byte wrapper without exposing its
transport. It requires a self-consistent five-byte envelope and bounded body, preserves identifier
`0x11`, response type 1, serial 0, and the current phone session, and records no-send when that
session is `0xFFFF`. It neither returns the identity payload nor invokes a sender. Tests cover
short, trailing, oversized-body, valid-session, and no-active-session cases.

The same portable module exposes a strict decoder for the six calibration bytes at `nv_r1` offset
`0x3E`: direction `0` subtracts, direction `1` adds, other values disable that channel, and an
all-`0xFF` record is reported absent. The source-built Zephyr GXT310 adapter consumes this value
read-only after KV startup. It does not invoke the destructive recovery merge or mutate `nv_r1`.

The adjacent six accelerometer bytes at offset `0x44` have a separate strict
three-Int16LE decoder. All three `-1` values mean absent, matching the stock
batch producer's erased-record check; other tuples are retained exactly. The
source-built Zephyr `"acc"` stream adds present offsets to normalized XYZ with
the recovered 16-bit wrap behavior and exposes no calibration writer.

A second strict decoder covers the exact four-byte `power` class: battery type is byte 0 and
signed Int16LE voltage compensation is at bytes 2...3. It reports the recovered type-1...4 and
compensation-range validity separately from the raw decoded values. Zephyr uses a valid type to
configure its runtime controller and exposes the complete decoded record read-only; it does not
enable the recovery merge or a periodic sampler.

The one-byte `r_size` class has its own strict decoder and is valid only for 6...15. Zephyr exposes
a valid value read-only, but does not infer the separate IQS7211E physical layout from ring size or
use this field to energize touch hardware.

The normal dispatcher continues to refuse live `nvRecover`. This is intentional hardening from the
firmware security audit: the body carries two identifiers plus sensor and battery calibration, and
a valid merge can mutate persistent device identity/configuration. The report sender and live
persistence surface are documented and byte-pinned but not exposed by OpenR1.

The static verifier pins all six bodies, the four manual function extents, complete direct-caller
maps, dispatcher/report-builder edges, and exact diagnostics:

```sh
python3 tools/evidence/summarize_r1_nv_recovery_closure.py
```
