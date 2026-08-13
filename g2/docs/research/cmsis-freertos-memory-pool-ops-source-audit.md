# CMSIS-FreeRTOS memory-pool operations source audit

Status date: 2026-08-10  
Target: official G2 `s200_v2.2.6.10`

## Result

The entire linked memory-pool operation family is production source-owned from
CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53` under Apache-2.0. This closes
public `osMemoryPoolAlloc` and `osMemoryPoolFree` plus private `CreateBlock`,
`AllocBlock`, and `FreeBlock`. Combined with the prior constructor, no private
CMSIS helper remains stock-backed.

| Function | Stock span | Bytes | Stock SHA-256 |
|---|---:|---:|---|
| `osMemoryPoolAlloc` | `[0x00449D3E,0x00449DD0)` | 146 | `048b16e65e5ea016a21f9061a83050d478077dba03ad165003c9c8e757913913` |
| `osMemoryPoolFree` | `[0x00449DD4,0x00449E8E)` | 186 | `aa5d91c466dd3682f69892e9a19af8fd75c713afcf8938a601c1a8c550cf87e3` |
| `CreateBlock` | `[0x00449E98,0x00449EB8)` | 32 | `d7701236547d60b1b890714e47bffb75daf6ce2c6d0493d4c3a7bfeaf4c54e06` |
| `AllocBlock` | `[0x00449EB8,0x00449ECA)` | 18 | `b3c8efce0ea52d40cabb82e0e1cf6c24dee8b41b00eb94e33ca0562d05ad19d4` |
| `FreeBlock` | `[0x00449ECA,0x00449ED2)` | 8 | `b91ff75c6b7ce4dba1f345e295ac3279f3aa2a6ada13b73105bbb40f78a37cca` |

## Recovered behavior

The adapters preserve the authenticated 116-byte pool control block and
status tag, lazy sequential allocation followed by free-list reuse, task and
ISR semaphore paths, timeout-zero restriction in ISR context, status recheck
after semaphore acquisition, critical/mask protection, capacity checks,
PendSV request after ISR give, and upstream v10.5.1's permissive interior
pointer free quirk. Every fixed dependency is already source-owned.

Seven focused tests pin source/fixture and stock bytes, task allocation and
reuse, validation and take failure, ISR allocation, task free range/capacity
behavior, ISR give/PendSV behavior, and dual-profile production placement.

The five Apple leaves total 392 source bytes at offsets `133400..133794`; the
Linux leaves total 394 source bytes plus four alignment bytes at
`135272..135670`. The current Apple/Linux packages are respectively
`4435684` / `57023a757db5c037fe1c0a63cf8ace615c1dc32a5f4152893e0db00cbe7ae185`
and `4437560` / `7504a643f6acbcfb8fd41742aa22eaa95f31888c1626e526995cacf4fd760981`.
No image was signed or flashed.
