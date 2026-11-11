#ifndef R1_NATIVE_ACK_REGISTRY_H
#define R1_NATIVE_ACK_REGISTRY_H
#include <stdint.h>
extern volatile uint8_t r1_protocol_reset_workspace[640];
uint32_t r1_ack_record_insert(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t r1_ack_record_register(const volatile uint8_t *,uint32_t,volatile uint8_t *,volatile uint16_t *);
uint32_t r1_ack_record_remove(uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t r1_ack_timeout_reaper(void);
uint32_t r1_ack_table_clear(void);
#endif
