/* Native attsCsfSetHashUpdateStatus 0x52c6c0; pinned Cordio atts_csf.c. */
#include <stdint.h>
extern uint8_t audio_ble_connection_state_table[]; /* native attsCsfCb 0x20073e04 */
extern volatile uint8_t audio_ble_trace_level_cell;
extern uint32_t g2_smp_candidate_compare(void *,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
extern void attsCheckPendDbHashReadRsp(void);
static const char info[]="INFO",error[]="ERR",warn[]="WARN";
static const char att[]="ATT",hci[]="HCI";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_csf.c";
static const char name[]="attsCsfSetHashUpdateStatus";
static const char complete[]="Database hash calculation complete";
static const char calculating[]="Calculating database hash";
static uint32_t compare(const char *a,const char *b,uint32_t n)
{
    return g2_smp_candidate_compare(0,(uint32_t)(uintptr_t)a,(uint32_t)(uintptr_t)b,n);
}
static void diagnostic(const char *message,uint32_t line)
{
    uint8_t level=0u;
    if (audio_ble_trace_level_cell!=0u && compare(info,error,3u)==0u)level=1u;
    else if (audio_ble_trace_level_cell!=0u && compare(info,warn,4u)==0u)level=2u;
    else if (audio_ble_trace_level_cell!=0u && compare(info,info,4u)==0u)level=3u;
    else if (audio_ble_trace_level_cell!=0u)level=4u;
    if (level!=0u) {
        if (audio_log_flags()&2u)
            audio_log_extended(level,att,path,name,line,message);
    } else if (audio_ble_trace_level_cell==0u || compare(att,hci,3u)!=0u) {
        audio_ble_wsf_trace(info,message);
    }
}
void attsCsfSetHashUpdateStatus(uint8_t updating)
{
    uint8_t *const state=audio_ble_connection_state_table;
    if (state[0x0cu]==updating) return;
    state[0x0cu]=updating;
    if (updating==0u) {
        diagnostic(complete,0x48u);
        attsCheckPendDbHashReadRsp();
    } else {
        diagnostic(calculating,0x55u);
        for (uint8_t i=0u;i<3u;i++) {
            uint8_t *const awareness=state+(uint32_t)i*2u+1u;
            if (*awareness==2u) *awareness=1u;
        }
    }
}
