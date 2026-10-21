/* Native 0x52f86a: copy the 16-byte EM9305 image header and report success.
 * The input and destination are caller-owned; this routine does not validate
 * either pointer.  The firmware image itself is a runtime file contract. */
#include <stdint.h>

uint32_t audio_ble_radio_header_copy_52f86a(void *image_header,
                                            void *parsed_header) {
    __builtin_memcpy(parsed_header, image_header, 16u);
    return 1u;
}
