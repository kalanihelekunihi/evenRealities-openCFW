/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10026358 TWS tick body. XIP application callees are real
 * external contracts; runtime queue address is a native literal.
 */
#include <stdint.h>

extern int32_t gx8002_xip_tws_dequeue_10206fb0(
    volatile void *queue, uint32_t *out_kind);
extern uint32_t gx8002_xip_tws_event_102088f8(void *record);
extern uint32_t gx8002_xip_tws_ack_102073a0(uint32_t bytes);
extern uint32_t gx8002_xip_tws_dispatch_10208cc0(const uint32_t *event);
extern int32_t gx8002_xip_tws_ready_102077f8(void);
extern int32_t gx8002_xip_tws_command_10207808(uint32_t command);

void gx8002_resident_tws_tick_26358(void)
{
    volatile uint8_t *const queue =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e6ec);
    uint32_t kind_and_record[2] = {0u, 0u};
    if (gx8002_xip_tws_dequeue_10206fb0(queue, kind_and_record) != 0) {
        uint32_t record = kind_and_record[1];
        if (kind_and_record[0] == 0x100u) {
            (void)gx8002_xip_tws_event_102088f8((void *)(uintptr_t)record);
            (void)gx8002_xip_tws_ack_102073a0(1u);
        }
        volatile uint8_t *const item =
            (volatile uint8_t *)(uintptr_t)record;
        if (item[0xdu] != 0u) {
            uint32_t event[2];
            event[0] = item[0xdu];
            event[1] = *(volatile uint32_t *)(void *)(item + 8u);
            (void)gx8002_xip_tws_dispatch_10208cc0(event);
        }
    }
    if (*(volatile uint32_t *)(void *)(queue + 0x4cu) == 4u &&
        gx8002_xip_tws_ready_102077f8() == 0)
        gx8002_xip_tws_command_10207808(13u);
}
