/* Native Cordio SmpHandler 0x537d0c. Queue and CCB are live SMP state. */
#include <stdint.h>
extern uint32_t SmpDbService(void); /* native 0x542960, inherited R3 result ignored */
extern void WsfBufFree(void *);
extern uint8_t *smpCcbByConnId(uint8_t);
extern void smpSmExecute(uint8_t *,const uint8_t *);
extern void *audio_ble_wsf_message_dequeue(void *,uint8_t *);
extern void audio_ble_wsf_message_free(void *);
extern uint8_t audio_ble_stack_state_20072cb8[]; /* selected secCb; AES queue at +0x20 */
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *,const char *,uint32_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
static const char warn[]="WARN",err[]="ERR",info[]="INFO",hci[]="HCI",module[]="SMP";
static const char message[]="AES token mismatch: %d %d";
static const char function_name[]="SmpHandler";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\smp\\smp_main.c";
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}

static void mismatch_trace(uint8_t previous,uint8_t received){
    uint8_t level=0u;
    if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,err,3u)==0)level=1u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,warn,4u)==0)level=2u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,info,4u)==0)level=3u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u)level=4u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()==0u||audio_l2c_strncmp(module,hci,3u)!=0)
        audio_ble_wsf_trace(warn,message,previous,received);
    if(level!=0u&&(audio_log_level()&2u)!=0u)
        audio_log_extended(level,module,path,function_name,0x375u,message,previous,received);
}

void audio_ble_smp_handler_537d0c(uint32_t handler __attribute__((unused)),uint8_t *event){
    if(event==0)return;
    if(event[2]==0x20u){SmpDbService();return;}
    if(event[2]==0x1cu){uint32_t buffer=rd32(event+8u);if(buffer!=0u)WsfBufFree((void *)(uintptr_t)buffer);}
    uint8_t *ccb=smpCcbByConnId(event[0]);
    if(ccb[0x3du]==0u)return;
    if(event[2]==0x0bu&&ccb[0x41u]!=event[3]){
        mismatch_trace(ccb[0x41u],event[3]);
        uint8_t handler_id=0u;
        void *message;
        while((message=audio_ble_wsf_message_dequeue(audio_ble_stack_state_20072cb8+0x20u,&handler_id))!=0)
            audio_ble_wsf_message_free(message);
        return;
    }
    smpSmExecute(ccb,event);
}
