# R1 nonvolatile recovery correlation

## Decision

The recovered `nvRecover` path is R1 product behavior, not Nordic SDK or third-party library code.
Four functions / 1,740 executable bytes are closed as `r1_product_specific` with disposition
`clean_room_behavior_only_security_preserving`. Two functions / 1,458 bytes are in Ghidra's
inventory; two valid functions / 282 bytes were omitted because inline diagnostic strings
interrupted automatic discovery.

| Entry | Bytes | Role |
| --- | ---: | --- |
| `0x0007B634` | 474 | build and validate the local 116-byte report body |
| `0x0007BBE8` | 174 | allocate, checksum, and send the identity-bearing report |
| `0x0007BD68` | 984 | CRC-check and fill-only merge into three KV records |
| `0x0007C450` | 108 | command/length/CRC dispatcher |

The exact direct route is `0x000841FA -> 0x0007C450`. Commands 0 and 1 return without effect.
Command 2 tail-calls `0x0007BD68` at `0x0007C46E` only for an exact 116-byte body and nonzero CRC;
otherwise it calls the local report sender at `0x0007C4B6`. The sender invokes report builder
`0x0007B634` at `0x0007BC02`, computes CRC-16/MODBUS, and uses the existing system response path.

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

[`r1_nv_recovery.c`](../../src/r1_nv_recovery.c) implements a bounded pure report builder
and fill-only merge planner over caller-owned state. It performs no flash write, commit, BLE send,
allocation, logging, or device access. Tests cover null/length/CRC rejection, all-field recovery,
valid-local preservation, invalid-incoming rejection, reserved-byte behavior, and the zero-voltage
asymmetry.

The normal dispatcher continues to refuse live `nvRecover`. This is intentional hardening from the
firmware security audit: the body carries two identifiers plus sensor and battery calibration, and
a valid merge can mutate persistent device identity/configuration. The report sender and live
persistence surface are documented and byte-pinned but not exposed by OpenR1.

The static verifier pins all four bodies, the two manual function extents, complete direct-caller
maps, dispatcher/report-builder edges, and exact diagnostics:

```sh
python3 scripts/firmware/summarize_r1_nv_recovery_closure.py
```
