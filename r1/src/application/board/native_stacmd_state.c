#include "native_stacmd.h"
/* Native scatter load explicitly writes four zero bytes at0x200075c0,
 * immediately before the existing108-byte STACMD configuration. */
volatile uint32_t r1_stacmd_failed_transactions
    __attribute__((section(".r1.stacmd.failed_transactions"),aligned(4)))=0;
