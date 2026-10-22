/* Native smpSendPkt 0x537a5a and L2cDataReq 0x530bbc.
 * 0x537ba4..b2 explicitly sets all four ARM argument registers before BL:
 * R0=6, R1=CCB handle, R2=authenticated size[packet[8]], R3=packet.
 * The decompiler's fifth-through-seventh arguments are ambient registers,
 * unused by the native four-register L2cDataReq body. */
#include <stdint.h>
extern void HciSendAclData(void *);
extern void audio_ble_wsf_message_free(void *);
extern volatile uint8_t audio_ble_trace_level_cell;
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t); /* 0x44b610 bounded strncmp */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
void L2cDataReq(uint16_t cid,uint16_t handle,uint16_t length,uint8_t *packet){
    packet[0]=(uint8_t)handle;packet[1]=(uint8_t)(handle>>8);
    packet[2]=(uint8_t)(length+4u);packet[3]=(uint8_t)((length+4u)>>8);
    packet[4]=(uint8_t)length;packet[5]=(uint8_t)(length>>8);
    packet[6]=(uint8_t)cid;packet[7]=(uint8_t)(cid>>8);
    HciSendAclData(packet);
}
