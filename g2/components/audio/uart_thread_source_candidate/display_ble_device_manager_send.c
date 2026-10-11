/* Native DEV_SendMessage 0x4c659a, queue error counter and diagnostics. */
#include <stdint.h>
extern uint8_t audio_ble_device_manager_state[]; /* RAM 0x2000060c, queue at +12 */
extern volatile uint8_t audio_ble_device_manager_queue_errors; /* RAM 0x20074fb2 */
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t); /* 0x449abe */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="device_mgr";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\device_mgr\\device_mgr.c";
static const char function[]="DEV_SendMessage";
void audio_ble_device_manager_send(const uint8_t *message) {
    if(message==0) return;
    void *queue=*(void **)(void *)(audio_ble_device_manager_state+12u);
    if(queue==0) return;
    int32_t status=audio_cmsis_queue_put(queue,message,0u,0u);
    if(status==0) return;
    audio_ble_device_manager_queue_errors=(uint8_t)(audio_ble_device_manager_queue_errors+1u);
    if(audio_ble_device_manager_queue_errors==0u) return;
    if(audio_log_level()&2u)
        audio_log_extended(2u,module,source,function,0x10cu,
            "[DEV_SendMessage]osMessageQueuePut error:0x%x",status);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x08400000u,
            "[device_mgr][DEV_SendMessage]osMessageQueuePut error:0x%x",
            "[device_mgr][DEV_SendMessage]osMessageQueuePut error:0x%x",status);
    audio_ble_device_manager_queue_errors=0u;
}
