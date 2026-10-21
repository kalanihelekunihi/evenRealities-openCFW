/* Native Cordio AttcDiscServiceCmpl 0x56bf32. */
#include <stdint.h>
extern volatile uint8_t audio_ble_trace_level_cell;
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static void wr16(uint8_t *p,uint16_t x){p[0]=(uint8_t)x;p[1]=(uint8_t)(x>>8);}
static void service_trace(uint8_t found,uint8_t event,uint16_t start,uint16_t end){
    static const char info[]="INFO",warn[]="WARN",error[]="ERR",att[]="ATT",hci[]="HCI";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\attc_disc.c";
    static const char name[]="AttcDiscServiceCmpl";
    static const char found_message[]="found service startHdl=0x%x endHdl=0x%x";
    static const char unexpected_message[]="unexpected callback event %d";
    const char *tag=found?info:warn,*message=found?found_message:unexpected_message;
    const uint32_t line=found?0x275u:0x262u;
    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(tag,error,3)!=0){
        if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(tag,warn,4)!=0){
            if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(tag,info,4)!=0){
                if(audio_ble_trace_level_cell==0){
                    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(att,hci,3)!=0){
                        if(found)audio_ble_wsf_trace(tag,message,start,end);
                        else audio_ble_wsf_trace(tag,message,event);
                    }
                }else if((audio_log_flags()&2u)!=0u){
                    if(found)audio_log_extended(4,att,source,name,line,message,start,end);
                    else audio_log_extended(4,att,source,name,line,message,event);
                }
            }else if((audio_log_flags()&2u)!=0u){
                if(found)audio_log_extended(3,att,source,name,line,message,start,end);
                else audio_log_extended(3,att,source,name,line,message,event);
            }
        }else if((audio_log_flags()&2u)!=0u){
            if(found)audio_log_extended(2,att,source,name,line,message,start,end);
            else audio_log_extended(2,att,source,name,line,message,event);
        }
    }else if((audio_log_flags()&2u)!=0u){
        if(found)audio_log_extended(1,att,source,name,line,message,start,end);
        else audio_log_extended(1,att,source,name,line,message,event);
    }
}
uint8_t audio_ble_discovery_service_complete_56bf32(uint8_t *context,const uint8_t *message){
    if(message[2]!=3u){service_trace(0u,message[2],0,0);return 0x75u;}
    if(message[3]!=0u)return message[3];
    if(rd16(message+8)==0u)return 10u;
    const uint8_t *data=(const uint8_t *)(uintptr_t)rd32(message+4);
    const uint16_t start=rd16(data),end=rd16(data+2);
    wr16(context+0x0e,start);wr16(context+0x10,end);
    service_trace(1u,0,start,end);
    return 0u;
}
