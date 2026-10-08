# Next asynchronous boundary: publisher0x42c45a..0x42c4c6

Static disassembly of the same locked bootloader (SHA f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5; load0x410000). This is newly readable pseudocode, not linked/tested source. Context validity/module and record capacity must be established by callers before using it.

```c
// Exact publisher body has no validation, allocation, callback or release.
uint32_t next = ctx->word_at_0x850 + 1; // wrapping ARM32 addition
uint32_t capacity = ctx->word_at_0x848;
// ARM UDIV-zero behavior assumes DIV_0_TRP clear; do not use C %0.
uint32_t quotient = capacity ? next / capacity : 0;
uint32_t index = next - capacity * quotient;
volatile uint32_t *record = (void *)(ctx->word_at_0x854 + (index << 5));
uintptr_t iom = 0x40050000 + (ctx->module << 12);
MMIO32(iom + 0x128) = record[0];
MMIO32(iom + 0x2c4) = record[1];
MMIO32(iom + 0x218) = 0;
MMIO32(iom + 0x21c) = record[2];
MMIO32(iom + 0x220) = record[3];
MMIO32(iom + 0x218) = record[4];
MMIO32(iom + 0x120) = record[5];
```

Records have32-byte stride; this body reads only their first24 bytes. It never updates the context head/capacity/record pointer and does not free/copy records. Read/publish ordering is relevant to any future owned-buffer scheme. Actual consumption, callbacks, head movement and lifetime belong to service42c6f8/callers; their concurrency semantics remain unresolved. No claim of safe release or physical command execution is made.
