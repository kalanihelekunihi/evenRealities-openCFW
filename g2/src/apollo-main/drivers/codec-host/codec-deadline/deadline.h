#ifndef CODEC_DEADLINE_H
#define CODEC_DEADLINE_H
#include <stdint.h>
/* Timeout is passed uint32 but sign-extended into64-bit deadline in stock.
 * Tick getter zero-extends32-bit OS tick. Tick wrap can leave unreachable
 * deadline; no safe tick-wrap normalization added to this reconstruction. */
uint32_t codec_read_byte_deadline(uint8_t *,uint32_t);
#endif
