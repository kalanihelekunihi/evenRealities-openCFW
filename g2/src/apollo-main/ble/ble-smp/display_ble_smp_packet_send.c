/* Native smpSendPkt 0x537a5a and L2cDataReq 0x530bbc.
 * 0x537ba4..b2 explicitly sets all four ARM argument registers before BL:
 * R0=6, R1=CCB handle, R2=authenticated size[packet[8]], R3=packet.
 * The decompiler's fifth-through-seventh arguments are ambient registers,
 * unused by the native four-register L2cDataReq body. */
#include <stdint.h>
extern void HciSendAclData(void *);
extern void audio_ble_wsf_message_free(void *);
extern volatile uint8_t audio_ble_trace_level_cell;
extern uint32_t g2_smp_candidate_compare(void *,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
const uint8_t audio_ble_smp_packet_lengths[16]={0,7,7,17,17,2,17,11,17,8,17,2,65,17,2,0};
static const char info[]="INFO",err[]="ERR",warn[]="WARN",smp[]="SMP",hci[]="HCI";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\smp\\smp_main.c";
static const char fn[]="smpSendPkt";
static const char discarded[]="smpSendPkt packet discarded cmd:%d";
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static void wr32(uint8_t *p,uint32_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);}
static uint32_t cmp(const char *a,const char *b,uint32_t n){
    return g2_smp_candidate_compare(0u,(uint32_t)(uintptr_t)a,(uint32_t)(uintptr_t)b,n);
}
static void trace_discarded(uint8_t command){
    uint8_t level=0u;
    if(audio_ble_trace_level_cell!=0u){
        if(cmp(warn,err,3u)==0u)level=1u;
        else if(cmp(warn,warn,4u)==0u)level=2u;
        else if(cmp(warn,info,4u)==0u)level=3u;
        else level=4u;
    }
    if(level!=0u){
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(level,smp,path,fn,0x255u,discarded,command);
    }else if(audio_ble_trace_level_cell==0u||cmp(smp,hci,3u)!=0u)
        audio_ble_wsf_trace(warn,discarded,command);
}
void L2cDataReq(uint16_t cid,uint16_t handle,uint16_t length,uint8_t *packet){
    packet[0]=(uint8_t)handle;packet[1]=(uint8_t)(handle>>8);
    packet[2]=(uint8_t)(length+4u);packet[3]=(uint8_t)((length+4u)>>8);
    packet[4]=(uint8_t)length;packet[5]=(uint8_t)(length>>8);
    packet[6]=(uint8_t)cid;packet[7]=(uint8_t)(cid>>8);
    HciSendAclData(packet);
}
void smpSendPkt(uint8_t *ccb,void *packet_void){
    uint8_t *packet=(uint8_t *)packet_void;
    if(ccb[0x3cu]==0u){
        L2cDataReq(6u,rd16(ccb+0x38u),audio_ble_smp_packet_lengths[packet[8]],packet);
    }else{
        uint32_t pending=(uint32_t)ccb[0x34u]|((uint32_t)ccb[0x35u]<<8)|
                         ((uint32_t)ccb[0x36u]<<16)|((uint32_t)ccb[0x37u]<<24);
        if(pending!=0u){
            trace_discarded(*(const uint8_t *)(uintptr_t)(pending+8u));
            audio_ble_wsf_message_free((void *)(uintptr_t)pending);
        }
        wr32(ccb+0x34u,(uint32_t)(uintptr_t)packet);
    }
}
