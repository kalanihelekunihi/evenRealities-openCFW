/* SPDX-License-Identifier: MIT
 * Three callback dispatch bodies at stage-2 0x10003418, 0x1000342c,
 * and 0x10003444. The callback slots and 0xffffffff missing-result
 * behavior follow retained pseudocode; the full containing descriptor
 * remains a product-owned data/layout contract.
 */
#include <stdint.h>

static uintptr_t callback_at(const void *descriptor, uint32_t offset)
{
    uintptr_t base = (uintptr_t)descriptor;
    return (uintptr_t)*(const volatile uint32_t *)(base + offset);
}

uint32_t gx8002_uart_stage2_callback_3418(const void *descriptor)
{
    uintptr_t target = callback_at(descriptor, 8);
    if (target == 0) return UINT32_MAX;
    uint32_t (*callback)(void) = (uint32_t (*)(void))(target & ~(uintptr_t)1);
    return callback();
}

uint32_t gx8002_uart_stage2_callback_342c(const void *descriptor,
                                            uint32_t arg0, uint32_t arg1)
{
    uintptr_t target = callback_at(descriptor, 12);
    if (target == 0) return UINT32_MAX;
    uint32_t (*callback)(uint32_t, uint32_t) =
        (uint32_t (*)(uint32_t, uint32_t))(target & ~(uintptr_t)1);
    return callback(arg0, arg1);
}

uint32_t gx8002_uart_stage2_callback_3444(const void *descriptor)
{
    uintptr_t target = callback_at(descriptor, 0x44);
    if (target == 0) return UINT32_MAX;
    uint32_t (*callback)(void) = (uint32_t (*)(void))(target & ~(uintptr_t)1);
    return callback();
}

/* The optional address-adjust callback at +0x6c can rewrite the offset.
 * The write callback at +0x10 returns a signed status whose sign is the
 * native outer result. Stock 0x10003458 has no success path without it.
 */
int32_t gx8002_uart_stage2_callback_write_3458(const void *descriptor,
                                                 uint32_t base,
                                                 uint32_t offset,
                                                 uint32_t value,
                                                 uint32_t options)
{
    uint32_t adjusted = 0;
    uintptr_t adjust_target = callback_at(descriptor, 0x6c);
    if (adjust_target != 0) {
        int32_t (*adjust)(uint32_t, uint32_t, uint32_t *) =
            (int32_t (*)(uint32_t, uint32_t, uint32_t *))
            (adjust_target & ~(uintptr_t)1);
        if (adjust(base, offset, &adjusted) != 0) return -1;
    } else {
        adjusted = offset;
    }
    uintptr_t write_target = callback_at(descriptor, 0x10);
    if (write_target == 0) return -1;
    int32_t (*write)(uint32_t, uint32_t, uint32_t) =
        (int32_t (*)(uint32_t, uint32_t, uint32_t))
        (write_target & ~(uintptr_t)1);
    return write(base + adjusted, value, options) >> 31;
}
