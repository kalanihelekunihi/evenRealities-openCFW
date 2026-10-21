/* Native ANCC parser children 0x4bedac, 0x4bf06c, 0x4beb82. */
#include <stdint.h>
extern uint8_t audio_ble_ancc_state[]; /* 0x200695c8 */
extern uint8_t audio_ble_ancc_cache[]; /* 0x2006ddd4 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern uint32_t g2_log_module_length(const char *);
extern int32_t audio_ble_send_status_message(uint32_t,const uint8_t *,uint32_t,uint32_t);
extern void audio_ble_ancc_rx_sync_callback_4bed0e(uint32_t);
extern void audio_ble_ancc_get_app_attribute_4bebc4(uint32_t,const char *);
extern void audio_ble_attc_write_request(uint8_t,uint16_t,uint16_t,const uint8_t *); /* native 0x4b579c */
static const char module[]="ble.ancc";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\ancc\\profile_ancc.c";
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
    ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}

void audio_ble_ancc_send_complete_4bedac(const uint8_t *payload,uint32_t length){
    static const char msg[]="Send Complete Notification Msg";
    static const char compact[]="[ble.ancc]Send Complete Notification Msg";
    if(audio_log_level()&2u)
        audio_log_extended(4u,module,path,"_anccSendCompleteNotificationMsg",0x17eu,msg);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10000000u,compact);
    (void)audio_ble_send_status_message(0x101u,payload,length&0xffffu,
        (uint32_t)(uintptr_t)audio_ble_ancc_rx_sync_callback_4bed0e);
}

void audio_ble_ancc_perform_action_4beb82(uint32_t handle_list,uint32_t uid,uint32_t action){
    const uint8_t *handles=(const uint8_t *)(uintptr_t)handle_list;
    uint16_t control=rd16(handles+4u);
    if(control==0u)return;
    const uint8_t packet[6]={2u,(uint8_t)uid,(uint8_t)(uid>>8),
        (uint8_t)(uid>>16),(uint8_t)(uid>>24),(uint8_t)action};
    audio_ble_attc_write_request(audio_ble_ancc_state[0],control,6u,packet);
}

void audio_ble_ancc_attr_callback_4bf06c(uint8_t *active){
    uint8_t *s=audio_ble_ancc_state;
    uint8_t *cache=audio_ble_ancc_cache;
    uint8_t attr_id=active[10u];
    uint16_t length=rd16(active+0x35au);
    const uint8_t *value=active+0x35cu;
    if(attr_id==0u){
        audio_queue_copy_bytes(s+0x31cu,value,length);
        s[0x31cu+length]=0u;
        uint32_t n=g2_log_module_length((const char *)(s+0x31cu));
        audio_queue_copy_bytes(cache+8u,s+0x31cu,n+1u);
        uint32_t index=rd16(active);
        cache[4u]=s[0x1eu+index*12u];
        cache[5u]=s[0x1cu+index*12u];
        if((cache[5u]==0u||cache[5u]==1u)&&s[0x31cu]!=0u){
            static const char msg[]="Requesting app attribute for app_id: %s";
            static const char compact[]="[ble.ancc]Requesting app attribute for app_id: %s";
            if(audio_log_level()&2u)
                audio_log_extended(4u,module,path,"_ancsAnccAttrCback",0x1efu,msg,s+0x31cu);
            if((audio_log_level()&1u)||(audio_log_level()&4u))
                (void)compressed_log_output(0x10400000u,compact,compact,s+0x31cu);
            audio_ble_ancc_get_app_attribute_4bebc4(rd32(s+4u),(const char *)(s+0x31cu));
        }
        cache[6u]=s[0x1du+index*12u];
        cache[7u]=s[0x1fu+index*12u];
    }else if(attr_id==1u||attr_id==2u||attr_id==3u||attr_id==5u){
        if(rd16(active+8u)!=0u){
            uint32_t dest=(attr_id==1u?0x68u:attr_id==2u?0xa8u:attr_id==3u?0xe8u:0x2e8u);
            audio_queue_copy_bytes(cache+dest,s+0x35cu+rd16(active+6u),rd16(active+8u));
        }
    }else if(attr_id==6u){
        if(rd16(active+8u)!=0u)cache[0x2f8u]=0u;
    }else if(attr_id==7u){
        if(rd16(active+8u)!=0u)cache[0x2f8u]=1u;
    }
}
