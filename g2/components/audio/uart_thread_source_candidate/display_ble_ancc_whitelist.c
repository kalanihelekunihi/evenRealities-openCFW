/* Native SVC_IsOnWhitelistByIdentifier 0x4d67b8. The product list at
 * 0x20054718 is live RAM; its initializer is a separate contract. */
#include <stdint.h>
extern uint8_t audio_ble_ancc_service_state[]; /* base 0x200036c8 */
extern uint8_t audio_ble_whitelist_info[]; /* base 0x20054718 */
extern uint32_t g2_log_module_length(const char *); /* selected strlen 0x44a43c */
extern int32_t audio_l2c_strncmp(const char *,const char *,uint32_t); /* selected 0x44b610 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
static const char module[]="svc.whitelist";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\message_notify\\service_whitelist.c";
static const char fn[]="SVC_IsOnWhitelistByIdentifier";
static void log0(uint8_t level,uint32_t line,const char *plain,uint32_t code,const char *compact){
    if(audio_log_level()&2u)audio_log_extended(level,module,path,fn,line,plain);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(code,compact,compact);
}
static void log1(uint8_t level,uint32_t line,const char *plain,uint32_t code,const char *compact,uint32_t value){
    if(audio_log_level()&2u)audio_log_extended(level,module,path,fn,line,plain,value);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(code,compact,compact,value);
}

uint8_t audio_ble_ancc_whitelist_type_4d67b8(const uint8_t *id){
    static const char disabled[]="whitelist is disable !";
    static const char disabled_short[]="[svc.whitelist]whitelist is disable !";
    if(audio_ble_ancc_service_state[4u]==1u){
        log0(4u,0x13au,disabled,0x10000000u,disabled_short);return 2u;
    }
    if(id==0){
        static const char bad[]="[%s-%d] pkg_name is NULL !";
        static const char bad_short[]="[svc.whitelist][%s-%d] pkg_name is NULL !";
        if(audio_log_level()&2u)audio_log_extended(1u,module,path,fn,0x13fu,bad,fn,0x13fu);
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x04800000u,bad_short,bad_short,fn,0x13fu);
        return 0u;
    }
    uint32_t length=g2_log_module_length((const char *)id);
    if(length>=64u){
        static const char bad[]="[%s-%d] pkg_name length is too long !";
        static const char bad_short[]="[svc.whitelist][%s-%d] pkg_name length is too long !";
        if(audio_log_level()&2u)audio_log_extended(1u,module,path,fn,0x143u,bad,fn,0x143u);
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x04800000u,bad_short,bad_short,fn,0x143u);
        return 0u;
    }
    if(audio_l2c_strncmp("com.even.sg",(const char *)id,11u)==0 ||
       audio_l2c_strncmp("com.even.g1",(const char *)id,11u)==0)return 2u;
    static const char count_msg[]="appcounts is %d ";
    static const char count_short[]="[svc.whitelist]appcounts is %d ";
    log1(4u,0x17du,count_msg,0x10400000u,count_short,audio_ble_whitelist_info[1u]);
    if(((audio_ble_whitelist_info[0u]&0x1fu)>>4)!=0u && audio_ble_whitelist_info[1u]!=0u){
        for(uint8_t i=0u;i<audio_ble_whitelist_info[1u];i=(uint8_t)(i+1u)){
            const uint8_t *entry=audio_ble_whitelist_info+2u+(uint32_t)i*0x50u;
            static const char row_msg[]="_g_appWhiteListInfo.listAppInfo[%d].id is %s ";
            static const char row_short[]="[svc.whitelist]_g_appWhiteListInfo.listAppInfo[%d].id is %s ";
            if(audio_log_level()&2u)audio_log_extended(4u,module,path,fn,0x182u,row_msg,i,entry);
            if((audio_log_level()&1u)||(audio_log_level()&4u))
                (void)compressed_log_output(0x10800000u,row_short,row_short,i,entry);
            uint32_t n=g2_log_module_length((const char *)entry);
            if(audio_l2c_strncmp((const char *)entry,(const char *)id,n)==0)return 2u;
        }
    }
    static const char blocked[]="[WHITELIST] Notification BLOCKED for: %s (not in whitelist)";
    static const char blocked_short[]="[svc.whitelist][WHITELIST] Notification BLOCKED for: %s (not in whitelist)";
    if(audio_log_level()&2u)audio_log_extended(4u,module,path,fn,400u,blocked,id);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10400000u,blocked_short,blocked_short,id);
    return 1u;
}
