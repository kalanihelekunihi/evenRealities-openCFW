# Protocol response correlation

The 364-byte function `0x000828B4..<0x00082A20`, SHA-256
`fce00c9e829f4cb27b24679f4a991108d3b0dc448eadc05aee034f065e42c52e`,
is the R1-owned final phone-protocol response encoder/send orchestrator. Seven
direct `BL` callsites (`0x0008283E`, `0x00082876`, `0x000828AE`, `0x00082B8E`,
`0x00082BCC`, `0x00082F36`, and `0x00084C4E`) feed the common response path.
Its direct packet constructor is the 136-byte function
`0x00082F9C..<0x00083024`, SHA-256
`5a0af8389804a98f224903c1c20174548b449a93f0872dfeb4e509c20928c644`,
called only at `0x00082916`. Both functions' disposition is
`r1_product_specific` / `clean_room_behavior_only`; the closure is two functions / 500 bytes.

The routine rejects a null six-field response header with result 2. It probes
the two external link/session providers and returns 5 when neither is active.
Otherwise it allocates exactly `payload length + 12` bytes through FreeRTOS,
passes the header and optional payload to the packet encoder, invokes the
registered BLE transport callback, and releases the allocation on all
post-allocation paths. Its observed results are 0 for success, 3 for allocation
failure, and 4 for transport failure. The packet header selects protocol
version 100, one of four module-version slots, status, command, subcommand,
serial, encoded length, and checksum. An odd status bit preserves the supplied
serial; an even status selects and post-increments the firmware-generated
serial counter. The constructor calls the shared table-driven primitive at
`0x0005D87C`, initialized to `0xFFFF`, to compute CRC-16/MODBUS over the whole
model while the two checksum bytes are zero.

The clean-room `r1_protocol_send_response` retains that orchestration while
injecting availability probes, serial-counter state, allocator/release, and
transport as typed provider seams. It reuses the existing bounded R1 packet
encoder with the recovered outbound CRC scheme rather than copying recovered
code. Nordic BLE, the registered GATT sender, FreeRTOS allocation, and logging
remain external and are not recreated.

The Nordic SDK 17.1.0 image retains `r1_model_encode` at `0x0003237E`,
`r1_protocol_send_response` at `0x0003264A`, and the response API pointer at
`0x0003CC38`. The verified unsigned image contains 94,804 bytes of text, 236
bytes of data, and 132,544 bytes of BSS; its 95,040-byte BIN has SHA-256
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`, and
the HEX SHA-256 is
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_protocol_response.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
