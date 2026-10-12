/* Native Cordio l2cHciAclCback at 0x5308e6. The HCI buffer is owned by this
 * callback and is freed on every return path. The table is installed by L2cInit. */
#include <stdint.h>

extern uint8_t audio_ble_l2c_state[0x30u];
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *, const char *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_hci_wsf_trace(const char *,const char *,...);
extern void WsfMsgFree(void *);

typedef void (*l2c_data_cb)(uint32_t,uint32_t,uint8_t *);
typedef void (*l2c_cid_cb)(uint32_t,uint32_t,uint32_t,uint8_t *);
static const char warn[]="WARN",err[]="ERR",info[]="INFO",module[]="L2C",hci[]="HCI";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\l2c\\l2c_main.c";
static const char function[]="l2cHciAclCback";
static const char mismatch[]="length mismatch: l2c=%u hci=%u";
static uint16_t rd16(const uint8_t *p) {return (uint16_t)((uint32_t)p[0]|((uint32_t)p[1]<<8));}
static void l2c_length_error(uint32_t payload,uint32_t hci_length) {
    uint8_t level;
    if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,err,3u)==0) level=1u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,warn,4u)==0) level=2u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,info,4u)==0) level=3u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u) level=4u;
    else {
        if(audio_ble_hci_vendor_log_enabled_4c9c50()==0u||audio_l2c_strncmp(module,hci,3u)!=0)
            audio_ble_hci_wsf_trace(warn,mismatch,payload&0xffffu,hci_length&0xffffu);
        return;
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(level,module,source,function,0xc0u,mismatch,payload&0xffffu,hci_length&0xffffu);
}
void audio_ble_l2c_hci_acl_5308e6(uint8_t *packet) {
    uint32_t handle=rd16(packet)&0xfffu;
    uint32_t hci_length=rd16(packet+2);
    uint32_t payload=hci_length<4u?0u:rd16(packet+4);
    const uint8_t *cid_at=packet+(hci_length<4u?4u:6u);
    if(hci_length==((payload+4u)&0xffffu)) {
        uint32_t cid=rd16(cid_at);
        if(cid==4u) ((l2c_data_cb)*(void **)(void *)(audio_ble_l2c_state+0u))(handle,payload,packet);
        else if(cid==6u) ((l2c_data_cb)*(void **)(void *)(audio_ble_l2c_state+4u))(handle,payload,packet);
        else if(cid==5u) ((l2c_data_cb)*(void **)(void *)(audio_ble_l2c_state+8u))(handle,payload,packet);
        else ((l2c_cid_cb)*(void **)(void *)(audio_ble_l2c_state+32u))(handle,cid,payload,packet);
    } else l2c_length_error(payload,hci_length);
    WsfMsgFree(packet);
}
