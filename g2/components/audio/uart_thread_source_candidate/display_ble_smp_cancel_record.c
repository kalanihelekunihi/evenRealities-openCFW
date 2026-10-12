/* Native Cordio SMP CCB lookup 0x5375fc, cancellation 0x56d188,
 * pairing-failure record update 0x542838. Diagnostic branches retained. */
#include <stdint.h>

extern uint8_t audio_ble_smp_handler_state[]; /* live 0x20070aec */
extern uint8_t audio_ble_smp_database[];      /* live 0x200708ec */
extern const uint8_t *audio_ble_comm_registration_slot; /* live pointer 0x200004b8 */
extern volatile uint8_t audio_ble_trace_level_cell; /* live 0x2007502f */
extern uint32_t g2_smp_candidate_compare(void *,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
extern uint8_t *smpDbGetRecord(uint8_t); /* native 0x541fb8 */

static const char err[]="ERR", warn[]="WARN", info[]="INFO";
static const char smp[]="SMP", hci[]="HCI";
static const char smp_main[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\smp\\smp_main.c";
static const char sc_main[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\smp\\smp_sc_main.c";
static const char db_main[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\smp\\smp_db.c";
static const char ccb_name[]="smpCcbByConnId", cancel_name[]="SmpScGetCancelMsgWithReattempt", fail_name[]="SmpDbPairingFailed";
static const char ccb_msg[]="Invalid connId in smpCcbByConnId: %d";
static const char cancel_msg[]="SmpScGetCancelMsgWithReattempt: %d";
static const char fail_msg[]="SmpDbPairingFailed: connId: %d";

static uint32_t cmp(const char *a,const char *b,uint32_t n) {
    return g2_smp_candidate_compare(0,(uint32_t)(uintptr_t)a,(uint32_t)(uintptr_t)b,n);
}
static void diagnostic(uint8_t severity,const char *path,const char *name,
                       uint32_t line,const char *msg,uint32_t value) {
    const char *tag=severity==2u?warn:info;
    uint8_t level=0u;
    if(audio_ble_trace_level_cell!=0u && cmp(tag,err,3u)==0u)level=1u;
    else if(audio_ble_trace_level_cell!=0u && cmp(tag,warn,4u)==0u)level=2u;
    else if(audio_ble_trace_level_cell!=0u && cmp(tag,info,4u)==0u)level=3u;
    else if(audio_ble_trace_level_cell!=0u)level=4u;
    if(level!=0u) {
        if(audio_log_flags()&2u)
            audio_log_extended(level,smp,path,name,line,msg,value);
    } else {
        /* Native disabled-policy branch tests SMP versus HCI before WsfTrace. */
        if(audio_ble_trace_level_cell==0u || cmp(smp,hci,3u)!=0u)
            audio_ble_wsf_trace(tag,msg,value);
    }
}

uint8_t *smpCcbByConnId(uint8_t conn) {
    if(conn!=0u)return audio_ble_smp_handler_state+(uint32_t)(conn-1u)*0x4cu;
    diagnostic(2u,smp_main,ccb_name,0x133u,ccb_msg,0u);
    return 0;
}
void SmpDbPairingFailed(uint8_t conn) {
    uint8_t *record=smpDbGetRecord(conn);
    diagnostic(3u,db_main,fail_name,0x14du,fail_msg,conn);
    __builtin_memcpy(record+0x10u,audio_ble_comm_registration_slot+0x10u,4u);
}
void SmpScGetCancelMsgWithReattempt(uint8_t conn,void *packet,uint8_t reason) {
    uint8_t *ccb=smpCcbByConnId(conn);
    uint8_t *message=(uint8_t *)packet;
    diagnostic(3u,sc_main,cancel_name,0x248u,cancel_msg,ccb[0x42u]);
    ccb[0x42u]=(uint8_t)(ccb[0x42u]+1u);
    message[0]=conn;message[1]=0u;message[3]=reason;
    SmpDbPairingFailed(conn);
    message[2]=ccb[0x42u]==audio_ble_comm_registration_slot[7u]?0x0du:3u;
}
