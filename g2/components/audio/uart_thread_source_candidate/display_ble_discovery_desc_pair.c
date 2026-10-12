/* Native Cordio attcDiscProcDescPair 0x56b8fa and attcUuidCmp 0x56b7ec. */
#include <stdint.h>
extern int32_t g2_lfs_memcmp(const void *,const void *,uint32_t);
extern uint8_t audio_ble_att_uuid_base_2000044c[16]; /* native mutable template 0x4b5014 */
extern volatile uint8_t audio_ble_trace_level_cell;
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
uint8_t audio_ble_att_uuid_compare_16_to_128(const uint8_t *uuid16,const uint8_t *uuid128){
    audio_ble_att_uuid_base_2000044c[12]=uuid16[0];
    audio_ble_att_uuid_base_2000044c[13]=uuid16[1];
    return g2_lfs_memcmp(audio_ble_att_uuid_base_2000044c,uuid128,16u)==0;
}
uint8_t audio_ble_att_uuid_compare_56b7ec(const uint8_t *entry,const uint8_t *uuid,uint8_t wide){
    const uint8_t flags=entry[4];
    const uint8_t *expected=(const uint8_t *)(uintptr_t)rd32(entry);
    if((flags&1u)==wide)
        return g2_lfs_memcmp(expected,uuid,wide==0u?2u:16u)==0;
    if(wide==1u && (flags&1u)==0u)
        return audio_ble_att_uuid_compare_16_to_128(expected,uuid);
    return 0u;
}
static void descriptor_found(uint16_t handle){
    static const char info[]="INFO",error[]="ERR",warn[]="WARN",att[]="ATT",hci[]="HCI";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\attc_disc.c";
    static const char name[]="attcDiscProcDescPair",message[]="descriptor found handle:0x%x";
    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(info,error,3)!=0){
        if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(info,warn,4)!=0){
            if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(info,info,4)!=0){
                if(audio_ble_trace_level_cell==0){
                    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(att,hci,3)!=0)
                        audio_ble_wsf_trace(info,message,handle);
                }else if((audio_log_flags()&2u)!=0u)
                    audio_log_extended(4,att,source,name,0xeeu,message,handle);
            }else if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3,att,source,name,0xeeu,message,handle);
        }else if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2,att,source,name,0xeeu,message,handle);
    }else if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1,att,source,name,0xeeu,message,handle);
}
void audio_ble_discovery_proc_desc_pair_56b8fa(uint8_t *context,uint8_t wide,const uint8_t *item){
    const uint16_t handle=rd16(item);
    const uint8_t *uuid=item+2;
    const uint8_t *entries=(const uint8_t *)(uintptr_t)rd32(context);
    uint8_t *handles=(uint8_t *)(uintptr_t)rd32(context+4);
    for(uint8_t i=context[0x12];i<context[0x0c];i++){
        const uint8_t *entry=(const uint8_t *)(uintptr_t)rd32(entries+(uint32_t)i*4u);
        if((entry[4]&4u)==0u)break;
        if(rd16(handles+(uint32_t)i*2u)==0u && audio_ble_att_uuid_compare_56b7ec(entry,uuid,wide)!=0u){
            handles[(uint32_t)i*2u]=(uint8_t)handle;
            handles[(uint32_t)i*2u+1u]=(uint8_t)(handle>>8);
            descriptor_found(handle);
            break;
        }
    }
}
