/* Native profile CCC state callbacks 0x4bdb90, 0x4bde4c, 0x4be228,
 * 0x4be3a4, 0x4be6f0. Product state cells are external runtime data. */
#include <stdint.h>
extern uint8_t audio_ble_ota_handler_state[4];
extern uint8_t audio_ble_eus_handler_state[4];
extern uint8_t audio_ble_ess_handler_state[4];
extern uint8_t audio_ble_efs_handler_state[4];
extern uint8_t audio_ble_nus_handler_state[4];
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static uint16_t half(const uint8_t *p,unsigned n) {
    return (uint16_t)p[n]|(uint16_t)((uint16_t)p[n+1u]<<8);
}
static void update(uint8_t *state,const uint8_t *message,uint8_t index,
                   const char *module,const char *path,const char *function,
                   uint32_t line,const char *plain,const char *compact) {
    if(message[8]!=index)return;
    uint32_t value=half(message,6u),handle=half(message,4u);
    if(plain) {
        if(audio_log_level()&2u)
            audio_log_extended(4u,module,path,function,line,plain,value,handle,index);
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x10c00000u,compact,compact,value,handle,index);
    }
    if(value==1u) {state[0]=message[0];state[2]=1u;}
    else {state[0]=0u;state[2]=0u;}
}
#define PATH(profile) "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\" profile "\\profile_" profile ".c"
void audio_ble_ota_update(void *raw) {
    update(audio_ble_ota_handler_state,(const uint8_t *)raw,1u,
           "profile.ota",PATH("ota"),"_evenOtaProcCccState",0x5eu,
           "ccc state ind value:%d handle:%d idx:%d",
           "[profile.ota]ccc state ind value:%d handle:%d idx:%d");
}
void audio_ble_eus_update(void *raw) {
    update(audio_ble_eus_handler_state,(const uint8_t *)raw,2u,
           "profile.eus",PATH("eus"),"eusProcCccState",0x42u,
           "eusProcCccState ccc state ind value=%d,handle=%d,idx=%d",
           "[profile.eus]eusProcCccState ccc state ind value=%d,handle=%d,idx=%d");
}
void audio_ble_ess_update(void *raw) {
    update(audio_ble_ess_handler_state,(const uint8_t *)raw,3u,0,0,0,0u,0,0);
}
void audio_ble_efs_update(void *raw) {
    update(audio_ble_efs_handler_state,(const uint8_t *)raw,4u,
           "profile.efs",PATH("efs"),"efsProcCccState",0x41u,
           "efsProcCccState ccc state ind value=%d,handle=%d,idx=%d",
           "[profile.efs]efsProcCccState ccc state ind value=%d,handle=%d,idx=%d");
}
void audio_ble_nus_update(void *raw) {
    update(audio_ble_nus_handler_state,(const uint8_t *)raw,5u,
           "profile.nus",PATH("nus"),"nusProcCccState",0x43u,
           "nusProcCccState ccc state ind value=%d,handle=%d,idx=%d",
           "[profile.nus]nusProcCccState ccc state ind value=%d,handle=%d,idx=%d");
}
