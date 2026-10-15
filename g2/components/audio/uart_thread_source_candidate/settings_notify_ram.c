/* Source-owned Apollo settings notification cells, authenticated by
 * setting_notify_common literal pool at 0x49bdf0/0x49bffc/0x49c030. */
#include <stdint.h>

uint8_t audio_settings_notify_encode_buffer[256]
    __attribute__((section(".g2.ram.settings_notify_encode_buffer"),used,aligned(4))); /* 0x200706ec */
uint8_t audio_settings_notify_staging[104]
    __attribute__((section(".g2.ram.settings_notify_staging"),used,aligned(4))); /* 0x200725a0 */
uint32_t audio_settings_notify_magic
    __attribute__((section(".g2.ram.settings_notify_magic"),used,aligned(4))); /* 0x2007486c */
