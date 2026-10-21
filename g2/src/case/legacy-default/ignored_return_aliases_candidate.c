/* SPDX-License-Identifier: MIT
 * Exact-address selected providers whose R0 is ignored at these call sites.
 * The signatures therefore use the selected void ABI. UART output remains
 * a physical transport contract.
 */
#include <stdint.h>
extern void case_ack(uint32_t opcode);                      /* 0x080068d0 */
extern void case_send(const uint8_t *payload,uint32_t n);  /* 0x0800680c */
extern void log_hex_buffer(const uint8_t *bytes,uint32_t n); /* 0x080067c8 */

void case_binary_ack0641(uint32_t opcode){case_ack(opcode);}
void case_binary_5e_ack(uint32_t opcode){case_ack(opcode);}
void case_binary_5e_send(const uint8_t *payload,uint32_t n){case_send(payload,n);}
void case_legacy_hex_log(const uint8_t *bytes,uint32_t n){log_hex_buffer(bytes,n);}
