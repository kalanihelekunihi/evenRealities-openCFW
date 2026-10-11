#include <stdint.h>

/* Complete stock 0x00591d14..0x00591d55 signed-halfword source map. */
uint32_t g2_pdm_clock_source(int32_t raw) {
    int32_t const source = (int16_t)raw;
    if (source == 0) return 6u;
    if (source == 0x100 || source == 0x202) return 4u;
    if (source == 0x200) return 5u;
    if (source == 0x201 || source == 0x203 || source == 0x204) return 2u;
    if (source == 0x205) return 3u;
    return 7u;
}
