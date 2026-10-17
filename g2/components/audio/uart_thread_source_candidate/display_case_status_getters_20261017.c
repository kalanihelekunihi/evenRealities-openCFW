/* Stock Main Case status byte getters 0x4acaa0, 0x4acaac, 0x4acab4.
 * Product RAM row base 0x20074188; observed bytes +4,+5,+6. */
#include <stdint.h>

volatile uint8_t audio_uart_case_soc_cell_2007418c
    __attribute__((section(".g2_ram_2007418c"),used));
volatile uint8_t audio_uart_case_charge_cell_2007418d
    __attribute__((section(".g2_ram_2007418d"),used));
extern volatile uint8_t audio_uart_case_sensor_b; /* existing +6 cell 0x2007418e */

uint8_t audio_uart_case_soc_4acaa0(void)
{
    return audio_uart_case_soc_cell_2007418c;
}
uint8_t audio_uart_case_charge_4acaac(void)
{
    return audio_uart_case_charge_cell_2007418d;
}
uint8_t audio_uart_case_lid_4acab4(void)
{
    return audio_uart_case_sensor_b;
}
