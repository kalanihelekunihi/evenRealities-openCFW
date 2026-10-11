/* Native 0x4a696c: change the command halfword in the eight-byte template. */
#include <stdint.h>
extern uint8_t audio_hub_timeout_message_template[8]; /* ROM 0x78e47c; product data contract */
extern const void *audio_hub_send_message(const void *); /* selected 0x4a6a1a */
void audio_hub_timer_callback(void *argument) {
    uint32_t words[2];
    const uint8_t *source=audio_hub_timeout_message_template;
    uint8_t *target=(uint8_t *)words;
    (void)argument;
    for(unsigned i=0;i<8u;i++) target[i]=source[i];
    target[0]=8u;
    target[1]=0u;
    (void)audio_hub_send_message(target);
}
