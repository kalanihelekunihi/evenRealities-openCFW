/* Native INPM_EventSend 0x4c5916, called by ring touch update 0x47269e.
 * The stock function writes only bytes 0..1 and 4..9 of its 12-byte local
 * packet before dispatch. Bytes 2..3 and 10..11 remain ambient stack data;
 * the source preserves that partial initialization, so their values are not
 * represented as a portable product constant. */
#include <stdint.h>
extern int32_t audio_uart_input_event_send_464d1c(uint16_t,const void *,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="input.manager";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\input\\service_input_manager.c";
static const char function[]="INPM_EventSend";
static const char message[]="InputDevType = %d, eventID = %d, diffx = %d, speed = %d";
static const char compact[]="[input.manager]InputDevType = %d, eventID = %d, diffx = %d, speed = %d";
void audio_uart_ring_touch_event_4c5916(uint16_t type,uint32_t event_id,uint8_t dx,uint8_t speed) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0x61u,message,type,event_id,dx,speed);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x11000000u,compact,compact,type,event_id,dx,speed);
    uint8_t event[12];
    event[0]=(uint8_t)type;event[1]=(uint8_t)(type>>8);
    event[4]=(uint8_t)event_id;event[5]=(uint8_t)(event_id>>8);
    event[6]=(uint8_t)(event_id>>16);event[7]=(uint8_t)(event_id>>24);
    event[8]=dx;event[9]=speed;
    (void)audio_uart_input_event_send_464d1c(0x108u,event,12u,0u);
}
