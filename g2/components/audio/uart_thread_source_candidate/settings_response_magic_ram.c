/* Native response encoder at 0x49b40e reads this four-byte cell at 0x20074864.
 * Its initialization and surrounding allocation remain whole-image gates. */
#include <stdint.h>
uint32_t audio_settings_response_magic_20074864
    __attribute__((section(".g2.ram.settings_response_magic"),used,aligned(4)));
