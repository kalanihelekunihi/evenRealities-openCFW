/* Six observed calibration object-pointer cells at native RAM 0x200749a8..bc
 * and the one-byte recalibration status at 0x2007501c.
 * The final startup initializer and physical placement remain unverified. */
#include <stdint.h>

uint32_t audio_uart_calibration_snapshot_200749a8
    __attribute__((section(".g2.ram.calibration.snapshot"), used, aligned(4)));
uint32_t audio_uart_calibration_success_primary_200749ac
    __attribute__((section(".g2.ram.calibration.success_primary"), used, aligned(4)));
uint32_t audio_uart_calibration_success_secondary_200749b0
    __attribute__((section(".g2.ram.calibration.success_secondary"), used, aligned(4)));
uint32_t audio_uart_calibration_panel_left_200749b4
    __attribute__((section(".g2.ram.calibration.panel_left"), used, aligned(4)));
uint32_t audio_uart_calibration_panel_right_200749b8
    __attribute__((section(".g2.ram.calibration.panel_right"), used, aligned(4)));
uint32_t audio_uart_calibration_panel_mark_200749bc
    __attribute__((section(".g2.ram.calibration.panel_mark"), used, aligned(4)));
uint8_t audio_uart_calibration_status_2007501c
    __attribute__((section(".g2.ram.calibration.status"), used));
