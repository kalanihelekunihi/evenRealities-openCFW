/* Cordio native default data callbacks 0x530538 and 0x530640. The odd
 * repeated log-enabled reads and category comparisons are retained: the
 * live enable byte can change between calls. */
#include <stdint.h>
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void); /* native 0x4c9c50 */
extern int32_t audio_l2c_strncmp(const char*,const char*,uint32_t); /* 0x44b610 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t,const char*,const char*,const char*,uint32_t,const char*,...);
extern void audio_ble_hci_wsf_trace(const char*,const char*,...); /* native 0x52a63c */
static const char warn[]="WARN",err[]="ERR",info[]="INFO",module[]="L2C",hci[]="HCI";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\l2c\\l2c_main.c";
static const char data_fn[]="l2cDefaultDataCback",cid_fn[]="l2cDefaultDataCidCback";
static const char data_msg[]="rcvd data on uregistered cid";
static const char cid_msg[]="unknown cid=0x%04x";
static void log_default(uint32_t cid,uint32_t is_cid,uint8_t level) {
    if(audio_log_flags()&2u) {
        if(is_cid) audio_log_extended(level,module,source,cid_fn,0x4bu,cid_msg,cid&0xffffu);
        else audio_log_extended(level,module,source,data_fn,0x3au,data_msg);
    }
}
static void default_callback(uint32_t cid,uint32_t is_cid) {
    if(audio_ble_hci_vendor_log_enabled_4c9c50()==0u||audio_l2c_strncmp(warn,err,3u)!=0) {
        if(audio_ble_hci_vendor_log_enabled_4c9c50()==0u||audio_l2c_strncmp(warn,warn,4u)!=0) {
            if(audio_ble_hci_vendor_log_enabled_4c9c50()==0u||audio_l2c_strncmp(warn,info,4u)!=0) {
                if(audio_ble_hci_vendor_log_enabled_4c9c50()==0u) {
                    if(audio_ble_hci_vendor_log_enabled_4c9c50()==0u||audio_l2c_strncmp(module,hci,3u)!=0) {
                        if(is_cid) audio_ble_hci_wsf_trace(warn,cid_msg,cid&0xffffu);
                        else audio_ble_hci_wsf_trace(warn,data_msg);
                    }
                } else log_default(cid,is_cid,4u);
            } else log_default(cid,is_cid,3u);
        } else log_default(cid,is_cid,2u);
    } else log_default(cid,is_cid,1u);
}
void audio_ble_l2c_default_data_530538(void) {default_callback(0u,0u);}
void audio_ble_l2c_default_cid_530640(uint32_t ignored,uint32_t cid,
                                       uint32_t unused2,uint32_t unused3) {
    (void)ignored;(void)unused2;(void)unused3;
    default_callback(cid,1u);
}
