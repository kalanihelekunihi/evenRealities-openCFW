/* Native 0x49b954 reads one four-byte command cell at 0x20074860.
 * The surrounding allocation and startup value remain unproved. */
#include <stdint.h>
uint32_t audio_settings_response_command_id_20074860
    __attribute__((section(".g2.ram.settings_response_command_id"),used,aligned(4)));
