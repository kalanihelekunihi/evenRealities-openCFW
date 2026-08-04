/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 generic ring-write primitive at
 * 0x00530084. The exact stock boundary, ring layout, callers, and behavioral
 * evidence are recorded in EVIDENCE.md.
 */

#ifndef OPEN_CFW_RING_WRITE_CRITICAL_ENTER
static inline unsigned int open_cfw_ring_write_critical_enter(void)
{
    unsigned int interrupt_mask;

    __asm__ volatile(
        "mrs %0, primask\n"
        "cpsid i"
        : "=r"(interrupt_mask)
        :
        : "memory"
    );
    return interrupt_mask;
}
#define OPEN_CFW_RING_WRITE_CRITICAL_ENTER() \
    open_cfw_ring_write_critical_enter()
#endif

#ifndef OPEN_CFW_RING_WRITE_CRITICAL_EXIT
static inline void open_cfw_ring_write_critical_exit(
    unsigned int interrupt_mask
)
{
    __asm__ volatile(
        "msr primask, %0"
        :
        : "r"(interrupt_mask)
        : "memory"
    );
}
#define OPEN_CFW_RING_WRITE_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_ring_write_critical_exit(interrupt_mask)
#endif

#ifndef OPEN_CFW_RING_WRITE_INDEX
#define OPEN_CFW_RING_WRITE_INDEX(ring) \
    (*(unsigned int *)(void *)( \
        (unsigned char *)(ring) + 0x00U \
    ))
#endif

#ifndef OPEN_CFW_RING_WRITE_AVAILABLE
#define OPEN_CFW_RING_WRITE_AVAILABLE(ring) \
    (*(unsigned int *)(void *)( \
        (unsigned char *)(ring) + 0x08U \
    ))
#endif

#ifndef OPEN_CFW_RING_WRITE_CAPACITY
#define OPEN_CFW_RING_WRITE_CAPACITY(ring) \
    (*(const unsigned int *)(const void *)( \
        (const unsigned char *)(ring) + 0x0CU \
    ))
#endif

#ifndef OPEN_CFW_RING_WRITE_ELEMENT_SIZE
#define OPEN_CFW_RING_WRITE_ELEMENT_SIZE(ring) \
    (*(const unsigned int *)(const void *)( \
        (const unsigned char *)(ring) + 0x10U \
    ))
#endif

#ifndef OPEN_CFW_RING_WRITE_BUFFER
#define OPEN_CFW_RING_WRITE_BUFFER(ring) \
    ((unsigned char *)( \
        *(const unsigned int *)(const void *)( \
            (const unsigned char *)(ring) + 0x14U \
        ) \
    ))
#endif

/*
 * Stock ABI at 0x00530084. A null source is intentional: a recovered
 * transport caller writes an element directly into ring storage, then uses
 * this routine to advance the write index and publish that element.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ring_write(
    void *ring,
    const void *source,
    unsigned int count
)
{
    unsigned int byte_count =
        OPEN_CFW_RING_WRITE_ELEMENT_SIZE(ring) * count;
    unsigned int byte_offset;
    unsigned int next_index;
    unsigned int interrupt_mask;
    unsigned int result;

    interrupt_mask = OPEN_CFW_RING_WRITE_CRITICAL_ENTER();
    if (
        OPEN_CFW_RING_WRITE_CAPACITY(ring)
            - OPEN_CFW_RING_WRITE_AVAILABLE(ring)
        < byte_count
    ) {
        result = 0U;
    }
    else {
        for (byte_offset = 0U; byte_offset < byte_count; ++byte_offset) {
            /*
             * Preserve the stock routine's single copy-or-reserve loop.
             * The zero-byte barrier prevents -O2 loop unswitching.
             */
            __asm__ volatile("" : "+r"(source));
            if (source != (const void *)0) {
                OPEN_CFW_RING_WRITE_BUFFER(ring)[
                    OPEN_CFW_RING_WRITE_INDEX(ring)
                ] = ((const unsigned char *)source)[byte_offset];
            }
            next_index = OPEN_CFW_RING_WRITE_INDEX(ring) + 1U;
            OPEN_CFW_RING_WRITE_INDEX(ring) =
                next_index
                - OPEN_CFW_RING_WRITE_CAPACITY(ring)
                    * (
                        next_index
                        / OPEN_CFW_RING_WRITE_CAPACITY(ring)
                    );
        }
        OPEN_CFW_RING_WRITE_AVAILABLE(ring) += byte_count;
        result = 1U;
    }
    OPEN_CFW_RING_WRITE_CRITICAL_EXIT(interrupt_mask);
    return result;
}
