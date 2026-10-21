#include <stdint.h>

/* Stock Apollo Main ROM at 0x78f558..0x78f55d, little endian int16_t. */
const int16_t g2_codec_i2s_irq_number __attribute__((section(".g2_rom_0078f558"))) = 44;
const int16_t g2_pdm_alternate_irq __attribute__((section(".g2_rom_0078f55a"))) = 48;
const int16_t g2_pdm_production_irq __attribute__((section(".g2_rom_0078f55c"))) = 48;
