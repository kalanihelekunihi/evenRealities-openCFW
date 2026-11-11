/* SPDX-License-Identifier: MIT
 * Stock 0x317534 lctrBisFlushStaleSdus (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified
 * against it in the QEMU-ARC harness (.waves/w28). Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_wsf_event_peek(uint32_t queue, uint32_t out_u8);
extern void opencfw_em9305_wsf_event_remove(uint32_t queue, uint32_t out_u8);
extern void opencfw_em9305_wsf_event_release(uint32_t ev);
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t, uint32_t);
extern void opencfw_em9305_radio_packet_complete_31ae74(uint32_t);
extern void opencfw_em9305_wsf_critical_enter(void);
extern void opencfw_em9305_wsf_critical_exit(void);

void opencfw_em9305_lctrBisFlushStaleSdus(uint32_t ctx)
{
  uint8_t tmp;
  uint32_t q = ctx + 8u, ev, elapsed;
  for (;;) {
    ev = opencfw_em9305_wsf_event_peek(q, (uint32_t)(uintptr_t)&tmp);
    if (ev == 0u || B8(ev + 0xeu) == 0u) return;
    elapsed = opencfw_em9305_auxiliary_elapsed_303f8c(W32(W32(ctx + 4u) + 0x130u), W32(ev + 0x10u));
    if (W32(W32(ctx + 4u) + 0x2cu) >= elapsed) return;
    opencfw_em9305_wsf_event_remove(q, (uint32_t)(uintptr_t)&tmp);
    opencfw_em9305_wsf_event_release(W32(ev));
    opencfw_em9305_radio_packet_complete_31ae74(ev);
    opencfw_em9305_wsf_critical_enter();
    B8(0x805adcu) = (uint8_t)(B8(0x805adcu) + 1u);
    opencfw_em9305_wsf_critical_exit();
  }
}
