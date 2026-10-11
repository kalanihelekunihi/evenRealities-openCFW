/* Native HUB_SendMessage 0x4a6a1a with actual queue and log effects. */
#include <stdint.h>
extern void *audio_hub_send_queue; /* live RAM cell 0x20003670 */
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t); /* selected 0x449abe */
extern uint32_t audio_log_flags(void); /* selected 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...); /* selected 0x43d574 */
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...); /* selected 0x43ce9e */
static const char module[]="sensor_hub";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\sensor_hub\\sensor_hub.c";
static const char function[]="HUB_SendMessage";
static const char failed[]="[HUB_MessageProcesser]osMessageQueuePut error:%d";
static const char short_failed[]="[sensor_hub][HUB_MessageProcesser]osMessageQueuePut error:%d";
const void *audio_hub_send_message(const void *message) {
    if(message!=0 && audio_hub_send_queue!=0) {
        int32_t result=audio_cmsis_queue_put(audio_hub_send_queue,message,0u,0u);
        if(result!=0) {
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(1u,module,path,function,242u,failed,result);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x04400000u,short_failed,short_failed,result);
        }
    }
    return message;
}
