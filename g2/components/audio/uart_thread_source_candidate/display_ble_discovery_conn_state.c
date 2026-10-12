/* Native Cordio AppConnBonded query 0x4bad26 and DmConnSetIdle 0x4b71dc. */
#include <stdint.h>
extern uint8_t audio_ble_discovery_connection_records_200717b0[];
extern uint8_t audio_ble_dm_conn_rows_200712a4[];
extern uint8_t audio_ble_connection_record_active(uint8_t); /* selected DmConnInUse */
extern volatile uint8_t audio_ble_trace_level_cell;
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);

static void app_invalid_conn(void) {
    static const char warn[]="WARN",error[]="ERR",info[]="INFO",hci[]="HCI",app[]="APP";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_main.c";
    static const char name[]="AppCheckBonded",message[]="Invalid connId in AppConnBonded: %d";
    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(warn,error,3)!=0){
        if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(warn,warn,4)!=0){
            if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(warn,info,4)!=0){
                if(audio_ble_trace_level_cell==0){
                    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(app,hci,3)!=0)
                        audio_ble_wsf_trace(warn,message,0);
                }else if((audio_log_flags()&2u)!=0u)
                    audio_log_extended(4,app,source,name,0xb5u,message,0);
            }else if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3,app,source,name,0xb5u,message,0);
        }else if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2,app,source,name,0xb5u,message,0);
    }else if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1,app,source,name,0xb5u,message,0);
}

uint8_t audio_ble_connection_is_active_4bad26(uint8_t connection) {
    if(connection==0){app_invalid_conn();return 0;}
    return audio_ble_discovery_connection_records_200717b0[((uint32_t)connection-1u)*0x30u+5u];
}

static uint16_t idle_mask(uint8_t connection) {
    uint8_t *p=audio_ble_dm_conn_rows_200712a4+((uint32_t)connection-1u)*0x30u+0x0eu;
    return (uint16_t)p[0]|((uint16_t)p[1]<<8);
}
static void set_idle_mask(uint8_t connection,uint16_t mask) {
    uint8_t *p=audio_ble_dm_conn_rows_200712a4+((uint32_t)connection-1u)*0x30u+0x0eu;
    p[0]=(uint8_t)mask;p[1]=(uint8_t)(mask>>8);
}
static void idle_trace(uint8_t connection,uint16_t mask) {
    static const char info[]="INFO",error[]="ERR",warn[]="WARN",dm[]="DM",hci[]="HCI";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\dm\\dm_conn.c";
    static const char name[]="DmConnSetIdle",message[]="connId=%d idleMask=0x%04x";
    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(info,error,3)!=0){
        if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(info,warn,4)!=0){
            if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(info,info,4)!=0){
                if(audio_ble_trace_level_cell==0){
                    if(audio_ble_trace_level_cell==0 || audio_ble_hci_vendor_compare_44b610(dm,hci,3)!=0)
                        audio_ble_wsf_trace(info,message,connection,mask);
                }else if((audio_log_flags()&2u)!=0u)
                    audio_log_extended(4,dm,source,name,0x6ddu,message,connection,mask);
            }else if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3,dm,source,name,0x6ddu,message,connection,mask);
        }else if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2,dm,source,name,0x6ddu,message,connection,mask);
    }else if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1,dm,source,name,0x6ddu,message,connection,mask);
}

void audio_ble_dm_conn_set_idle(uint8_t connection,uint8_t bits,uint8_t value) {
    WsfTaskLock();
    if(audio_ble_connection_record_active(connection)!=0){
        uint16_t mask=idle_mask(connection);
        mask=value==0u?(uint16_t)(mask & (uint16_t)~bits):(uint16_t)(mask | bits);
        set_idle_mask(connection,mask);
    }
    WsfTaskUnlock();
    idle_trace(connection,idle_mask(connection));
}
