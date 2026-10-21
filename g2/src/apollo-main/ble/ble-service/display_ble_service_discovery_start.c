/* Native Cordio appDiscStart 0x531d60 and byte comparator 0x44b610.
 * Product runtime rows/callbacks stay explicit. */
#include <stdint.h>
extern volatile uint8_t audio_ble_trace_level_cell; /* 0x2007502f */
extern uint8_t audio_ble_subsystem_rows_200733fc[];
extern uintptr_t audio_ble_service_dispatch_20074348;
extern uint8_t *audio_ble_pair_record(uint8_t); /* selected 0x4bb07c */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
extern void audio_ble_service_discovery_step_531bd4(uint8_t,uint8_t);
extern void audio_ble_service_discovery_followup_5336e0(uint8_t);

int32_t audio_ble_hci_vendor_compare_44b610(const void *left,const void *right,uint32_t size) {
    const uint8_t *a=(const uint8_t *)left,*b=(const uint8_t *)right;
    while(size!=0u) {
        uint8_t x=*a,y=*b;
        if(x!=y)return x<y?-1:1;
        if(x==0u)return 0;
        ++a;++b;--size;
    }
    return 0;
}
static void discovery_log(uint8_t level) {
    static const char module[]="APP";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_disc.c";
    static const char name[]="appDiscStart";
    static const char message[]="Invalid connId in appDiscStart: %d";
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(level,module,source,name,0x7cu,message,0u);
}
void audio_ble_service_discovery_start(uint8_t connection) {
    static const char warn[]="WARN",error[]="ERR",info[]="INFO",hci[]="HCI",app[]="APP";
    static const char message[]="Invalid connId in appDiscStart: %d";
    if(connection==0u) {
        if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(warn,error,3u)!=0) {
            if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(warn,warn,4u)!=0) {
                if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(warn,info,4u)!=0) {
                    if(audio_ble_trace_level_cell==0u) {
                        if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(app,hci,3u)!=0)
                            audio_ble_wsf_trace(warn,message,0u);
                    } else discovery_log(4u);
                } else discovery_log(3u);
            } else discovery_log(2u);
        } else discovery_log(1u);
        return;
    }
    uint8_t *row=audio_ble_subsystem_rows_200733fc+((uint32_t)connection-1u)*0x10u;
    if(row[11u]!=0u)return;
    uint8_t *record=audio_ble_pair_record(connection);
    uint8_t stage=record==0 ? row[9u] : 0u;
    if(stage<4u) {
        ((void (*)(uint8_t,uint8_t))audio_ble_service_dispatch_20074348)(connection,3u);
        return;
    }
    if(stage==5u)return;
    uint32_t destination=(uint32_t)row[4u]|((uint32_t)row[5u]<<8)|
                         ((uint32_t)row[6u]<<16)|((uint32_t)row[7u]<<24);
    if(record!=0 && destination!=0u) {
        if(record[0x86u]!=0u) { audio_ble_service_discovery_followup_5336e0(connection);return; }
        (void)audio_queue_copy_bytes((void *)(uintptr_t)destination,record+0x98u,(uint32_t)row[10u]<<1u);
    }
    audio_ble_service_discovery_step_531bd4(connection,stage);
}
