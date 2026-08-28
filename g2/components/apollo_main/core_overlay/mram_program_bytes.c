/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded protected-MRAM byte-program wrapper matched to stock entry
 * 0x0047CBE8.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_program_bytes_uintptr;

typedef unsigned int (*open_cfw_mram_program_bytes_function)(
    unsigned int,
    const void *,
    void *,
    unsigned int
);

#ifndef OPEN_CFW_MRAM_PROGRAM_BYTES_IRQ_DISABLE
#define OPEN_CFW_MRAM_PROGRAM_BYTES_IRQ_DISABLE() \
    open_cfw_lv_irq_disable()
#endif
#ifndef OPEN_CFW_MRAM_PROGRAM_BYTES_PROGRAM
#define OPEN_CFW_MRAM_PROGRAM_BYTES_PROGRAM(key, source, destination, words) \
    (((open_cfw_mram_program_bytes_function) \
        (open_cfw_mram_program_bytes_uintptr)0x004D0A2DU)( \
            (key), \
            (source), \
            (destination), \
            (words) \
        ))
#endif
#ifndef OPEN_CFW_MRAM_PROGRAM_BYTES_PRIMASK_RESTORE
static __attribute__((always_inline)) inline void
open_cfw_mram_program_bytes_primask_restore(unsigned int value)
{
    __asm__ volatile(
        "msr primask, %0"
        :
        : "r"(value)
        : "memory"
    );
}

#define OPEN_CFW_MRAM_PROGRAM_BYTES_PRIMASK_RESTORE(value) \
    open_cfw_mram_program_bytes_primask_restore(value)
#endif

unsigned int open_cfw_lv_irq_disable(void);

__attribute__((used, noinline))
void open_cfw_mram_program_bytes(
    void *destination,
    const void *source,
    unsigned int size
)
{
    unsigned int words = (size + 3U) >> 2U;
    unsigned int primask = OPEN_CFW_MRAM_PROGRAM_BYTES_IRQ_DISABLE();

    (void)OPEN_CFW_MRAM_PROGRAM_BYTES_PROGRAM(
        0x12344321U,
        source,
        destination,
        words
    );
    OPEN_CFW_MRAM_PROGRAM_BYTES_PRIMASK_RESTORE(primask);
}

#undef OPEN_CFW_MRAM_PROGRAM_BYTES_PRIMASK_RESTORE
#undef OPEN_CFW_MRAM_PROGRAM_BYTES_PROGRAM
#undef OPEN_CFW_MRAM_PROGRAM_BYTES_IRQ_DISABLE
