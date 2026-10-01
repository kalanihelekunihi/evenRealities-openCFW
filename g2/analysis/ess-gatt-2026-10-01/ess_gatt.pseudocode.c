/* Manual behavioral reconstruction, not decompiler output or firmware source.
 * Pointers below describe the 32-bit image. External side effects are abstract.
 */
#include <stdint.h>
extern void att_event(uint8_t conn, unsigned event);
extern void add_group(uint32_t address);
extern void send_mtu_response(uint16_t local_mtu);
extern void att_error_request_not_supported(void);

/* 0x5361f6 stores read=0, write=essWriteCallback|1 into group+8/+12.
 * 0x5361ec calls AttsAddGroup(0x20003b38).
 * Group contains attrTable=0x6de9d4, start=0x0860, end=0x0865.
 */
void recovered_ess_register(void) { add_group(0x20003b38); }

/* 0x4b503c. bearer u8 selects core+4*bearer; conn byte at core+14.
 * Callback fires only when value changes. Return register is incidental.
 */
void recovered_att_set_mtu(uint16_t *slot, uint8_t conn,
                           uint16_t peer, uint16_t local) {
    uint16_t selected=peer<local?peer:local;
    if (*slot!=selected) { *slot=selected; att_event(conn,0x16); }
}
/* 0x56c6fc, normal feature branch. Logging omitted. Request bytes9/10
 * are LE peer MTU after an eight-byte internal prefix and opcode.
 * Firmware raises peer MTU to 247. This models the observed instructions,
 * not a recommended negotiation algorithm. Failed response allocation still
 * reaches attSetMtu in the original routine.
 */
void recovered_mtu_request(uint16_t *slot, uint8_t conn, uint8_t features,
                            uint16_t peer, uint16_t configured,
                            uint16_t acl_rx_max, int allocation_succeeds) {
    if (features & 2) { att_error_request_not_supported(); return; }
    if (peer<247) peer=247;
    uint16_t local=configured<(int)acl_rx_max-4 ? configured : acl_rx_max-4;
    if (allocation_succeeds) send_mtu_response(local);
    recovered_att_set_mtu(slot,conn,peer,local);
}
/* 0x4b5204 AttGetMtu(conn) returns core[0] without payload adjustment.
 * 0x533c6c notification gate reads *(u16*)(*(server+16)+4*bearer).
 * Compare at0x533cec/0x533cee is stored_mtu >= (u16)value_length+3.
 * Existing original-instruction tests establish 205+3=208, reject207.
 */
int recovered_notification_size_gate(uint16_t stored_mtu, uint16_t value_length) {
    return stored_mtu >= (unsigned)value_length+3;
}
