/* Native Cordio dmConnCcbByHandle 0x4b601c, three 0x30-byte CCBs. */
#include <stdint.h>
extern uint8_t audio_dm_connection_records[]; /* native 0x200712a4 */
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *,const char *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_hci_wsf_trace(const char *,const char *,...);
static const char warn[]="WARN",err[]="ERR",info[]="INFO",module[]="DM",hci[]="HCI";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\dm\\dm_conn.c";
static const char function[]="dmConnCcbByHandle";
static const char message[]="dmConnCcbByHandle not found 0x%04x";
static void missing(uint16_t handle){
    uint8_t level;
    if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,err,3u)==0)level=1u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,warn,4u)==0)level=2u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,info,4u)==0)level=3u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u)level=4u;
    else{
        if(audio_ble_hci_vendor_log_enabled_4c9c50()==0u||audio_l2c_strncmp(module,hci,3u)!=0)
            audio_ble_hci_wsf_trace(warn,message,handle);
        return;
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(level,module,source,function,0xefu,message,handle);
}
uint8_t *audio_ble_dm_conn_ccb_by_handle_4b601c(uint16_t handle){
    uint8_t *record=audio_dm_connection_records;
    for(uint32_t i=0;i<3u;i++,record+=0x30u){
        uint16_t candidate=(uint16_t)((uint32_t)record[0x0cu]|((uint32_t)record[0x0du]<<8));
        if(record[0x16u]!=0u&&candidate==handle)return record;
    }
    missing(handle);return 0;
}
