#include <stdint.h>
/* Authenticated connection field at base 0x200064b2 + 6. Ownership of adjacent
 * connection fields and connection transitions remains separately gated. */
volatile uint16_t r1_connection_field6
 __attribute__((section(".r1.connection.field6"),aligned(2)))=UINT16_MAX;
uint32_t r1_conn_field6_get(void) { return r1_connection_field6; }

volatile uint16_t r1_connection_field8
 __attribute__((section(".r1.connection.field8"),aligned(2)))=UINT16_MAX;
volatile uint16_t r1_connection_field10
 __attribute__((section(".r1.connection.field10"),aligned(2)))=UINT16_MAX;
uint32_t r1_phone_connection_handle_get(void) { return r1_connection_field8; }
uint32_t r1_glasses_connection_handle_get(void) { return r1_connection_field10; }
