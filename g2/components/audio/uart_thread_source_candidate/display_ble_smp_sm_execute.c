/* Native Cordio smpSmExecute 0x56ee62. The selected SMP init routines own
 * table pointer installation; transition/action tables remain typed ROM. */
#include <stdint.h>
extern uint8_t audio_ble_smp_handler_state[];
extern uint8_t audio_dm_conn_role(uint8_t);
extern volatile uint8_t audio_ble_trace_level_cell;
extern uint32_t g2_smp_candidate_compare(void *,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
extern const char *smpStateStr(uint8_t);
extern const char *smpEventStr(uint8_t);
static const char info[]="INFO",err[]="ERR",warn[]="WARN",smp[]="SMP",hci[]="HCI";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\smp\\smp_act.c";
static const char fn[]="smpSmExecute";
static const char numeric[]="smpSmExecute event=%d state=%d";
static const char named[]="SMP Exe: evt=%s st=%s";
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint32_t cmp(const char *a,const char *b,uint32_t n){
    return g2_smp_candidate_compare(0u,(uint32_t)(uintptr_t)a,(uint32_t)(uintptr_t)b,n);
}
static uint8_t trace_level(void){
    if(audio_ble_trace_level_cell==0u)return 0u;
    if(cmp(info,err,3u)==0u)return 1u;
    if(cmp(info,warn,4u)==0u)return 2u;
    if(cmp(info,info,4u)==0u)return 3u;
    return 4u;
}
void smpSmExecute(uint8_t *ccb,const uint8_t *message){
    const uint8_t event=message[2];
    const uint8_t state=ccb[0x3eu];
    const uint32_t profile=rd32(ccb+0x48u);
    const uint8_t named_trace=(audio_ble_smp_handler_state[0xf8u]!=0u&&
                               profile!=0u&&
                               *(const uint8_t *)(uintptr_t)profile!=0u);
    const uint8_t level=trace_level();
    if(named_trace){
        if(level!=0u){
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(level,smp,path,fn,0x354u,named,
                                   smpEventStr(event),smpStateStr(state));
        }else if(audio_ble_trace_level_cell==0u||cmp(smp,hci,3u)!=0u)
            audio_ble_wsf_trace(info,named,smpEventStr(event),smpStateStr(state));
    }else{
        if(level!=0u){
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(level,smp,path,fn,0x357u,numeric,event,state);
        }else if(audio_ble_trace_level_cell==0u||cmp(smp,hci,3u)!=0u)
            audio_ble_wsf_trace(info,numeric,event,state);
    }
    const uint32_t descriptor=rd32(audio_ble_smp_handler_state+
                                   (audio_dm_conn_role(ccb[0x3du])==1u?0xe4u:0xe8u));
    const uint8_t *const table=(const uint8_t *)(uintptr_t)descriptor;
    const uint32_t rows=rd32(table);
    const uint32_t actions=rd32(table+4u);
    const uint32_t fallback=rd32(table+8u);
    const uint8_t *transition=(const uint8_t *)(uintptr_t)rd32((const uint8_t *)(uintptr_t)rows+
                                                        (uint32_t)state*4u);
    for(;;){
        do{
            if(transition[0]==event){
                ccb[0x3eu]=transition[1];
                const uint32_t target=rd32((const uint8_t *)(uintptr_t)actions+
                                            (uint32_t)transition[2]*4u);
                ((void (*)(uint8_t *,const uint8_t *))(uintptr_t)target)(ccb,message);
                return;
            }
            transition+=3u;
        }while(transition[0]!=0u);
        if((uintptr_t)transition==(uintptr_t)fallback+12u)return;
        transition=(const uint8_t *)(uintptr_t)fallback;
    }
}
