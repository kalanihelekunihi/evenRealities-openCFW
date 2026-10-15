#include <stdint.h>

/* Native RAM 0x2007502f. BLE and L2C source names are the same byte. */
volatile uint8_t audio_l2c_log_enabled_cell;
extern volatile uint8_t audio_ble_trace_level_cell
    __attribute__((alias("audio_l2c_log_enabled_cell")));
