/* Eight native radio stack rows at 0x2003b558..0x2003fa97.
 * Final linker placement and startup zeroing remain image-level gates. */
#include <stdint.h>

__attribute__((used, aligned(4), section(".g2_bss_2003b558")))
uint8_t audio_ble_vendor_stack_rows_2003b558[8u * 0x8a8u];

_Static_assert(sizeof(audio_ble_vendor_stack_rows_2003b558) == 0x4540u,
               "native radio stack row extent");
