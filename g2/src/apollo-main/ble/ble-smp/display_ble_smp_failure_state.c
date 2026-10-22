/* Native SMP DB failure state 0x5422c4/0x542418/0x54257c.
 * The selected smpDbGetRecord owns record selection. */
#include <stdint.h>
extern uint8_t *smpDbGetRecord(uint8_t);
extern const uint8_t *audio_ble_comm_registration_slot;
extern volatile uint8_t audio_ble_trace_level_cell;
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t); /* 0x44b610 bounded strncmp */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
static const char info[]="INFO",err[]="ERR",warn[]="WARN",smp[]="SMP",hci[]="HCI";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\smp\\smp_db.c";
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void wr32(uint8_t *p,uint32_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);}
static uint32_t cmp(const char *a,const char *b,uint32_t n){
    return (uint32_t)audio_ble_hci_vendor_compare_44b610(a,b,n);
}
static void trace2(uint32_t line,const char *fn,const char *fmt,uint32_t a,uint32_t b){
    uint8_t level=0u;
    if(audio_ble_trace_level_cell!=0u){
        if(cmp(info,err,3u)==0u)level=1u;
        else if(cmp(info,warn,4u)==0u)level=2u;
        else if(cmp(info,info,4u)==0u)level=3u;
        else level=4u;
    }
    if(level!=0u){if((audio_log_flags()&2u)!=0u)audio_log_extended(level,smp,path,fn,line,fmt,a,b);}
    else if(audio_ble_trace_level_cell==0u||cmp(smp,hci,3u)!=0u)
        audio_ble_wsf_trace(info,fmt,a,b);
}
static void trace3(uint32_t line,const char *fn,const char *fmt,uint32_t a,uint32_t b,uint32_t c){
    uint8_t level=0u;
    if(audio_ble_trace_level_cell!=0u){
        if(cmp(info,err,3u)==0u)level=1u;
        else if(cmp(info,warn,4u)==0u)level=2u;
        else if(cmp(info,info,4u)==0u)level=3u;
        else level=4u;
    }
    if(level!=0u){if((audio_log_flags()&2u)!=0u)audio_log_extended(level,smp,path,fn,line,fmt,a,b,c);}
    else if(audio_ble_trace_level_cell==0u||cmp(smp,hci,3u)!=0u)
        audio_ble_wsf_trace(info,fmt,a,b,c);
}
uint32_t SmpDbGetPairingDisabledTime(uint8_t connection){
    const uint8_t *record=smpDbGetRecord(connection);
    const uint32_t period=rd32(record+0x0cu);
    trace3(0xe4u,"SmpDbGetPairingDisabledTime",
           "SmpDbGetPairingDisabledTime: connId: %d period: %d attemptMult: %d",
           connection,period,rd16(record+8u));
    return period;
}
uint8_t SmpDbGetFailureCount(uint8_t connection){
    const uint8_t *record=smpDbGetRecord(connection);
    const uint8_t count=record[7u];
    trace2(0x10eu,"SmpDbGetFailureCount",
           "SmpDbGetFailureCount: connId: %d count: %d",connection,count);
    return count;
}
void SmpDbSetFailureCount(uint8_t connection,uint8_t count){
    uint8_t *record=smpDbGetRecord(connection);
    trace2(0xf7u,"SmpDbSetFailureCount",
           "SmpDbSetFailureCount: connId: %d count: %d",connection,count);
    record[7u]=count;
    if(count!=0u)wr32(record+0x14u,rd32(audio_ble_comm_registration_slot+0x0cu));
}
