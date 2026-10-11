/* Five native 14-byte profile message entry wrappers. Each forwards a
 * nonnull message to its actual profile handler; no success value is made up. */
#include <stdint.h>
extern void audio_ble_ota_message_body(void *); /* 0x4bdc0c */
extern void audio_ble_eus_message_body(void *); /* 0x4bded6 */
extern void audio_ble_ess_message_body(void *); /* 0x4be24e */
extern void audio_ble_efs_message_body(void *); /* 0x4be420 */
extern void audio_ble_nus_message_body(void *); /* 0x4be76c */
void audio_ble_ota_message(uint8_t handler,void *message) {
    (void)handler;if(message)audio_ble_ota_message_body(message);
}
void audio_ble_eus_message(uint8_t handler,void *message) {
    (void)handler;if(message)audio_ble_eus_message_body(message);
}
void audio_ble_ess_message(uint8_t handler,void *message) {
    (void)handler;if(message)audio_ble_ess_message_body(message);
}
void audio_ble_efs_message(uint8_t handler,void *message) {
    (void)handler;if(message)audio_ble_efs_message_body(message);
}
void audio_ble_nus_message(uint8_t handler,void *message) {
    (void)handler;if(message)audio_ble_nus_message_body(message);
}
