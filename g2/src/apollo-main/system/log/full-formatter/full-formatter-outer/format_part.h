#ifndef G2_MAIN_FORMAT_PART_H
#define G2_MAIN_FORMAT_PART_H
#include <stdint.h>
typedef struct {
    uint8_t prefix[8],body[96],suffix[32];
    uint32_t prefix_len,body_len,suffix_len,lead_zero,mid_zero,trail_zero;
} g2_format_part;
#endif
