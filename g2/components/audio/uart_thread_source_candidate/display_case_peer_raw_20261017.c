/* Provisional C storage for Case sync peer bytes at stock RAM 0x20074188..8b.
 * Their final startup and contiguous layout with the status cells remain open.
 */
#include <stdint.h>
volatile uint8_t audio_uart_case_peer_raw_20074188[4]
    __attribute__((section(".g2_ram_20074188"),used));
