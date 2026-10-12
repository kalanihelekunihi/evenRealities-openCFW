/* Native DmConnPeerRpa/LocalRpa 0x4b6f28/0x4b707c; pinned Cordio dm_conn.c. */
#include <stdint.h>
extern uint8_t audio_dm_connection_records[]; /* native RAM 0x200712a4 */
extern volatile uint8_t audio_ble_trace_level_cell;
extern uint32_t g2_smp_candidate_compare(void *,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
static const char error[]="ERR",warn[]="WARN",info[]="INFO";
static const char dm[]="DM",hci[]="HCI";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\dm\\dm_conn.c";
static const char peer_name[]="DmConnPeerRpa",local_name[]="DmConnLocalRpa";
static const char peer_message[]="Invalid connId in DmConnPeerRpa: %d";
static const char local_message[]="Invalid connId in DmConnLocalRpa: %d";

static uint32_t compare(const char *left,const char *right,uint32_t n)
{
    return g2_smp_candidate_compare(0,(uint32_t)(uintptr_t)left,
                                     (uint32_t)(uintptr_t)right,n);
}
static void invalid_connection(const char *name,uint32_t line,const char *message)
{
    uint8_t level=0u;
    if (audio_ble_trace_level_cell!=0u && compare(warn,error,3u)==0u)level=1u;
    else if (audio_ble_trace_level_cell!=0u && compare(warn,warn,4u)==0u)level=2u;
    else if (audio_ble_trace_level_cell!=0u && compare(warn,info,4u)==0u)level=3u;
    else if (audio_ble_trace_level_cell!=0u)level=4u;
    if (level!=0u) {
        if (audio_log_flags()&2u)
            audio_log_extended(level,dm,path,name,line,message,0u);
    } else if (audio_ble_trace_level_cell==0u || compare(dm,hci,3u)!=0u) {
        audio_ble_wsf_trace(warn,message,0u);
    }
}

uint8_t *DmConnPeerRpa(uint8_t connection)
{
    if (connection==0u) {
        invalid_connection(peer_name,0x691u,peer_message);
        return 0;
    }
    uintptr_t address=(uintptr_t)audio_dm_connection_records
        +(uint32_t)connection*0x30u-0x10u;
    return (uint8_t *)address;
}
uint8_t *DmConnLocalRpa(uint8_t connection)
{
    if (connection==0u) {
        invalid_connection(local_name,0x6a6u,local_message);
        return 0;
    }
    uintptr_t address=(uintptr_t)audio_dm_connection_records
        +(uint32_t)connection*0x30u-0x16u;
    return (uint8_t *)address;
}
