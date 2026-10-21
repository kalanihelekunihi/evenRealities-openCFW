/* Native Cordio attcCcbByConnId 0x531820.  Its connected result is a
 * 0x2c-byte slot in each 0x84-byte client connection record. */
#include <stdint.h>
extern volatile uint8_t audio_ble_trace_level_cell; /* selected RAM 0x2007502f */
extern uint8_t audio_ble_connection_record_active(uint8_t); /* selected 0x4b6ec6 */
extern uint8_t audio_ble_attc_state[]; /* selected AttcInit producer, RAM 0x2006f904 */
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
static void ccb_log(uint8_t level,uint32_t line,const char *message,uint8_t connection,uint8_t slot) {
    static const char module[]="ATT";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\attc_main.c";
    static const char name[]="attcCcbByConnId";
    if((audio_log_flags()&2u)!=0u) {
        if(line==0x2f9u)audio_log_extended(level,module,source,name,line,message,connection);
        else audio_log_extended(level,module,source,name,line,message,connection,slot);
    }
}
static void ccb_invalid_log(uint8_t connection,uint8_t slot,uint8_t inactive) {
    static const char warn[]="WARN",error[]="ERR",info[]="INFO",att[]="ATT",hci[]="HCI";
    static const char bad_id[]="Invalid connId in attcCcbByConnId: %d, slot: %d";
    static const char inactive_id[]="attc ccb not in use: %d";
    const char *message=inactive?inactive_id:bad_id;
    uint32_t line=inactive?0x2f9u:0x2f0u;
    if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(warn,error,3u)!=0) {
        if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(warn,warn,4u)!=0) {
            if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(warn,info,4u)!=0) {
                if(audio_ble_trace_level_cell==0u) {
                    if(audio_ble_trace_level_cell==0u || audio_ble_hci_vendor_compare_44b610(att,hci,3u)!=0) {
                        if(inactive)audio_ble_wsf_trace(warn,message,connection);
                        else audio_ble_wsf_trace(warn,message,0u,slot);
                    }
                } else ccb_log(4u,line,message,connection,slot);
            } else ccb_log(3u,line,message,connection,slot);
        } else ccb_log(2u,line,message,connection,slot);
    } else ccb_log(1u,line,message,connection,slot);
}
uint8_t *audio_ble_attc_ccb_by_conn_id_531820(uint8_t connection,uint8_t slot) {
    if(connection==0u) { ccb_invalid_log(connection,slot,0u);return (uint8_t *)0; }
    if(audio_ble_connection_record_active(connection)==0u) {
        ccb_invalid_log(connection,slot,1u);
        return (uint8_t *)0;
    }
    return audio_ble_attc_state+
           ((uint32_t)connection-1u)*0x84u+(uint32_t)slot*0x2cu;
}
