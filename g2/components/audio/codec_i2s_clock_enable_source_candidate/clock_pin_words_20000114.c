/* Nine initialized codec pin descriptors decoded from the official
 * Apollo Main low-RAM startup record. Order follows stock RAM addresses. */
#include <stdint.h>

#define PIN_WORD(name, value) \
    __attribute__((section(".data.opencfw.codec.clock_pin_" #name), used)) \
    const uint32_t g2_codec_clock_pin_##name = value

PIN_WORD(0a, 0x00000402u);
PIN_WORD(0d, 0x00000409u);
PIN_WORD(0b, 0x00000c09u);
PIN_WORD(0c, 0x00000409u);
PIN_WORD(1a, 0x0000040au);
PIN_WORD(1d, 0x00000409u);
PIN_WORD(1e, 0x0000040au);
PIN_WORD(1b, 0x0000040au);
PIN_WORD(1c, 0x0000040au);

_Static_assert(sizeof(g2_codec_clock_pin_0a) == 4, "codec pin word extent");
