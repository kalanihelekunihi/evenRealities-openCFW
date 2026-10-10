# Independent caller, length and fixture contract

This additive contract constrains the proposed guard comparison. It establishes offline source/stock caller semantics and lineage, not a reachable vulnerability. No live BLE traffic, target-function execution or exploit development occurred.

## Length and pointer ownership

Public r20.05c and supplied SDK define the callback as `void(uint16_t handle, uint16_t len, uint8_t *pPacket)`. `len` is the L2CAP **payload** length, excluding the four-byte L2CAP header and four-byte HCI ACL header. `pPacket` still points at the HCI ACL packet's first byte. The callback does not receive a pointer advanced to its payload.

Authenticated stock `l2cHciAclCback`, 0x5308E6..0x530A9C (438 bytes), independently confirms this layout:

- It reads handle at packet +0 and masks to 12 bits; HCI data length at +2.
- At 0x53090C it compares zero-extended HCI length with 4 before reading L2CAP length at +4. Below 4 it substitutes zero payload length.
- At 0x530924..0x53092C it compares HCI length with zero-extended L2CAP length plus 4, using a 32-bit addition/comparison. This is not a wrapping 16-bit sum.
- On equality it reads CID at +6. For LE signaling CID 5, 0x53094A..0x530956 passes r0=masked handle, r1=zero-extended payload length, r2=the **original** packet pointer, through control block +8.
- After the callback returns, all paths join at 0x530A94 and call canonical `WsfMsgFree` at 0x4BF9B0 with that original pointer. Callback does not acquire ownership or free it.

The verified control-block literal is 0x200737D8. Authenticated `L2cInit` writes Thumb pointer 0x53076F into +8, binding the proposed 0x53076E target; it supplies ACL callback pointer 0x5308E7 at its registration call. The source header's callback order matches offsets +0 ATT, +4 SMP, +8 signaling, +24 master signaling, +28 slave signaling, +32 other CID. `CALLER-ABI-RECEIPT.json` retains literal values and call ABI; disassembly files retain the complete caller and initializer instruction extents. No canonical symbol confidence was changed.

## Minimum headers and preconditions

There are two distinct four-byte headers: the L2CAP framing header is included in HCI length, while the signaling command header lies **inside** L2CAP payload. Framing equality does not guarantee a signaling payload of at least four bytes. The caller can dispatch lengths 0..3 if its HCI length is payload length +4 and CID is signaling. This is a static caller-admission fact, not proof that actual upstream delivery permits such input.

The supplied guard checks `len < L2C_SIG_HDR_LEN`, where the constant is 4, before connection lookup. Public r20.05c lacks that local check. Master/slave source handlers advance by `L2C_PAYLOAD_START` before reading code, identifier and parameter length. They therefore have a precondition that four signaling-header bytes are readable. Their later length/identifier checks do not themselves establish that precondition before those initial reads. The dependency member hashes and constants are in `DEPENDENCY-CONTRACT-PROVENANCE.json`.

Do not infer allocation size from encoded packet length alone. The ACL callback's own four-byte initial HCI-header read presumes readable storage; end-to-end controller transport, reassembly/allocation limits, active connection role and callback installation are not established by this bounded caller audit. No end-to-end vulnerability conclusion is admitted. Actual downstream stock parser bodies are also outside this source/ABI contract.

For this authenticated caller, framing equality additionally requires payload length <=65531, because HCI length is 16-bit and payload+4 is compared in 32 bits. The previously proposed direct-target length-65535 case remains useful only as an ABI/unsigned-length fixture; it is **not** reachable through this caller's equality branch. Do not count it as a transport-admission case.

## Safe offline fixture constraints

- Model the actual 32-bit Arm callback ABI: r0/r1 contain zero-extended 16-bit values, r2 is a guest pointer; callback slots are 32-bit Thumb pointers. Host pointer sizes must not be substituted into the control-block layout.
- Give every synthetic direct-target packet at least 12 initialized readable bytes (4 HCI +4 L2CAP +4 signaling header), even for a declared payload length 0..3. For longer cases, allocate the full declared framing size when testing any parser that reads it. Short logical lengths must not be implemented as short allocations.
- Stub role/connection providers and master/slave callbacks to record call order and arguments without reading beyond the fixture buffer. Direct-target tests have no deallocation; caller-composition tests use a recording free stub and require exactly one free after dispatch returns.
- Hold the packet pointer stable and use readable aligned control state at its verified offsets. A source mock must mirror 32-bit state layout or explicitly map fields; native host C structures are not a stock ABI proof.
- Freeze trace behavior as a logged stub or documented disabled configuration. Do not let a real logger, transport or scheduler turn a direct call-order test into platform work.
- Owner's target proof must preserve complete function bytes/control flow. Synthetic fixtures prove bounded semantic ordering, not live delivery or producing revision.

## Lineage conclusion

The source-only distinction remains pre-lookup length guard versus no guard. SDK 5.2 is a concrete guard-bearing source variant; the existing public r20.05c pin is a no-local-guard comparator. A match can select that behavioral variant but cannot establish the private stock revision or security impact. All work stayed in this isolated analysis directory, preserving production, index and sealed evidence.
