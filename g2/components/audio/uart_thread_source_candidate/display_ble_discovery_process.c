/* Native Cordio AppDiscProcAttMsg 0x532924. Runtime rows/callback remain external. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_rows_200733fc[];
extern uint8_t audio_ble_discovery_connection_records_200717b0[];
extern uintptr_t audio_ble_service_dispatch_20074348;
extern void audio_ble_service_discovery_restart_531f20(uint8_t);
extern void audio_ble_service_discovery_start(uint8_t);
extern void audio_ble_service_discovery_step_531bd4(uint8_t,uint8_t);
extern uint8_t *audio_ble_pair_record(uint8_t);
extern uint8_t *audio_ble_pair_record_create_47a71c(uint8_t,const uint8_t *,uint8_t);
extern void audio_ble_pair_record_update_name_47b3ae(uint8_t *,const uint8_t *);
extern void audio_ble_pair_record_clear_b(uint8_t *,uint8_t);
extern uint8_t audio_dm_conn_role(uint8_t);
extern const uint8_t *DmConnPeerAddr(uint8_t);
extern uint8_t DmConnPeerAddrType(uint8_t);
extern uint8_t audio_ble_dm_sec_level_4b71b2(uint8_t);
extern void audio_ble_dm_conn_set_idle(uint8_t,uint8_t,uint8_t);
extern uint8_t audio_ble_discovery_service_complete_56bf32(uint8_t *,const uint8_t *);
extern void audio_ble_discovery_char_start_56c1b8(uint8_t,uint8_t *);
extern uint8_t audio_ble_discovery_char_complete_56c1f8(uint8_t *,const uint8_t *);
extern uint8_t audio_ble_discovery_config_complete_56c396(uint8_t,uint8_t *);
extern void audio_ble_discovery_print_characteristics_5322f6(uint8_t *,const uint8_t *);
extern void audio_ble_discovery_print_descriptors_532644(uint8_t *,const uint8_t *);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern int32_t g2_lfs_memcmp(const void *,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern volatile uint8_t audio_ble_trace_level_cell;
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern void audio_ble_wsf_trace(const char *,const char *,...);
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static void wr32(uint8_t *p,uint32_t x){p[0]=(uint8_t)x;p[1]=(uint8_t)(x>>8);p[2]=(uint8_t)(x>>16);p[3]=(uint8_t)(x>>24);}
static void dispatch(uint8_t connection,uint8_t status){
    ((void (*)(uint8_t,uint8_t))audio_ble_service_dispatch_20074348)(connection,status);
}
static const char module[]="app.disc";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_disc.c";
static const char function_name[]="AppDiscProcAttMsg";
#define STATUS_LOG(line,mask,plain,short_text,value) do { \
    if((audio_log_flags()&2u)!=0u) audio_log_extended(4,module,source,function_name,line,plain,value); \
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u) \
        (void)compressed_log_output(mask,short_text,short_text,value); \
}while(0)
static void invalid_open(void){
    static const char warn[]="WARN",error[]="ERR",info[]="INFO",app[]="APP",hci[]="HCI";
    static const char message[]="Invalid connId in appDiscConnOpen: %d";
    uint8_t level=4;
    if(audio_ble_trace_level_cell!=0u){
        if(audio_ble_hci_vendor_compare_44b610(warn,error,3u)==0)level=1;
        else if(audio_ble_hci_vendor_compare_44b610(warn,warn,4u)==0)level=2;
        else if(audio_ble_hci_vendor_compare_44b610(warn,info,4u)==0)level=3;
    }
    if(audio_ble_trace_level_cell==0u){
        if(audio_ble_hci_vendor_compare_44b610(app,hci,3u)!=0)
            audio_ble_wsf_trace(warn,message,0u);
    }else if((audio_log_flags()&2u)!=0u)
        audio_log_extended(level,app,source,function_name,0x29eu,message,0u);
}
void audio_ble_discovery_process_532924(const uint8_t *message){
    const uint8_t connection=message[0];
    uint8_t *row=audio_ble_subsystem_rows_200733fc+((uint32_t)connection-1u)*16u;
    if(message[3]==0x12u)audio_ble_service_discovery_restart_531f20(connection);
    if(row[11]==3u){
        if(message[2]!=4u)return;
        if(message[3]!=0u){dispatch(connection,3u);return;}
        row[11]=0u;
        uint8_t *record=audio_ble_pair_record(connection);
        if(record==0){
            if(connection==0u){invalid_open();return;}
            const uint8_t role=audio_dm_conn_role(connection);
            record=audio_ble_pair_record_create_47a71c(DmConnPeerAddrType(connection),
                                                        DmConnPeerAddr(connection),role==0u);
            wr32(audio_ble_discovery_connection_records_200717b0+
                 ((uint32_t)connection-1u)*0x30u,(uint32_t)(uintptr_t)record);
        }
        const uint8_t *payload=(const uint8_t *)(uintptr_t)rd32(message+4);
        if(g2_lfs_memcmp(record+0x87u,payload+3u,16u)==0){
            (void)audio_queue_copy_bytes((void *)(uintptr_t)rd32(row+4),record+0x98u,
                                          (uint32_t)row[10]*2u);
            audio_ble_service_discovery_step_531bd4(connection,record[0xc2u]);
        }else{
            audio_ble_pair_record_update_name_47b3ae(record,payload+3u);
            audio_ble_pair_record_clear_b(record,1u);
            dispatch(connection,3u);
        }
        return;
    }
    uint8_t *context=(uint8_t *)(uintptr_t)rd32(row);
    if(row[11]==1u){
        if(message[2]==3u){
            const uint8_t status=audio_ble_discovery_service_complete_56bf32(context,message);
            STATUS_LOG(0x2d1u,0x10400000u,"AttcDiscServiceCmpl status 0x%02x",
                       "[app.disc]AttcDiscServiceCmpl status 0x%02x",status);
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(4,module,source,function_name,0x2d2u,
                    "appDiscPrint found service startHdl=0x%04X endHdl=0x%04X",
                    rd16(context+0x0e),rd16(context+0x10));
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u){
                static const char short_text[]="[app.disc]appDiscPrint found service startHdl=0x%04X endHdl=0x%04X";
                (void)compressed_log_output(0x10800000u,short_text,short_text,rd16(context+0x0e),rd16(context+0x10));
            }
            if(status==0u)audio_ble_discovery_char_start_56c1b8(connection,context);
            else if(status!=0x79u){audio_ble_dm_conn_set_idle(connection,8u,0u);dispatch(connection,5u);}
        }else if(message[2]==4u || message[2]==2u){
            const uint8_t status=audio_ble_discovery_char_complete_56c1f8(context,message);
            STATUS_LOG(0x2eau,0x10400000u,"AttcDiscCharCmpl status 0x%02x",
                       "[app.disc]AttcDiscCharCmpl status 0x%02x",status);
            if(message[2]==4u){if(rd16(message+8)>7u)audio_ble_discovery_print_characteristics_5322f6(context,message);}
            else if(rd16(message+8)>4u)audio_ble_discovery_print_descriptors_532644(context,message);
            if(status==0u)dispatch(connection,4u);
            else if(status!=0x79u){audio_ble_dm_conn_set_idle(connection,8u,0u);dispatch(connection,5u);}
        }
        return;
    }
    if(row[11]!=2u)return;
    if(message[2]==5u || message[2]==9u){
        if(row[14]!=0u){
            row[14]=0u;row[11]=0u;audio_ble_service_discovery_start(connection);return;
        }
        if((message[3]==5u || message[3]==0x0fu) && audio_ble_dm_sec_level_4b71b2(connection)==0u){
            row[13]=1u;dispatch(connection,2u);return;
        }
        const uint8_t status=audio_ble_discovery_config_complete_56c396(connection,context);
        STATUS_LOG(0x322u,0x10400000u,"AttcDiscConfigCmpl status 0x%02x",
                   "[app.disc]AttcDiscConfigCmpl status 0x%02x",status);
        if(status!=0x79u)dispatch(connection,8u);
    }else if(message[3]!=0u && message[3]!=0x79u){
        STATUS_LOG(0x330u,0x08400000u,"Configuration failed with status 0x%02x, clearing idle state",
                   "[app.disc]Configuration failed with status 0x%02x, clearing idle state",message[3]);
        audio_ble_dm_conn_set_idle(connection,8u,0u);row[11]=0u;dispatch(connection,5u);
    }
}
