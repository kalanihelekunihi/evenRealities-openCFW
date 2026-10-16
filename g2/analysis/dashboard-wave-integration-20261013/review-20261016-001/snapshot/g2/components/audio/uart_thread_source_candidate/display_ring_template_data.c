#include <stdint.h>

const char audio_uart_display_create_error[] = "lv_disp_drv_setup";
const uint8_t audio_uart_ring_status_template[8] = {6u, 0u, 1u, 0u, 0u, 0u, 0u, 0u};
const uint8_t audio_uart_ring_query_template[8] = {5u, 0u, 1u, 0u, 0u, 0u, 0u, 0u};
