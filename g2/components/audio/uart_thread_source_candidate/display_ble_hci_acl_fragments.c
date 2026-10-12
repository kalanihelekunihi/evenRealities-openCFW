/* Native hciCoreTxAclStart/Continue/Complete 0x52a850/0x52a8b0/0x52a936.
 * Connection records and packet ownership are live WSF state, not source data. */
#include <stdint.h>

extern uint16_t audio_ble_hci_get_buf_size(void); /* HciGetBufSize 0x530d34 */
extern uint32_t audio_ble_hci_send_acl_data(void *,void *); /* 0x52a76c */
extern uint8_t *audio_ble_hci_next_conn_fragment(void); /* 0x52a72e */
extern void audio_ble_wsf_message_free(void *); /* selected WsfMsgFree */

static uint16_t get16(const uint8_t *p) {uint16_t x;__builtin_memcpy(&x,p,2);return x;}
static void put16(uint8_t *p,uint16_t x) {__builtin_memcpy(p,&x,2);}
static uint8_t *getptr(const uint8_t *p) {uint32_t x;__builtin_memcpy(&x,p,4);return (uint8_t *)(uintptr_t)x;}
static void putptr(uint8_t *p,const void *v) {uint32_t x=(uint32_t)(uintptr_t)v;__builtin_memcpy(p,&x,4);}

uint32_t audio_ble_hci_tx_acl_start(void *record,uint16_t length,void *packet) {
    uint8_t *conn=(uint8_t *)record;
    uint8_t *data=(uint8_t *)packet;
    uint16_t limit=audio_ble_hci_get_buf_size();
    if(limit<length) {
        put16(conn+0x12u,(uint16_t)(length-limit));
        putptr(conn+4u,data+limit);
        putptr(conn,data);
        conn[0x16u]=1u;
        put16(data+2u,limit);
        if(audio_ble_hci_send_acl_data(conn,data)==1u)return 1u;
        putptr(conn,0);
        conn[0x16u]=0u;
        put16(data+2u,length);
        return 0u;
    }
    return audio_ble_hci_send_acl_data(conn,data);
}

void audio_ble_hci_tx_acl_complete(void *record,void *packet) {
    uint8_t *conn=(uint8_t *)record;
    if(conn[0x16u]==0u) {
        if(packet!=0)audio_ble_wsf_message_free(packet);
    } else if(get16(conn+0x12u)==0u) {
        audio_ble_wsf_message_free(getptr(conn));
        putptr(conn,0);
        conn[0x16u]=0u;
    }
}

uint32_t audio_ble_hci_tx_acl_continue(void *record) {
    uint8_t *conn=(uint8_t *)record;
    if(conn==0)conn=audio_ble_hci_next_conn_fragment();
    if(conn==0)return 0u;
    uint16_t remaining=get16(conn+0x12u);
    uint16_t limit=audio_ble_hci_get_buf_size();
    uint16_t count=remaining<limit?remaining:audio_ble_hci_get_buf_size();
    if(count==0u)return 0u;
    uint8_t *packet=getptr(conn+4u);
    packet[0u]=conn[0x10u];
    packet[1u]=(uint8_t)(conn[0x11u]|0x10u);
    put16(packet+2u,count);
    if(audio_ble_hci_send_acl_data(conn,packet)!=1u)return 0u;
    remaining=(uint16_t)(remaining-count);
    put16(conn+0x12u,remaining);
    if(remaining!=0u)putptr(conn+4u,packet+count);
    audio_ble_hci_tx_acl_complete(conn,getptr(conn+4u));
    return 1u;
}
