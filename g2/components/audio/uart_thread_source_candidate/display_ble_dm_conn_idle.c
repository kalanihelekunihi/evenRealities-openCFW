/* Native DmConnSetIdle 0x4b71dc, pinned Cordio dm_conn.c including trace. */
#include <stdint.h>
extern uint8_t audio_dm_connection_records[]; /* dmConnCb RAM 0x200712a4 */
extern volatile uint8_t audio_ble_trace_level_cell; /* live trace policy */
extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);
extern uint8_t DmConnInUse(uint8_t connection);
extern uint32_t g2_smp_candidate_compare(void *,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);

static const char info[]="INFO", err[]="ERR", warn[]="WARN";
static const char dm[]="DM", hci[]="HCI";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\dm\\dm_conn.c";
static const char name[]="DmConnSetIdle";
static const char format[]="connId=%d idleMask=0x%04x";
static uint32_t compare(const char *left,const char *right,uint32_t size) {
    return g2_smp_candidate_compare(0,(uint32_t)(uintptr_t)left,
                                     (uint32_t)(uintptr_t)right,size);
}
static void trace(uint8_t connection,uint16_t mask) {
    uint8_t level=0u;
    if (audio_ble_trace_level_cell!=0u && compare(info,err,3u)==0u)level=1u;
    else if (audio_ble_trace_level_cell!=0u && compare(info,warn,4u)==0u)level=2u;
    else if (audio_ble_trace_level_cell!=0u && compare(info,info,4u)==0u)level=3u;
    else if (audio_ble_trace_level_cell!=0u)level=4u;
    if (level!=0u) {
        if (audio_log_flags()&2u)
            audio_log_extended(level,dm,path,name,0x6ddu,format,connection,mask);
    } else if (audio_ble_trace_level_cell==0u || compare(dm,hci,3u)!=0u) {
        audio_ble_wsf_trace(info,format,connection,mask);
    }
}
void DmConnSetIdle(uint8_t connection,uint16_t idle_mask,uint8_t idle) {
    uintptr_t address=(uintptr_t)audio_dm_connection_records
        +(uint32_t)connection*0x30u-0x22u;
    volatile uint16_t *slot=(volatile uint16_t *)address;
    WsfTaskLock();
    if (DmConnInUse(connection)) {
        if (idle==0u) *slot=(uint16_t)(*slot & (uint16_t)~idle_mask);
        else *slot=(uint16_t)(*slot | idle_mask);
    }
    WsfTaskUnlock();
    trace(connection,*slot);
}
