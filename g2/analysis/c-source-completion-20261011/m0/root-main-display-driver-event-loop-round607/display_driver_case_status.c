/* Apollo case-status check 0x4acad0, inlined 0x4acac0/0x4acab4 getters. */
#include <stdint.h>
uint8_t display_driver_case_state_cells[8]; /* native base 0x20074188, extent gated */
uint8_t display_driver_case_override_cell; /* native 0x20075012 */
uint32_t audio_uart_case_status(void) {
    if(display_driver_case_override_cell!=0u) return 0u;
    if(display_driver_case_state_cells[7]==1u) return 1u;
    return display_driver_case_state_cells[6]==1u ? 1u : 0u;
}
