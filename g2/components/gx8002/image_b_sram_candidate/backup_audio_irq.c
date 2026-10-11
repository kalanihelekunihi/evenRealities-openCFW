/* SPDX-License-Identifier: MIT
 * Image-B audio IRQ, native 0x10015830..0x10015b60. The six event paths
 * retain the native enable/status read order, W1C order and callback order.
 */
#include <stdint.h>

#ifdef GX8002_IMAGE_B_ISR_HOST_TEST
extern uint32_t gx8002_image_b_isr_test_read(uint32_t offset);
extern void gx8002_image_b_isr_test_write(uint32_t offset, uint32_t value);
extern void gx8002_image_b_isr_test_event(uint32_t slot, uint32_t flags);
extern void gx8002_image_b_isr_test_stream(uint32_t slot, uint32_t flags,
                                            uint32_t address[3]);
#define IRQ_READ(offset) gx8002_image_b_isr_test_read(offset)
#define IRQ_WRITE(offset, value) gx8002_image_b_isr_test_write((offset), (value))
#else
#define IRQ_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0a00000) + (offset)))
#define IRQ_READ(offset) IRQ_WORD(offset)
#define IRQ_WRITE(offset, value) (IRQ_WORD(offset) = (value))
#define IRQ_STATE ((volatile uint32_t *)(uintptr_t)UINT32_C(0x20017624))

static void event_callback(uint32_t slot, uint32_t flags)
{
    uint32_t address = IRQ_STATE[slot / 4u];
    if (address != 0u)
        ((int32_t (*)(uint32_t))(uintptr_t)address)(flags);
}

static void stream_callback(uint32_t slot, uint32_t flags, uint32_t address[3])
{
    uint32_t function = IRQ_STATE[slot / 4u];
    if (function != 0u)
        ((int32_t (*)(uint32_t, uint32_t *))(uintptr_t)function)(flags, address);
}
#endif

static uint32_t event_active(uint32_t bit)
{
    uint32_t mask = UINT32_C(1) << bit;
    if ((IRQ_READ(0x100u) & mask) == 0u)
        return 0u;
    return (IRQ_READ(0x104u) & mask) != 0u;
}

static void acknowledge(uint32_t bit)
{
    IRQ_WRITE(0x104u, UINT32_C(1) << bit);
}

int32_t gx8002_image_b_audio_irq_10015830(int32_t irq, void *private_data)
{
    (void)irq;
    (void)private_data;
    /* Native first reads bit 24 at most three times before event handling. */
    if ((IRQ_READ(0x104u) & (1u << 24)) == 0u) {
        if ((IRQ_READ(0x104u) & (1u << 24)) == 0u)
            (void)IRQ_READ(0x104u);
    }

    uint32_t flags = 0u;
    if (event_active(18u)) { acknowledge(18u); flags |= 1u; }
    if (event_active(19u)) { acknowledge(19u); flags |= 2u; }
    if (event_active(20u)) { acknowledge(20u); flags |= 4u; }
    if (flags != 0u) {
#ifdef GX8002_IMAGE_B_ISR_HOST_TEST
        gx8002_image_b_isr_test_event(0x14u, flags);
#else
        event_callback(0x14u, flags);
#endif
    }

    uint32_t record[3] = {0u, 0u, 0u};
    flags = 0u;
    if (event_active(0u)) flags |= 1u;
    record[0] = IRQ_READ(0x124u);
    if (event_active(1u)) flags |= 2u;
    record[1] = IRQ_READ(0x148u);
    if (event_active(2u)) flags |= 4u;
    record[2] = IRQ_READ(0x168u);
    if (flags != 0u) {
#ifdef GX8002_IMAGE_B_ISR_HOST_TEST
        gx8002_image_b_isr_test_stream(0x0cu, flags, record);
#else
        stream_callback(0x0cu, flags, record);
#endif
    }
    if ((flags & 1u) != 0u) acknowledge(0u);
    if ((flags & 2u) != 0u) acknowledge(1u);
    if ((flags & 4u) != 0u) acknowledge(2u);

    uint32_t update[3] = {0u, 0u, 0u};
    flags = 0u;
    if (event_active(3u)) { update[0] = IRQ_READ(0x128u); flags |= 1u; }
    if (event_active(4u)) { update[1] = IRQ_READ(0x14cu); flags |= 2u; }
    if (event_active(5u)) { update[2] = IRQ_READ(0x16cu); flags |= 4u; }
    if (flags != 0u) {
#ifdef GX8002_IMAGE_B_ISR_HOST_TEST
        gx8002_image_b_isr_test_stream(0x10u, flags, update);
#else
        stream_callback(0x10u, flags, update);
#endif
    }
    if ((flags & 1u) != 0u) acknowledge(3u);
    if ((flags & 2u) != 0u) acknowledge(4u);
    if ((flags & 4u) != 0u) acknowledge(5u);

    flags = 0u;
    if (event_active(16u)) { acknowledge(16u); flags |= 1u; }
    if (event_active(17u)) { acknowledge(17u); flags |= 2u; }
#ifdef GX8002_IMAGE_B_ISR_HOST_TEST
    gx8002_image_b_isr_test_event(0x18u, flags);
#else
    event_callback(0x18u, flags);
#endif
    return 0;
}
