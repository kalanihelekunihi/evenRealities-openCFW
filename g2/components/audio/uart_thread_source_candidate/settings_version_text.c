#include <stdint.h>

/* Official Apollo payload ROM 0x78b7bc; the caller copies all 11 bytes. */
const uint8_t audio_settings_right_version_text[11] = {
    '2', '.', '2', '.', '6', '.', '1', '0', 0, 0, 0
};

/* Official Apollo payload ROM 0x78c074; the caller copies all 9 bytes. */
const uint8_t audio_settings_version_text[9] = {
    '2', '.', '2', '.', '6', '.', '1', '0', 0
};
