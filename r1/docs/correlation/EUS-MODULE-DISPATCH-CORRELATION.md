# EUS module dispatch correlation

## Outcome

The production EUS module ingress and system-module registration dispatcher are now represented
by compilable, bounded C plans. The implementation validates the same header fields, reports the
same module destination, and performs the same 20-key system lookup without importing or calling
any recovered function pointer.

The exact recovered bodies are immutable evidence:

| Recovered extent | Bytes | SHA-256 | Role |
| --- | ---: | --- | --- |
| `0x0008316C..<0x0008321C` | 176 | `ceb1700eb786b7fca329fd99a1ff6a322c857958e2cce5525fa1251aef185618` | top-level EUS module ingress |
| `0x00083CA8..<0x00083CCC` | 36 | `73d1743ef3107d165e196cedff2cec7dce192930e4ba425ac803c9db67b388d7` | system registration dispatcher |

Both were explicit Ghidra analysis seeds omitted from the canonical function CSV. Their independent
prologues, complete return/tail-dispatch paths, adjacent literal pools, and hashes establish the
manual executable extents.

## Recovered contract

The ingress rejects a null packet, fewer than 12 bytes, protocol version other than 100, module
version below 100, and modules other than `00...03` or `7F`. The scatter-loaded module table has
null slots for modules 0 and 3, system dispatcher `0x83CA9` for module 1, and health dispatcher
`0x82BE9` for module 2. Module `7F` takes the separate testable dispatcher at `0x84C98`.

For an accepted packet, the evidence preserves the external session, little-endian serial at byte
3, status byte 5, command/subcommand bytes 6/7, and the diagnostic composite
`module << 16 | command << 8 | subcommand`. This boundary intentionally does not validate the
declared packet length or CRC; those checks belong to the preceding model/reassembly layer.

The exact sorted system identifiers at table `0x0009A4CC` are:

`0001 0002 0003 0004 0005 0007 0008 0009 000A 000B 000C 000E 000F 0010 0011 0012 007E 007F 0082 0083`.

`r1_eus_system_dispatch_plan_build` reproduces the binary-search membership and reports the stable
table index. It retains neither the table's 20 Thumb pointers nor a generic indirect-call seam.

## Safety and tests

`r1_eus_ingress_plan_decode` returns a typed rejection or system/health/testable dispatch intent.
It never invokes a module handler, transmits a response, accesses BLE state, or weakens the normal
model checksum gate. Tests cover every ingress rejection, the two null module slots, all three
dispatch destinations, the production `module_version >= 100` comparison, the deliberately
separate declared-length/CRC responsibility, all 20 system registrations, missing keys, and null
output arguments.

No firmware bytes, recovered pointers, private handlers, transport implementation, signing
material, or device-programming operation are compiled into this closure.
