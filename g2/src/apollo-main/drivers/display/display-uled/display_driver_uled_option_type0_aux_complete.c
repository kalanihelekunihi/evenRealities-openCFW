/* Apollo S200 type-0 auxiliary complete command sequence at 0x593660. */
#include <stdint.h>

extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t display_driver_uled_type0_aux_reg_write_5926ee(uint32_t,
                                                                 const void *,uint32_t);
extern void audio_ble_hci_boot_delay_491102(uint32_t);
extern uint32_t audio_delay(uint32_t);

void display_driver_uled_type0_aux_complete_593660(void) {
    uint8_t scratch[20];
    audio_uart_buffer_zero(scratch,20u,0u);
    (void)display_driver_uled_type0_aux_reg_write_5926ee(0x71u,scratch,0u);
    audio_ble_hci_boot_delay_491102(2u);
    (void)display_driver_uled_type0_aux_reg_write_5926ee(0x73u,scratch,0u);
    audio_ble_hci_boot_delay_491102(2u);
    (void)display_driver_uled_type0_aux_reg_write_5926ee(0x97u,scratch,0u);
    (void)audio_delay(2u);
}
