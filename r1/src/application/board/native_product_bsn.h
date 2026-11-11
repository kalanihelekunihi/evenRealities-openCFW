#ifndef R1_NATIVE_PRODUCT_BSN_H
#define R1_NATIVE_PRODUCT_BSN_H
#include <stdint.h>
/* Read at most capacity bytes. Invalid/erased lengths use up to 21 ff bytes;
 * no terminator is appended. Return the number of bytes written. */
uint32_t r1_product_bsn_read(void *destination,uint32_t capacity);
/* Native compatibility entry: the caller must provide 30 bytes. */
void r1_product_bsn_get(void *destination);
#endif
