/* Native Cordio L2cSlaveHandler 0x536fa4 and l2cSlaveReqTimeout 0x536b40. */
#include <stdint.h>
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *,const char *,uint32_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
extern void audio_ble_dm_l2c_conn_update_cnf_56e580(uint16_t,uint16_t);
static const char warn[]="WARN",err[]="ERR",info[]="INFO",hci[]="HCI",module[]="L2C";
static const char message[]="conn update req timeout";
static const char function_name[]="l2cSlaveReqTimeout";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\l2c\\l2c_slave.c";

void audio_ble_l2c_slave_req_timeout_536b40(const uint8_t *event){
    uint8_t level=0u;
    if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,err,3u)==0)level=1u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,warn,4u)==0)level=2u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,info,4u)==0)level=3u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u)level=4u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()==0u||audio_l2c_strncmp(module,hci,3u)!=0)
        audio_ble_wsf_trace(warn,message);
    if(level!=0u&&(audio_log_level()&2u)!=0u)
        audio_log_extended(level,module,path,function_name,0x4au,message);
    audio_ble_dm_l2c_conn_update_cnf_56e580((uint16_t)event[0]|((uint16_t)event[1]<<8),1u);
}

/* Stock 0x536FA4 (L2cSlaveHandler). The stock epilogue popped the caller's
 * R7 into R0; it is installed as a WSF event handler, which returns void. */
void audio_ble_handler_536fa4(uint32_t event_mask,const uint8_t *message){
    (void)event_mask;
    if(message!=0&&message[2]==1u)
        audio_ble_l2c_slave_req_timeout_536b40(message);
}
