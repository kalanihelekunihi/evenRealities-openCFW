/* SPDX-License-Identifier: MIT
 * Typed 64-word image-A vector source at 0x10023400..0x10023500.
 * Native stock has reset, 31 exception-bridge entries, then 32 compact IRQ
 * entries. Final addresses and even C-SKY code-pointer encoding require
 * linker/scatter qualification; this object deliberately uses relocations.
 */
#include <stdint.h>

extern void gx8002_resident_reset_entry_23500(void);
extern void gx8002_resident_exception_bridge_23640(void);
extern void gx8002_resident_irq_compact_entry_25574(void);

/* Stock 0x10023400 (gx8002_application_vectors_vectors) */
const uintptr_t gx8002_resident_vectors_23400[64]
    __attribute__((section(".gx8002.vectors.23400"), used,
                   aligned(4))) = {
    (uintptr_t)&gx8002_resident_reset_entry_23500, /* 0 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 1 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 2 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 3 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 4 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 5 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 6 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 7 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 8 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 9 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 10 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 11 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 12 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 13 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 14 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 15 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 16 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 17 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 18 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 19 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 20 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 21 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 22 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 23 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 24 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 25 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 26 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 27 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 28 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 29 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 30 */
    (uintptr_t)&gx8002_resident_exception_bridge_23640, /* 31 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 32 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 33 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 34 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 35 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 36 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 37 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 38 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 39 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 40 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 41 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 42 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 43 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 44 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 45 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 46 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 47 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 48 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 49 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 50 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 51 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 52 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 53 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 54 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 55 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 56 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 57 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 58 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 59 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 60 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 61 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 62 */
    (uintptr_t)&gx8002_resident_irq_compact_entry_25574, /* 63 */
};
_Static_assert(sizeof(gx8002_resident_vectors_23400) == 256,
               "native vector table extent");
