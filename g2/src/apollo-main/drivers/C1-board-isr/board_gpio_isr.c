/* Board GPIO interrupt handlers named in the board pin table
 * (app/S3-app-data/pt_production_data.c). Both are 10-byte stubs
 * (push {r7, lr}; movs r0, #0; bl ...; pop {r0, pc}).
 *
 *   0x510fd8..0x510fe1  GPIO4  nPM1300 nIRQ  -> ring-link event 0 (0x4ac16c)
 *   0x55ba64..0x55ba6d  GPIO27 touch attention -> input_msg_send_touch (0x513056)
 *
 * Stock passes 0 in r0 to both callees. input_msg_send_touch ignores r0; it
 * is declared here with one argument so the call materialises the same
 * movs r0, #0. */
#include <stdint.h>

extern void audio_ble_master_emit_ring_event(uint8_t event); /* 0x4ac16c */
extern void input_msg_send_touch(uint32_t unused);           /* 0x513056, r0 ignored */

void board_gpio4_pmic_isr_510fd8(void);
void board_gpio27_touch_isr_55ba64(void);

/* Stock 0x510fd8: GPIO4 (nPM1300 interrupt line). */
void board_gpio4_pmic_isr_510fd8(void)
{
    audio_ble_master_emit_ring_event(0u);
}

/* Stock 0x55ba64: GPIO27 (CY8C4046 touch attention). */
void board_gpio27_touch_isr_55ba64(void)
{
    input_msg_send_touch(0u);
}
