# Stock ESS discovery and MTU identity

This batch links the previously recovered 205-byte audio value to the actual
registered GATT service, and separates the notification size check from the
firmware's MTU negotiation behavior. These are manual behavioral reconstructions,
not firmware patches or source-completeness claims.

## Evidence and verification

Image `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`;
Thumb, runtime address = file offset + `0x437fe0`.
`verify.py` authenticates the image and five code ranges, runs the original
initializer `0x43a11e` on descriptor `0x75d3f4`, and verifies decoded SRAM SHA-256
`df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743`.
It executes the original registration wrappers, MTU setter/accessor, and server
MTU request handler. **13 cases pass**; `validation.json` includes arguments,
GATT rows, CCC rows, and response bytes. `disassembly.txt` binds code to hashes.

Providers for connection state, feature flags, logging, allocation, callback,
GATT insertion and L2CAP are explicit stubs. Table recovery and handler arithmetic
are established offline; this does not reproduce live discovery, radio delivery,
controller limits, scheduling, or a real peer negotiation. The test controller
reports ACL RX maximum251, so its local cap is247. Its configuration pointer is
from freshly initialized stock SRAM. An initially swapped pair of feature/ACL
provider hooks failed closed with an unmapped-write error; the corrected mapping
is resolved against the corpus symbols and all final cases pass.

## Actual service and attributes

`bleStackRegister` (`0x4b7ec2`, static call-chain evidence) calls `0x5361f6` with
read callback0 and write callback `essWriteCallback` (`0x4be2b4`, Thumb pointer
`0x4be2b5`), then `0x5361ec`. Original wrapper execution stores these callbacks
and passes group `0x20003b38` to `AttsAddGroup` (`0x5353ae`). The group contains
attribute table `0x6de9d4`, start `0x0860`, end `0x0865`.

Each table entry is16 bytes: UUID pointer+0, value pointer+4, current-length
pointer+8, maximum-length u16+12, settings byte+14, permission byte+15.
UUIDs below are canonical text; firmware stores the full128-bit values least
significant byte first. Settings/permissions are preserved numerically in the
receipt; their entire bitfield meaning is not inferred here.

| Handle | Type / UUID | Value / meaning |
| --- | --- | --- |
| 0860 | Primary Service2800 | `00002760-08c2-11e1-9073-0e8ac72e6450` |
| 0861 | Characteristic2803 | property04, value0862, UUID ending6401 |
| 0862 | `00002760-08c2-11e1-9073-0e8ac72e6401` | Write Without Response declaration; maximum512 |
| 0863 | Characteristic2803 | property10, value0864, UUID ending6402 |
| 0864 | `00002760-08c2-11e1-9073-0e8ac72e6402` | Notify declaration; maximum512; raw audio value travels here |
| 0865 | CCC2902 | length2, initial backing pointer `0x20074f3e` |

Service bytes at `0x7894f0`: `50642ec78a0e7390e111c20860270000`.
Notify UUID bytes at `0x7894e0`: `02642ec78a0e7390e111c20860270000`.
Notify declaration at `0x783af0`: `10 6408 02642ec78a0e7390e111c20860270000`.
CCC configuration array `0x7518c0` has six six-byte rows. Row3 is
`6508 0100 0000`: handle0865 and notification bit1. This matches the prior
original-instruction proof that `essProcCccState` checks index3 and value1.
The registration wrappers were absent as individual decompiler files; their
10/8-byte executable ranges were decoded directly, excluding literal pools.

## MTU: source gate versus protocol-sized packet

The characteristic **value is205 bytes**. The raw ATT packet starts
`1b 64 08` (notification opcode plus little-endian handle), then those205 bytes.
Thus the full ATT notification is**208 bytes**, and a negotiated ATT MTU208
can contain it.211 would count the same three-byte ATT header twice.
This does not imply205/208 bytes include lower-layer L2CAP/link-layer framing.

The source gate is **stored ATT MTU >= value_length+3**, not an effective
payload-MTU comparison. `attsHandleValueIndNtf` (`0x533c6c`) uses the server CCB
from `attsCcbByConnId`, dereferences its core pointer at+16, and reads u16 at
core+4*bearer (`LDRH 0x533c98`). `ADD #3` at `0x533cec`, `CMP 0x533cee` lead to
status77 rejection at `0x533d96` when too small. The earlier batch tests207
reject/208accept. `attSetMtu` (`0x4b503c`) stores the minimum of its two u16
inputs at that same core slot, without subtracting3. `AttGetMtu` (`0x4b5204`)
returns the core's first u16 unchanged. New tests cover both bearer0 and1.

**However, that stored number is not unconditional proof of a correct peer
negotiation.** In `attsProcMtuReq` (`0x56c6fc`), the original instructions decode
the incoming peer u16LE, raise any value below247 to247, then pass it to
`attSetMtu` together with `min(configured_mtu, HciGetMaxRxAclLen()-4)`.
With test ACL cap251 and stock configuration, peer requests23,207,208,247 and517
all produce stored247 and response `03 f7 00`. Feature bit1 instead takes the
error branch and leaves the old MTU unchanged. These are executed stock
instructions with explicit synthetic providers, not a claim that a real phone
has accepted247 after requesting23. The setter itself correctly takes a minimum;
the caller changes the peer input first. Client-response behavior has similar
static decompiler evidence but is **not instruction-tested by this batch**.

## App use and remaining boundaries

Discover the service and notification UUIDs from `ess_gatt.h`; subscribe to the
notify characteristic's CCC through the platform BLE API. Avoid hardcoding the
stock handles for other firmware versions. Feed the205-byte notification value
to `g2_ess_audio_value` in the previous batch. Use the208-byte parser only for
raw ATT captures that include the opcode/handle. Request/confirm an ATT MTU
large enough for208 bytes (247 matches the stock request path), and do not treat
a firmware-only stored247 as proof of the peer's effective receive agreement.

The table's maximum512 is a storage/declaration limit, not a claim the current
stream emits512 or fragments across notifications. There is still no explicit
encoder-success flag in the205-byte body; applications can only infer failures
from decode results/content and gaps, which have other causes too.

No hardware trace was available to establish whether the low-peer-MTU clamp
causes observable delivery failure, or how a specific mobile BLE stack reacts.
A bounded next input is a raw MTU exchange plus first ESS notifications from a
peer requesting23 versus247. No firmware patch is justified solely by the
synthetic trace. The next useful static batch could decode `essWriteCallback`
commands at0862; this batch establishes discovery, not their command grammar.
