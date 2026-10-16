#include <stdint.h>
/* Authenticated cold scatter initialization: context is20 zero bytes at
 * 0x2000687c; shared transaction request is20 zero bytes at0x20016b70. */
volatile uint8_t r1_yhm_transport_context[20]
    __attribute__((section(".r1.yhm.transport_context"),aligned(4)))={0};
volatile uint8_t r1_yhm_request[20]
    __attribute__((section(".r1.yhm.request"),aligned(4)))={0};
