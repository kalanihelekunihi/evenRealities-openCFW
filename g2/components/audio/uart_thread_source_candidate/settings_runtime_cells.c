#include <stdint.h>

/* Native Apollo RAM literal cells. Initialization/ownership of OS handles
 * remains with the original producer paths until those paths are recovered. */
uint32_t audio_settings_left_version_last_request_tick
    __attribute__((section(".g2.ram.settings_left_version_last_request_tick"),used,aligned(4))); /* 0x20074994 */
void *audio_settings_ancc_mutex
    __attribute__((section(".g2.ram.settings_ancc_mutex"),used,aligned(4))); /* 0x2007491c */
uint8_t audio_settings_ancc_count
    __attribute__((section(".g2.ram.settings_ancc_count"),used)); /* 0x2007500d */
void *audio_settings_peer_send_queue
    __attribute__((section(".g2.ram.settings_peer_send_queue"),used,aligned(4))); /* 0x200749cc */
void *audio_settings_peer_event
    __attribute__((section(".g2.ram.settings_peer_event"),used,aligned(4))); /* 0x20074b10 */
