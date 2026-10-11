/* Clock reset INFO1 cache fill enters Apollo 0x47f954. */
#include "../info_memory_offline/info.c"

__asm__(".global stock_info_populate\n"
        ".set stock_info_populate, audio_info1_populate\n");
