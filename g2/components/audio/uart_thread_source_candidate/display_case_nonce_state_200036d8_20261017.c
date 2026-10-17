/* Stock initialized low-RAM bytes 0x200036d8..db: ff ff 02 02.
 * Extracted by decode_main_low_ram_20261016.py from the authenticated
 * 0x75d3f4 startup record; final section placement remains gated.
 */
#include <stdint.h>
uint8_t audio_uart_case_nonce_state_200036d8[4]
    __attribute__((section(".g2_ram_200036d8"),used))={0xffu,0xffu,0x02u,0x02u};
