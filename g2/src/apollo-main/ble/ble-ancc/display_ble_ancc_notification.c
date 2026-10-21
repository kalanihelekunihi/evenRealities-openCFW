/* Native ANCC notification update 0x4bee5a, list push 0x4bec20,
 * and remove callback 0x4bee0a. Live ANCC state is externally placed. */
#include <stdint.h>
extern uint8_t audio_ble_ancc_state[]; /* RAM 0x200695c8 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
extern uint32_t audio_ble_ancc_no_connection_active_4bea24(void);
extern void audio_ble_ancc_get_next_delayed_4bea7a(uint32_t);
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t);
extern uint32_t audio_ble_ancc_attr_handler_4bf228(const uint8_t *,uint16_t);
static const char module[]="ble.ancc";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\ancc\\profile_ancc.c";
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
    ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void wr32(uint8_t *p,uint32_t v){for(uint32_t i=0;i<4u;++i)p[i]=(uint8_t)(v>>(i*8u));}

uint32_t audio_ble_ancc_action_push_4bec20(const uint8_t *item){
    uint32_t uid=rd32(item+4u);
    for(uint32_t i=0;i<64u;++i){
        uint8_t *entry=audio_ble_ancc_state+0x1cu+i*12u;
        if(entry[8u]==1u && rd32(entry+4u)==uid){
            for(uint32_t j=0;j<4u;++j)entry[j]=item[j];
            wr32(entry+4u,uid);
            return 1u;
        }
    }
    for(uint32_t i=0;i<64u;++i){
        uint8_t *entry=audio_ble_ancc_state+0x1cu+i*12u;
        if(entry[8u]==0u){
            for(uint32_t j=0;j<4u;++j)entry[j]=item[j];
            wr32(entry+4u,uid);
            entry[8u]=1u;
            return 1u;
        }
    }
    return 0u;
}

void audio_ble_ancc_remove_callback_4bee0a(const uint8_t *item){
    static const char fn[]="_anccNotiRemoveCback";
    static const char message[]="Nofity removed, category_id = %d";
    static const char compact[]="[ble.ancc]Nofity removed, category_id = %d";
    if(audio_log_level()&2u)
        audio_log_extended(4u,module,path,fn,0x185u,message,item[2u]);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10400000u,compact,compact,item[2u]);
}

void audio_ble_ancc_notification_value_update_4bee5a(uint8_t *handles,const uint8_t *event){
    uint16_t handle=rd16(event+10u);
    uint32_t data_address=rd32(event+4u);
    const uint8_t *data=(const uint8_t *)(uintptr_t)data_address;
    if(handle==rd16(handles)){
        uint8_t item[8];for(uint32_t i=0;i<8u;++i)item[i]=data[i];
        if(item[0]==2u){audio_ble_ancc_remove_callback_4bee0a(item);return;}
        if(audio_ble_ancc_action_push_4bec20(item)==0u){
            static const char full[]="action list full...";
            static const char compact[]="[ble.ancc]action list full...";
            if(audio_log_level()&2u)
                audio_log_extended(2u,module,path,"_anccNtfValueUpdate",0x1acu,full);
            if((audio_log_level()&1u)||(audio_log_level()&4u))
                (void)compressed_log_output(0x08000000u,compact);
        }else{
            static const char message[]="added to action list, notification_uid: %lu, event_id: %d";
            static const char compact[]="[ble.ancc]added to action list, notification_uid: %lu, event_id: %d";
            if(audio_ble_ancc_no_connection_active_4bea24()==0u)
                audio_event_loop_push_delayed((void (*)(void))audio_ble_ancc_get_next_delayed_4bea7a,0xa2u,200u);
            if(audio_log_level()&2u)
                audio_log_extended(4u,module,path,"_anccNtfValueUpdate",0x1b6u,message,rd32(item+4u),item[0]);
            if((audio_log_level()&1u)||(audio_log_level()&4u))
                (void)compressed_log_output(0x10800000u,compact,compact,rd32(item+4u),item[0]);
        }
    }else if(handle==rd16(handles+6u)){
        static const char message[]="Processing data source, current attrState: %d, attrCount: %d";
        static const char compact[]="[ble.ancc]Processing data source, current attrState: %d, attrCount: %d";
        uint16_t count=rd16(audio_ble_ancc_state+0x14u);
        if(audio_log_level()&2u)
            audio_log_extended(4u,module,path,"_anccNtfValueUpdate",0x1bcu,message,audio_ble_ancc_state[10u],count);
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x10800000u,compact,compact,audio_ble_ancc_state[10u],count);
        do {} while(audio_ble_ancc_attr_handler_4bf228(data,rd16(event+8u))!=0u);
    }
}
