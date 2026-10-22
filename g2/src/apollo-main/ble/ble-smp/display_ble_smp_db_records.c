/* Native Cordio SMP database record search/add/in-use 0x541fb8,
 * 0x541e72, 0x541e50 and six-byte address equality/copy children. */
#include <stdint.h>
extern uint8_t audio_ble_smp_database[]; /* selected 0x200708ec */
extern volatile uint8_t audio_ble_trace_level_cell; /* live 0x2007502f */
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t); /* 0x44b610 bounded strncmp */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
extern uint8_t DmConnPeerAddrType(uint8_t); /* native 0x4b6ed8 */
extern uint8_t DmHostAddrType(uint8_t); /* selected 0x4d2aa8 */
extern const uint8_t *DmConnPeerAddr(uint8_t); /* native 0x4b6eea */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern int32_t g2_lfs_memcmp(const void *,const void *,uint32_t); /* selected 0x4751c8 */

static const char info[]="INFO",err[]="ERR",warn[]="WARN",smp[]="SMP",hci[]="HCI";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\smp\\smp_db.c";
static const char get_name[]="smpDbGetRecord",add_name[]="smpDbAddDevice";
static const char get_msg[]="smpDbGetRecord: connId: %d type: %d";
static const char common_msg[]="smpDbGetRecord: common record";
static const char add_msg[]="smpDbAddDevice";
static uint32_t cmp(const char *a,const char *b,uint32_t n) {
    return (uint32_t)audio_ble_hci_vendor_compare_44b610(a,b,n);
}
void audio_ble_smp_db_diagnostic(const char *name,uint32_t line,const char *message,
                                 uint8_t arity,uint32_t first,uint32_t second) {
    uint8_t level=0u;
    if(audio_ble_trace_level_cell!=0u && cmp(info,err,3u)==0u)level=1u;
    else if(audio_ble_trace_level_cell!=0u && cmp(info,warn,4u)==0u)level=2u;
    else if(audio_ble_trace_level_cell!=0u && cmp(info,info,4u)==0u)level=3u;
    else if(audio_ble_trace_level_cell!=0u)level=4u;
    if(level!=0u) {
        if(audio_log_flags()&2u) {
            if(arity==2u)audio_log_extended(level,smp,path,name,line,message,first,second);
            else if(arity==1u)audio_log_extended(level,smp,path,name,line,message,first);
            else audio_log_extended(level,smp,path,name,line,message);
        }
    } else if(audio_ble_trace_level_cell==0u || cmp(smp,hci,3u)!=0u) {
        if(arity==2u)audio_ble_wsf_trace(info,message,first,second);
        else if(arity==1u)audio_ble_wsf_trace(info,message,first);
        else audio_ble_wsf_trace(info,message);
    }
}

uint32_t smpDbRecordInUse(const uint8_t *record) {
    if(record[7u]!=0u)return 1u;
    uint32_t word;
    __builtin_memcpy(&word,record+0x0cu,4u);
    if(word!=0u)return 1u;
    uint16_t half;
    __builtin_memcpy(&half,record+8u,2u);
    return half!=0u;
}
uint32_t audio_ble_smp_address_equal(const uint8_t *record,const uint8_t *address) {
    return g2_lfs_memcmp(record,address,6u)==0;
}
void audio_ble_smp_address_copy(uint8_t *record,const uint8_t *address) {
    __builtin_memcpy(record,address,6u);
}
uint8_t *smpDbAddDevice(const uint8_t *address,uint8_t type) {
    audio_ble_smp_db_diagnostic(add_name,0x85u,add_msg,0u,0u,0u);
    for(uint32_t i=0u;i<9u;i++) {
        uint8_t *record=audio_ble_smp_database+0x18u+i*0x18u;
        if(smpDbRecordInUse(record)==0u) {
            audio_uart_buffer_zero(record,0x18u,0u);
            record[6u]=type;
            audio_ble_smp_address_copy(record,address);
            return record;
        }
    }
    return 0;
}
uint8_t *smpDbGetRecord(uint8_t conn) {
    uint8_t type=DmHostAddrType(DmConnPeerAddrType(conn));
    const uint8_t *address=DmConnPeerAddr(conn);
    audio_ble_smp_db_diagnostic(get_name,0xa7u,get_msg,2u,conn,type);
    for(uint32_t i=0u;i<9u;i++) {
        uint8_t *record=audio_ble_smp_database+0x18u+i*0x18u;
        if(smpDbRecordInUse(record)!=0u && record[6u]==type &&
           audio_ble_smp_address_equal(record,address)!=0u)return record;
    }
    uint8_t *record=smpDbAddDevice(address,type);
    if(!record) {
        audio_ble_smp_db_diagnostic(get_name,0xb6u,common_msg,0u,0u,0u);
        return audio_ble_smp_database;
    }
    return record;
}
