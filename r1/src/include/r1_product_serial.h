#ifndef R1_PRODUCT_SERIAL_H
#define R1_PRODUCT_SERIAL_H
#include <stdint.h>
/* Writable15-byte destination; optional writable length byte. Same C body. */
uint32_t r1_native_product_serial_read(void *,uint8_t *);
uint32_t r1_advertising_product_sn_read(void *,uint8_t *);
#endif
