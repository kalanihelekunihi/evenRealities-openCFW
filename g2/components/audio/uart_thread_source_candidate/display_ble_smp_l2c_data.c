/* Native smpL2cDataCback 0x537278. Thumb entry recreates the native
 * push/sub stack frame, preserving its ambient byte at SP+3 for normal
 * commands. The C body writes only the bytes written by native code. */
#include <stdint.h>
extern uint8_t *smpCcbByHandle(uint16_t);
extern const uint8_t audio_ble_smp_packet_lengths[16];
extern void smpSmExecute(uint8_t *,const uint8_t *);
extern volatile uint8_t audio_ble_trace_level_cell;
extern uint32_t g2_smp_candidate_compare(void *,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
static const char warn[]="WARN",err[]="ERR",info[]="INFO",smp[]="SMP",hci[]="HCI";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\smp\\smp_main.c";
static const char fn[]="smpL2cDataCback";
static const char unexpected[]="unexpected packet cmd:%d len:%d, expected:%d";
static uint32_t cmp(const char *a,const char *b,uint32_t n){
    return g2_smp_candidate_compare(0u,(uint32_t)(uintptr_t)a,(uint32_t)(uintptr_t)b,n);
}
static void trace_unexpected(uint8_t command,uint16_t length,uint8_t expected){
    uint8_t level=0u;
    if(audio_ble_trace_level_cell!=0u){
        if(cmp(warn,err,3u)==0u)level=1u;
        else if(cmp(warn,warn,4u)==0u)level=2u;
        else if(cmp(warn,info,4u)==0u)level=3u;
        else level=4u;
    }
    if(level!=0u){
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(level,smp,path,fn,0x77u,unexpected,command,length,expected);
    }else if(audio_ble_trace_level_cell==0u||cmp(smp,hci,3u)!=0u)
        audio_ble_wsf_trace(warn,unexpected,command,length,expected);
}
__attribute__((used,noinline))
static void audio_ble_smp_l2c_data_body(uint16_t handle,uint16_t length,
                                       const uint8_t *packet,uint8_t *event){
    uint8_t *ccb=smpCcbByHandle(handle);
    if(ccb==0)return;
    const uint8_t command=packet[8];
    if(command==0u||command>14u||length!=audio_ble_smp_packet_lengths[command]||
       (command!=ccb[0x3fu]&&command!=5u)){
        trace_unexpected(command,length,ccb[0x3fu]);
        return;
    }
    event[0]=ccb[0x3du];event[1]=0u;
    event[2]=command==5u?7u:6u;
    if(command==5u)event[3]=packet[9];
    const uint32_t address=(uint32_t)(uintptr_t)packet;
    event[4]=(uint8_t)address;event[5]=(uint8_t)(address>>8);
    event[6]=(uint8_t)(address>>16);event[7]=(uint8_t)(address>>24);
    smpSmExecute(ccb,event);
}
__attribute__((naked))
void audio_ble_smp_l2c_data_callback_537278(
    uint16_t handle __attribute__((unused)),uint16_t length __attribute__((unused)),
    const uint8_t *packet __attribute__((unused)),uint32_t inherited __attribute__((unused))){
    __asm volatile(
        "push {r3-r7, lr}\n"
        "sub sp, #24\n"
        "mov r3, sp\n"
        "bl audio_ble_smp_l2c_data_body\n"
        "add sp, #24\n"
        "pop {r3-r7, pc}\n");
}
