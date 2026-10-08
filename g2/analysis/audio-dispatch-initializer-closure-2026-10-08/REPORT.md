# Authenticated audio dispatcher initialization recovered

Original initializer decoder **0x43A11E**, reconstructed C and independent Python agree on **all 17,752 bytes** of the actual locked application's startup data record. This closes the previously missing initialized-table provenance for **0x20003FBC**; no RAM snapshot was invented. [Results](results.json), [reconstructed unpacker](../../components/audio/startup_unpack_offline/unpack.c), [instructions](original-disassembly.txt).

Reset helper 0x5E4294 calls initializer runner 0x5E42B4 when low-level init returns nonzero. Runner bounds derive from PC-relative literals: table 0x75D3C8..0x75D410. Each row begins with signed relative callback displacement; callback returns pointer to next row. The first zero-initializer describes BSS beginning at 0x20004558. The selected compressed RAM-data row callback word is at 0x75D3F0; arguments start at **0x75D3F4**. Callback resolves to 0x43A11F (Thumb). Source is record+0x344AA = **0x79189E**; encoded length 0x54E0 means **10,864 compressed bytes**, destination **0x20000000**. Decoder reaches input end 0x79430E and returns next record at 0x75D400. Decoded output ends exactly where BSS begins, 0x20004558.

## Recovered table

Eight rows at 0x20003FBC, stride 8: u16 type, u16 zero padding, Thumb callback pointer.

| Type | Callback pointer | Code entry |
| --- | --- | --- |
| 0 | 0x53C861 | 0x53C860 |
| 1 | 0x53C7B1 | 0x53C7B0 |
| 2 | **0x53C6F3** | **0x53C6F2** |
| 3 | 0x53C777 | 0x53C776 |
| 4 | 0x53C9FB | 0x53C9FA |
| 5 | 0x53CA73 | 0x53CA72 |
| 6 | 0x53C92F | 0x53C92E |
| 8 | 0x53CCA7 | 0x53CCA6 |

Dispatcher 0x53C5AC compares the message's low16-bit type, skips NULL callbacks and invokes the first match. The type2 PCM callback relationship now follows actual startup bytes, rather than only a synthetic table fixture. Type7 has no registered row in this initializer. Later mutation, reset-runner reachability/complete boot and live queue/task scheduling are not executed here; this proves authenticated initialized data and decoder semantics, not a booted lifecycle.

## Decoder semantics and validation

Token low2 bits encode literal count+1; zero expands with a following byte+3. High nibble is match length-2; 15 expands with following byte+15. Literal bytes are copied first. Nonzero match field consumes backward offset low byte and token bits2..3 as high byte; high value3 expands with following byte. Copy is bytewise and permits overlapping back references. Record size bit0 selects SB-relative destination; this actual row has bit0 clear, so no relocation assumption is used.

Original decoder runs directly with the authentic record pointer, no calls/stubs. Independent Python asserts bounded input and valid back references; reconstructed ARM C output is compared separately. Both emulator outputs equal Python across the entire decoded region and retain 64-byte destination guard. Original R0 returns next record; reconstructed helper R0 returns output end by its deliberately different helper interface. C preserves token behavior for valid compressed inputs; it is not a hardened generic decoder or proof of arbitrary malformed-input handling. One full authentic record, not a synthetic fuzz suite, is validated. Other initializer records are not decoded by this batch.

Build/run using build_offline.py then opencfw venv verify.py. No blob was copied into production source, no firmware changed/flash, no index edits/commits. All older sealed evidence remains intact. Remaining high-value leads include other callbacks' behavior and real lifecycle scheduling; this is not global source exhaustion.
