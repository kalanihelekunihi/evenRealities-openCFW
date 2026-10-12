/* Native Cordio attcDiscProcCharDecl 0x56bb1c. */
#include <stdint.h>
extern uint8_t audio_ble_att_uuid_compare_56b7ec(const uint8_t *,const uint8_t *,uint8_t);
extern volatile uint8_t audio_ble_trace_level_cell;
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static void wr16(uint8_t *p,uint16_t x){p[0]=(uint8_t)x;p[1]=(uint8_t)(x>>8);}
static void trace_handle(uint8_t found,uint16_t handle){
    static const char info[]="INFO",warn[]="WARN",error[]="ERR",att[]="ATT",hci[]="HCI";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\attc_disc.c";
    static const char name[]="attcDiscProcCharDecl";
    static const char found_message[]="characteristic found handle:0x%x";
    static const char invalid_message[]="invalid handle:0x%x";
    const char *tag=found?info:warn;
    const char *message=found?found_message:invalid_message;
    const uint32_t line=found?0x185u:0x18eu;
    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(tag,error,3)!=0){
        if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(tag,warn,4)!=0){
            if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(tag,info,4)!=0){
                if(audio_ble_trace_level_cell==0){
                    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(att,hci,3)!=0)
                        audio_ble_wsf_trace(tag,message,handle);
                }else if((audio_log_flags()&2u)!=0u)
                    audio_log_extended(4,att,source,name,line,message,handle);
            }else if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3,att,source,name,line,message,handle);
        }else if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2,att,source,name,line,message,handle);
    }else if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1,att,source,name,line,message,handle);
}
void audio_ble_discovery_proc_char_decl_56bb1c(uint8_t *context,uint8_t wide,const uint8_t *item){
    const uint16_t declaration=rd16(item);
    const uint16_t value=rd16(item+3);
    const uint8_t *uuid=item+5;
    uint8_t *handles=(uint8_t *)(uintptr_t)rd32(context+4);
    if(context[0x13]!=0xffu){
        wr16(handles+(uint32_t)context[0x13]*2u,(uint16_t)(declaration-1u));
        context[0x13]=0xffu;
    }
    if(declaration<value && value<=rd16(context+0x10)){
        const uint8_t *entries=(const uint8_t *)(uintptr_t)rd32(context);
        for(uint8_t i=0;i<context[0x0c];i++){
            const uint8_t *entry=(const uint8_t *)(uintptr_t)rd32(entries+(uint32_t)i*4u);
            if(rd16(handles+(uint32_t)i*2u)==0u && audio_ble_att_uuid_compare_56b7ec(entry,uuid,wide)!=0u){
                wr16(handles+(uint32_t)i*2u,value);
                if(i<(uint8_t)(context[0x0c]-1u)){
                    const uint8_t *next=(const uint8_t *)(uintptr_t)rd32(entries+(uint32_t)(i+1u)*4u);
                    if((next[4]&4u)!=0u)context[0x13]=(uint8_t)(i+1u);
                }
                trace_handle(1u,value);
                break;
            }
        }
    }else trace_handle(0u,value);
}
