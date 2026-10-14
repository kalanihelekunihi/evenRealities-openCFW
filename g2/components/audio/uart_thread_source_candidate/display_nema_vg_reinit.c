/* Apollo MAIN s200 v2.2.6.10 native 0x5224b6 outer VG reinit body.
 * The five eight-byte records are copied from authenticated ROM
 * 0x5225d4..0x5225fb. */
#include <stdint.h>

extern void audio_uart_nema_instruction_upload_522920(const uint32_t *, uint32_t, uint32_t);
extern void audio_uart_nema_child_514846(uint32_t, uint32_t);
extern void *audio_uart_nema_vg_framebuffer_get_51562e(void);

volatile uint32_t audio_uart_nema_vg_framebuffer_context_cell_20074f08;

static const uint32_t vg_records[5][2] = {
    {0x080c0182u, 0x8a9f5a24u},
    {0x080c0182u, 0x8a9f5a34u},
    {0x080c0182u, 0x8a8761c6u},
    {0x004e0002u, 0x800b0286u},
    {0x0a980002u, 0x8081a046u},
};

void audio_uart_nema_vg_reinit_5224b6(void) {
    audio_uart_nema_instruction_upload_522920(vg_records[0], 1u, 0x16u);
    audio_uart_nema_instruction_upload_522920(vg_records[1], 1u, 0x17u);
    audio_uart_nema_child_514846(0x388u, 1u);
    audio_uart_nema_instruction_upload_522920(vg_records[2], 1u, 0x15u);
    audio_uart_nema_instruction_upload_522920(vg_records[3], 1u, 0x14u);
    audio_uart_nema_instruction_upload_522920(vg_records[4], 1u, 0x13u);
    audio_uart_nema_vg_framebuffer_context_cell_20074f08 =
        (uint32_t)(uintptr_t)audio_uart_nema_vg_framebuffer_get_51562e();
}
