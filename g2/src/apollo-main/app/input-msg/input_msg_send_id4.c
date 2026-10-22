/* Apollo input_msg_send_id4, native 0x5130c0. */
#include <stdint.h>
extern void audio_input_message_send_record(const void *);

/* Stock 0x005130C0 (input_msg_send_id4) */
void audio_input_message_send_id4(uint32_t value) {
    const uint32_t record[3]={4u,0u,value};
    audio_input_message_send_record(record);
}
