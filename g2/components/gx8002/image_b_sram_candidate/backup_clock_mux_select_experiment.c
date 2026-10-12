/* Stock image-B 0x100080f4..0x1000812f. The register is loaded as a word,
 * narrowed to its low byte, then written back as a word. The native three
 * accepted mux values and invalid-value return are preserved exactly.
 * Source: binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>

int32_t gx8002_image_b_clock_mux_select_100080f4(uint32_t selection)
{
    volatile uint32_t *const mux = (volatile uint32_t *)(uintptr_t)0xa0005058u;
    uint32_t low = (uint8_t)*mux;
    switch (selection) {
    case 0u:
        low &= 0xfbu;
        break;
    case 1u:
        low = (low & 0xf9u) | 0x04u;
        break;
    case 2u:
        low = (low & 0xfbu) | 0x06u;
        break;
    default:
        return -1;
    }
    *mux = low;
    return 0;
}
