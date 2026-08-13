/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 generic ring-read primitive at
 * 0x005300E2. The exact stock boundary, ring layout, callers, and behavioral
 * evidence are recorded in EVIDENCE.md.
 */

#ifndef OPEN_CFW_RING_READ_CRITICAL_ENTER
static inline unsigned int open_cfw_ring_read_critical_enter(void)
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
#define OPEN_CFW_RING_READ_CRITICAL_ENTER() \
    open_cfw_ring_read_critical_enter()
#endif

#ifndef OPEN_CFW_RING_READ_CRITICAL_EXIT
static inline void open_cfw_ring_read_critical_exit(
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
#define OPEN_CFW_RING_READ_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_ring_read_critical_exit(interrupt_mask)
#endif

#ifndef OPEN_CFW_RING_READ_INDEX
#define OPEN_CFW_RING_READ_INDEX(ring) \
    (*(unsigned int *)(void *)( \
        (unsigned char *)(ring) + 0x04U \
    ))
#endif

#ifndef OPEN_CFW_RING_READ_AVAILABLE
#define OPEN_CFW_RING_READ_AVAILABLE(ring) \
    (*(unsigned int *)(void *)( \
        (unsigned char *)(ring) + 0x08U \
    ))
#endif

#ifndef OPEN_CFW_RING_READ_CAPACITY
#define OPEN_CFW_RING_READ_CAPACITY(ring) \
    (*(const unsigned int *)(const void *)( \
        (const unsigned char *)(ring) + 0x0CU \
    ))
#endif

#ifndef OPEN_CFW_RING_READ_ELEMENT_SIZE
#define OPEN_CFW_RING_READ_ELEMENT_SIZE(ring) \
    (*(const unsigned int *)(const void *)( \
        (const unsigned char *)(ring) + 0x10U \
    ))
#endif

#ifndef OPEN_CFW_RING_READ_BUFFER
#define OPEN_CFW_RING_READ_BUFFER(ring) \
    ((const unsigned char *)( \
        *(const unsigned int *)(const void *)( \
            (const unsigned char *)(ring) + 0x14U \
        ) \
    ))
#endif

/*
 * Stock ABI at 0x005300E2. A null destination is intentional: one recovered
 * transport caller uses it to discard a successfully transmitted element.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ring_read(
    void *ring,
    void *destination,
    unsigned int count
)
{
    unsigned int byte_count =
        OPEN_CFW_RING_READ_ELEMENT_SIZE(ring) * count;
    unsigned int byte_offset;
    unsigned int next_index;
    unsigned int interrupt_mask;
    unsigned int result;

    interrupt_mask = OPEN_CFW_RING_READ_CRITICAL_ENTER();
    if (OPEN_CFW_RING_READ_AVAILABLE(ring) < byte_count) {
        result = 0U;
    }
    else {
        for (byte_offset = 0U; byte_offset < byte_count; ++byte_offset) {
            /*
             * Keep the stock routine's single copy-or-discard loop. Without
             * this zero-byte compiler barrier, -O2 duplicates the complete
             * loop for the invariant null/non-null destination branches.
             */
            __asm__ volatile("" : "+r"(destination));
            if (destination != (void *)0) {
                ((unsigned char *)destination)[byte_offset] =
                    OPEN_CFW_RING_READ_BUFFER(ring)[
                        OPEN_CFW_RING_READ_INDEX(ring)
                    ];
            }
            next_index = OPEN_CFW_RING_READ_INDEX(ring) + 1U;
            OPEN_CFW_RING_READ_INDEX(ring) =
                next_index
                - OPEN_CFW_RING_READ_CAPACITY(ring)
                    * (
                        next_index
                        / OPEN_CFW_RING_READ_CAPACITY(ring)
                    );
        }
        OPEN_CFW_RING_READ_AVAILABLE(ring) -= byte_count;
        result = 1U;
    }
    OPEN_CFW_RING_READ_CRITICAL_EXIT(interrupt_mask);
    return result;
}
