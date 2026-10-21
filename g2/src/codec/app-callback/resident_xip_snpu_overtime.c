/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10205ad8 dump and 0x10205b1c overtime reset.
 * Output literals are from the authenticated stock Codec image; the
 * 0x20000000 command alias and 0x20027350 state base are retained.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
extern void gx8002_xip_npu_get_base_address_102058b4(
    uint32_t, uint32_t, uint32_t *);
extern void gx8002_xip_npu_get_current_command_102058c4(uint32_t, uint32_t *);
extern void gx8002_xip_npu_get_over_command_10205860(uint32_t, uint32_t *);
extern void gx8002_xip_npu_get_task_head_102058a4(uint32_t, uint32_t *);
extern void gx8002_xip_npu_disable_10205600(uint32_t);
extern void gx8002_xip_npu_reset_10205880(uint32_t);
extern void gx8002_xip_npu_registers_initialize_10205950(void);
extern void gx8002_xip_npu_set_task_head_10205898(uint32_t, uint32_t);
extern void gx8002_xip_npu_enable_102055f4(uint32_t);

void gx8002_xip_snpu_dump_words_10205ad8(const uint32_t *words)
{
    for (uint32_t i = 0u; i < 32u; ++i) {
        (void)gx8002_xip_tws_publish_10206c24("0x%08x ", words[i]);
        if ((i + 1u) % 10u == 0u)
            (void)gx8002_xip_tws_publish_10206c24("\n");
    }
    (void)gx8002_xip_tws_publish_10206c24("\n");
}

void gx8002_xip_snpu_overtime_reset_10205b1c(void)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027350);
    uint32_t npu = state[0x171u];
    uint32_t base_command = 0u, current = 0u, over = 0u, head = 0u;
    gx8002_xip_npu_get_base_address_102058b4(
        state[0x173u], 2u, &base_command);
    gx8002_xip_npu_get_current_command_102058c4(npu, &current);
    gx8002_xip_npu_get_over_command_10205860(npu, &over);
    (void)gx8002_xip_tws_publish_10206c24(
        "[SNPU] overtime addr: 0x%x, base cmd addr: 0x%x, prev int addr: 0x%x\n",
        current, base_command, over);
    (void)gx8002_xip_tws_publish_10206c24(
        "[SNPU] overtime addr - 0x80:\n");
    gx8002_xip_snpu_dump_words_10205ad8(
        (const uint32_t *)(uintptr_t)(current - 0x80u));
    (void)gx8002_xip_tws_publish_10206c24("[SNPU] overtime cmd :\n");
    gx8002_xip_snpu_dump_words_10205ad8(
        (const uint32_t *)(uintptr_t)(current + UINT32_C(0x20000000)));
    (void)gx8002_xip_tws_publish_10206c24("cmd_type: 0x%x\n",
        *(volatile uint8_t *)(uintptr_t)(current + UINT32_C(0x20000000)));
    if (over == 0u)
        gx8002_xip_npu_get_task_head_102058a4(npu, &head);
    else
        head = *(volatile uint32_t *)(uintptr_t)(over + UINT32_C(0x20000004));
    gx8002_xip_npu_disable_10205600(npu);
    gx8002_xip_npu_reset_10205880(state[0x172u]);
    gx8002_xip_npu_registers_initialize_10205950();
    gx8002_xip_npu_set_task_head_10205898(npu, head);
    gx8002_xip_npu_enable_102055f4(npu);
}
