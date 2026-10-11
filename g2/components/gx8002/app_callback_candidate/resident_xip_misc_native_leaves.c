/* SPDX-License-Identifier: MIT
 * Seven independent small image-A XIP bodies with direct native disassembly:
 * 0x10203b38, 0x10204cd4, 0x102055c0, 0x10206908,
 * 0x10208c60, 0x10203598, 0x102077d4. RAM allocation/layout is open.
 */
#include <stdint.h>

extern void gx8002_xip_dma_deallocate_10203a98(uint32_t channel);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);

void gx8002_xip_dma_release_10203b38(uint32_t channel)
{
    gx8002_xip_dma_deallocate_10203a98(channel);
}

int32_t gx8002_xip_aout_get_mute_10204cd4(const void *configuration)
{
    const uint8_t *const bytes = configuration;
    return *(const int16_t *)(const void *)(bytes + 0x10u);
}

uint32_t gx8002_xip_register_get_bit_102055c0(
    volatile const uint32_t *register_word, uint32_t bit)
{
    uint32_t value = *register_word;
    __asm__ volatile("lsr %0, %1" : "+r"(value) : "r"(bit) : "cc");
    return value & 1u;
}

uint32_t gx8002_xip_gsensor_workstate_10206908(void)
{
    volatile const uint32_t *const workstate =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x20026c70);
    uint32_t value = *workstate;
    (void)gx8002_xip_tws_publish_10206c24(
        "gsensor_workstate =%d\n", (int32_t)value);
    return value;
}

void *gx8002_xip_ctc_model_output_10208c60(void *snpu_buffer)
{
    return (uint8_t *)snpu_buffer + 0x2110u;
}

void gx8002_xip_uart_flush_10203598(uint32_t port)
{
    volatile const uint8_t *const channel =
        (volatile const uint8_t *)(uintptr_t)
            (UINT32_C(0x20026a94) + (port << 7u));
    const uint32_t registers =
        *(volatile const uint32_t *)(const void *)(channel + 4u);
    volatile const uint32_t *const status =
        (volatile const uint32_t *)(uintptr_t)(registers + 0x14u);
    while ((*status & 0x40u) == 0u) { }
}

uint32_t gx8002_xip_power_unlock_102077d4(int32_t token)
{
    if (token >= 33) return UINT32_MAX;
    volatile uint32_t *const flags =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002dfbc);
    uint32_t mask = UINT32_C(0xfffffffe);
    uint32_t rotation = (uint32_t)token - 1u;
    __asm__ volatile("rotl %0, %1" : "+r"(mask) : "r"(rotation) : "cc");
    *flags = *flags & mask;
    return 0u;
}
