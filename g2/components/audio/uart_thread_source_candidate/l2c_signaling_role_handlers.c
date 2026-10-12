/* Native Cordio master/slave signaling callbacks 0x536fbc and 0x536c5c.
 * Connection state is live RAM at 0x20073bd8; no product initializer is
 * inferred here. */
#include <stdint.h>
extern uint8_t audio_ble_l2c_slave_state[];
extern uint8_t DmConnIdByHandle(uint16_t);
extern void WsfTimerStop(void *);
extern void audio_ble_hci_wsf_trace(const char *,const char *,...);
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *,const char *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_l2c_send_cmd_reject_530ae0(uint16_t,uint8_t,uint16_t);
extern void audio_ble_l2c_dm_conn_update_rsp_537230(uint8_t,uint16_t,uint8_t);
extern void audio_ble_dm_l2c_conn_update_ind_55bc96(uint8_t,uint16_t,const uint16_t *);
extern void audio_ble_dm_l2c_conn_update_cnf_56e580(uint16_t,uint16_t);
extern void audio_ble_dm_l2c_cmd_rej_ind_56e5a4(uint16_t,uint16_t);

static const char err[]="ERR",warn[]="WARN",info[]="INFO",module[]="L2C",hci[]="HCI";
static const char message[]="invalid msg code:%d len:%d l2cLen:%d";
static const char master_fn[]="l2cMasterRxSignalingPkt",slave_fn[]="l2cSlaveRxSignalingPkt";
static const char master_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\l2c\\l2c_master.c";
static const char slave_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\l2c\\l2c_slave.c";
static uint16_t rd16(const uint8_t *p){return (uint16_t)((uint32_t)p[0]|((uint32_t)p[1]<<8));}
static void invalid(uint8_t master,uint8_t code,uint16_t cmd_len,uint16_t l2c_len){
    uint8_t level;
    if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,err,3u)==0)level=1u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,warn,4u)==0)level=2u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(warn,info,4u)==0)level=3u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u)level=4u;
    else{
        if(audio_ble_hci_vendor_log_enabled_4c9c50()==0u||audio_l2c_strncmp(module,hci,3u)!=0)
            audio_ble_hci_wsf_trace(warn,message,code,cmd_len,l2c_len);
        return;
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(level,module,master?master_source:slave_source,
                           master?master_fn:slave_fn,master?0x46u:0x9eu,
                           message,code,cmd_len,l2c_len);
}
void audio_ble_l2c_master_rx_536fbc(uint16_t handle,uint16_t l2c_len,uint8_t *packet){
    uint8_t code=packet[8],id=packet[9];
    uint16_t cmd_len=rd16(packet+10);
    if((uint32_t)l2c_len==(uint32_t)cmd_len+4u&&code==0x12u&&cmd_len==8u){
        uint16_t params[6]={rd16(packet+12),rd16(packet+14),rd16(packet+16),rd16(packet+18),0u,0u};
        if((uint32_t)params[0]-6u<0xc7bu&&params[0]<=params[1]&&
           (uint32_t)params[1]-6u<0xc7bu&&params[2]<500u&&
           (uint32_t)params[3]-10u<0xc77u)
            audio_ble_dm_l2c_conn_update_ind_55bc96(id,handle,params);
        else audio_ble_l2c_dm_conn_update_rsp_537230(id,handle,1u);
    }else{
        invalid(1u,code,cmd_len,l2c_len);
        if(code!=1u)audio_ble_l2c_send_cmd_reject_530ae0(handle,id,0u);
    }
}
void audio_ble_l2c_slave_rx_536c5c(uint16_t handle,uint16_t l2c_len,uint8_t *packet){
    uint8_t conn=DmConnIdByHandle(handle);
    if(conn==0u)return;
    uint8_t code=packet[8],id=packet[9];
    uint16_t cmd_len=rd16(packet+10);
    if(id==0u)return;
    uint8_t *record=audio_ble_l2c_slave_state+conn;
    if(id==record[0x13u]&&(uint32_t)l2c_len==(uint32_t)cmd_len+4u&&
       ((code==0x13u&&cmd_len==2u)||code==1u)){
        uint8_t prior=record[0x10u];
        record[0x13u]=0u;
        uint16_t result=rd16(packet+12);
        WsfTimerStop(audio_ble_l2c_slave_state);
        if(prior==0x12u){
            if(code==1u)result=1u;
            audio_ble_dm_l2c_conn_update_cnf_56e580(handle,result);
        }else audio_ble_dm_l2c_cmd_rej_ind_56e5a4(handle,result);
    }else{
        invalid(0u,code,cmd_len,l2c_len);
        if(code!=1u)audio_ble_l2c_send_cmd_reject_530ae0(handle,id,0u);
    }
}
