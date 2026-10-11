/* Native BLE communication dispatcher _bleCommHandler, 0x4b7d32.
 * Product profile/runtime tables and downstream protocol handlers stay imports. */
#include <stdint.h>

extern uint32_t audio_log_level(void);                /* 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...); /* 0x43ce9e */
extern uint8_t audio_dm_conn_role(uint8_t);          /* 0x4b73c4 */
extern uint32_t audio_ble_connection_get(void);      /* 0x46ef60 */
extern void audio_ble_comm_dm_dispatch_a(void *);    /* 0x532924 */
extern void audio_ble_comm_dm_dispatch_b(void *);    /* 0x53484c */
extern void audio_ble_comm_master_dispatch_a(void *);/* 0x503b92 */
extern void audio_ble_comm_master_dispatch_b(void *);/* 0x503c32 */
extern void audio_ble_comm_slave_dispatch(void *);   /* 0x4b3ca4 */
extern void audio_ble_comm_slave_finish(void *);     /* 0x4b45b0 */
extern void audio_ble_comm_message_release(void *);  /* 0x4b75ce */
extern uint32_t audio_ble_comm_forward_a(uint8_t,void *,uint32_t,uint32_t);/* 0x46ef74 */
extern uint32_t audio_ble_comm_forward_b(uint8_t,void *,uint32_t,uint32_t);/* 0x4a19c0 */

static const char module[]="ble.comm";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble.c";
static const char function[]="_bleCommHandler";
static const char dm_message[]="DM messages ble connId %d, role %d";
static const char dm_message_short[]="[ble.comm]DM messages ble connId %d, role %d";
static const char block_message[]="[Ring Connection] Blocking AppSlaveProcDmMsg for DM_ADV_STOP_IND to prevent auto restart";
static const char block_message_short[]="[ble.comm][Ring Connection] Blocking AppSlaveProcDmMsg for DM_ADV_STOP_IND to prevent auto restart";

void audio_ble_handler_4b7d32(uint8_t handler,void *message) {
    if(!message)return;
    const uint8_t *bytes=(const uint8_t *)message;
    uint8_t event=bytes[2];
    if((uint32_t)(event-2u)<0x17u) {
        audio_ble_comm_dm_dispatch_a(message);
        audio_ble_comm_dm_dispatch_b(message);
    } else if((uint32_t)(event-0x20u)<0x5cu) {
        uint16_t connection=(uint16_t)bytes[0]|(uint16_t)((uint16_t)bytes[1]<<8);
        if(audio_log_level()&2u)
            audio_log_extended(4u,module,source,function,0x28bu,dm_message,
                               (uint32_t)connection,(uint32_t)audio_dm_conn_role((uint8_t)connection));
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x10800000u,dm_message_short,dm_message_short,
                                        (uint32_t)connection,(uint32_t)audio_dm_conn_role((uint8_t)connection));
        if(connection==0u || audio_dm_conn_role((uint8_t)connection)==0u) {
            audio_ble_comm_master_dispatch_a(message);
            audio_ble_comm_master_dispatch_b(message);
        }
        if(connection==0u || audio_dm_conn_role((uint8_t)connection)==1u) {
            if(audio_ble_connection_get()==0u || event!=0x22u) {
                audio_ble_comm_slave_dispatch(message);
            } else {
                if(audio_log_level()&2u)
                    audio_log_extended(3u,module,source,function,0x29au,block_message);
                if((audio_log_level()&1u)||(audio_log_level()&4u))
                    (void)compressed_log_output(0x0c000000u,block_message_short,block_message_short);
            }
            audio_ble_comm_slave_finish(message);
        }
    }
    audio_ble_comm_message_release(message);
    (void)audio_ble_comm_forward_a(handler,message,0u,0u);
    (void)audio_ble_comm_forward_b(handler,message,0u,0u);
}
