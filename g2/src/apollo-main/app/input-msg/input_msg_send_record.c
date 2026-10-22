/* Apollo input_msg_send_record, native 0x51301c. */
#include <stdint.h>
uint8_t audio_input_message_state[16]
    __attribute__((section(".g2_ram_2000408c")));
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t);
extern uint32_t audio_thread_flags_set(void *,uint32_t);
extern int32_t audio_ble_hci_boot_log_4733ee(const char *,...);

static const char queue_error[]="INP_SendMessage osMessageQueuePut error:0x%x\n";

static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

/* Stock 0x0051301C (input_msg_send_record) */
void audio_input_message_send_record(const void *record) {
    if(record==0) return;
    uint32_t queue=load_u32(audio_input_message_state+12u);
    if(queue==0u) return;
    int32_t status=audio_cmsis_queue_put((void *)(uintptr_t)queue,record,0u,0u);
    if(status==0) {
        uint32_t thread=load_u32(audio_input_message_state+8u);
        (void)audio_thread_flags_set((void *)(uintptr_t)thread,0x400000u);
    } else {
        (void)audio_ble_hci_boot_log_4733ee(queue_error,status);
    }
}
