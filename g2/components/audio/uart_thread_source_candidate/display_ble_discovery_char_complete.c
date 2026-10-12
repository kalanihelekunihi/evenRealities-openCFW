/* Native Cordio AttcDiscCharCmpl 0x56c1f8: status and buffer effects. */
#include <stdint.h>
extern uint8_t audio_ble_discovery_proc_char_56be30(uint8_t *,const uint8_t *);
extern uint8_t audio_ble_discovery_proc_desc_56ba82(uint8_t *,const uint8_t *);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern volatile uint8_t audio_ble_trace_level_cell;
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
static uint32_t word32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void unexpected_event(uint8_t event){
    static const char warn[]="WARN",error[]="ERR",info[]="INFO",att[]="ATT",hci[]="HCI";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\attc_disc.c";
    static const char name[]="AttcDiscCharCmpl",message[]="unexpected callback event %d";
    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(warn,error,3)!=0){
        if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(warn,warn,4)!=0){
            if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(warn,info,4)!=0){
                if(audio_ble_trace_level_cell==0){
                    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(att,hci,3)!=0)
                        audio_ble_wsf_trace(warn,message,event);
                }else if((audio_log_flags()&2u)!=0u)
                    audio_log_extended(4,att,source,name,0x2a6u,message,event);
            }else if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3,att,source,name,0x2a6u,message,event);
        }else if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2,att,source,name,0x2a6u,message,event);
    }else if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1,att,source,name,0x2a6u,message,event);
}
uint8_t audio_ble_discovery_char_complete_56c1f8(uint8_t *context,const uint8_t *message){
    uint8_t status;
    if(message[2]==4u)status=audio_ble_discovery_proc_char_56be30(context,message);
    else if(message[2]==2u)status=audio_ble_discovery_proc_desc_56ba82(context,message);
    else {unexpected_event(message[2]);return 0x75u;}
    if(status!=0u && status!=0x79u)
        audio_uart_buffer_zero((void *)(uintptr_t)word32(context+4),
                               (uint32_t)context[0x0c]<<1u,0u);
    return status;
}
