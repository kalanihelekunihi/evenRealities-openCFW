/* Provisional product RAM for APP_PbNotifyEncodeGlassesCaseInfo.
 * Source-observed minimum extents: ten-byte frame, 256-byte encoded output,
 * and one-byte sequence. Stock startup contents and linker placement remain
 * separate contracts. */
#include <stdint.h>

uint8_t audio_uart_case_tx_frame_200f5a9c[10]
    __attribute__((section(".g2_ram_200f5a9c"),used));
uint8_t audio_uart_case_tx_encoded_2037c5a0[256]
    __attribute__((section(".g2_ram_2037c5a0"),used));
uint8_t audio_uart_case_tx_magic_20074ffa
    __attribute__((section(".g2_ram_20074ffa"),used));
