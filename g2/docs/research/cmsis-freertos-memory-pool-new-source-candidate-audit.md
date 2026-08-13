# CMSIS-FreeRTOS memory-pool constructor source-candidate audit

Status: production-integrated and independently replayed
Target: official G2 `s200_v2.2.6.10` Apollo-main application  
Scope: `osMemoryPoolNew`

## Result

`osMemoryPoolNew` is source-closable over existing OpenCFW providers. Its
complete stock entry is `[0x00449C14,0x00449D3E)` (298 bytes, SHA-256
`c108de1748627d51427e2771a74fe9b3ddcd5b53c5816ebb2f82972e8bdc6136`)
and has one external caller. The selected oracle is CMSIS-FreeRTOS v10.5.1
commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`; the exact source blob was
first introduced by `13acfbef7be85119fc6bc56832c455d4547d92c7`.

## Recovered ABI and behavior

- `MemPool_t` is 116 bytes: 36 bytes of pool metadata followed by the known
  80-byte G2 `StaticSemaphore_t` at offset `0x24`.
- The block array size uses 32-bit `(((block_size + 3) >> 2) * count) << 2`
  arithmetic, preserving target wrap behavior.
- Status begins at `0x5EED0000`; bits zero and one tag dynamically allocated
  control and array storage respectively.
- The availability semaphore is always the source-owned static counting
  semaphore embedded in the pool control block.
- The v10.5.1 source/stock quirk for a non-null undersized supplied control or
  array buffer is preserved: validation leaves its mode at `-1`, but the
  non-null pointer is still selected. A static control block whose stale array
  pointer survives semaphore-creation failure is likewise preserved. These are
  authenticated compatibility behaviors, not recommended new API policy.
- Failure cleanup frees only a dynamically allocated pool control block, as in
  the selected source.

All five fixed call edges are source-owned: private `IRQ_Context`, heap_4
allocate/free, and the static counting-semaphore constructor. No TCB field,
WSF hook, ISR queue-receive path, or private memory-pool list helper is used.

## Candidate pins

The source is 5,668 bytes / SHA-256
`7f39930cd3a7a6532d733d443efb211c40594d116ec17d03c2ccb0602a732bb1`.
The host fixture is 4,155 bytes / SHA-256
`4f4f6dcd73eec33401c571576a534a26410923a0f936966ab20db7adcf577ae4`.
Apple clang emits a 254-byte unrelocated body with SHA-256
`8ff778cf06ce1652e66b260a59b6f277295b727688d5c2ae080ea8250f96fca3`.
Seven focused tests pin stock/source/target identity, validation, four storage
combinations, rounding and field initialization, the compatibility quirks,
allocation/semaphore cleanup, and production admission.

## Production admission

The complete public stock entry redirects to the source leaf; no private pool
helper is part of this constructor. Both compiler profiles were recorded once
and then reproduced by ordinary fail-closed component and package builds.

| Profile | Linked leaf | Overlay | Component/provider | Package |
|---|---|---|---|---|
| Apple clang 21 | `254` / `ff4675969e47e4558d41506f657230e7dda578b43b342a0831f830ac777ebe82` at `132792` | `133046` / `9c0137cff9d27883a6775a986a7b2899d25ef3002afc74397b2a023d392722a8` | `3656442` / `4fcab7c117664d5a1f5fe0a521182eb96ce9bbd53ef9dfb72a72feb03a31d3d1` | `4434936` / `584c83efd097a561aa388b3083adb9df89fb92076f406444a022a40aa8610530` |
| Homebrew clang 22.1.8 | `250` / `fc11de9c673f30bef9ccbb880a4d4abd1de2ca27951f32cda68e10f190cb16eb` at `134672` | `134922` / `9a0aee259518e62b85c319fed76f66de6c3aa1a290ded5adfae6579e50893b56` | `3658318` / `32592835229627f9b36ffeb73a82265f2d6e2b22f92b1ae26d096d0f3f5132ea` | `4436812` / `8e2f22f1fbe488c5704450da04d1c717b9c966e0a5716a6de21be051df33e62b` |

The canonical package now source-owns 25 of the 38 linked public CMSIS APIs,
plus private `IRQ_Context` and `TimerCallback`. Thirteen public APIs and the
three private memory-pool list helpers remain stock-backed.

## Reproduction

```sh
make -C openCFW cmsis-freertos-memory-pool-new
```
