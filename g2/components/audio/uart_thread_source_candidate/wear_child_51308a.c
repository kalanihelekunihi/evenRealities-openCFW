/* Native four-word request wrapper 0x51308a..0x5130a6. */
#include <stdint.h>
extern void audio_input_message_send_record(const void *); /* stock 0x51301c */
void audio_wear_child_51308a(uint32_t value) {
    uint32_t request[4]={1u,0u,value,0u};
    audio_input_message_send_record(request);
}
