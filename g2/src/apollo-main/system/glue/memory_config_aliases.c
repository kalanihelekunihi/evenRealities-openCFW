/* Clock reset callers use the Apollo MCU/SRAM memory config entries.
 * Export their original source bodies directly, with no extra call frame. */
#include "../../runtime/info-memory/memory.c"

__asm__(".global stock_mcu_memory_config\n"
        ".set stock_mcu_memory_config, audio_mcu_memory_config\n"
        ".global stock_sram_config\n"
        ".set stock_sram_config, audio_sram_config\n");
