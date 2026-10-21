#include <stdint.h>

/* Native RAM 0x200737b0: selected slave mode paths write a halfword at
 * +0x22, so the observed source range extends through +0x23. */
uint8_t audio_ble_comm_mode[0x24] __attribute__((aligned(4)));
