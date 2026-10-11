/* Native HUB_Open/HUB_Close 0x4a6d58/0x4a6dca. */
#include <stdint.h>
extern volatile uint16_t audio_uart_hub_role_cell; /* RAM 0x20004526 */
extern uint32_t audio_log_flags(void); /* selected 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...); /* selected 0x43d574 */
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...); /* selected 0x43ce9e */
extern const void *audio_hub_send_message(const void *); /* native 0x4a6a1a */
static const char module[]="sensor_hub";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\sensor_hub\\sensor_hub.c";
static const char open_function[]="HUB_Open",close_function[]="HUB_Close";
static const char open_error[]="IMU open role type is left, cannot open";
static const char close_error[]="IMU open role type is left, cannot close";
static const char open_short[]="[sensor_hub]IMU open role type is left, cannot open";
static const char close_short[]="[sensor_hub]IMU open role type is left, cannot close";
static uint32_t send(uint32_t channel,uint16_t operation) {
    uint8_t message[8]={0};
    *(uint16_t *)(void *)message=operation;
    message[4]=(uint8_t)channel;
    (void)audio_hub_send_message(message);
    return 0;
}
static uint32_t denied(const char *function,const char *error,
                       const char *short_text,uint32_t line) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,function,line,error);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04000000u,short_text,short_text);
    return UINT32_MAX;
}
uint32_t audio_hub_channel_open(uint32_t channel) {
    if(audio_uart_hub_role_cell==2u)
        return denied(open_function,open_error,open_short,391u);
    return send(channel,5u);
}
uint32_t audio_hub_channel_close(uint32_t channel) {
    if(audio_uart_hub_role_cell==2u)
        return denied(close_function,close_error,close_short,404u);
    return send(channel,6u);
}
