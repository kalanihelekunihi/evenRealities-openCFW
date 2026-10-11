/* PCM2.1 caller uses the same Apollo MAIN 0x474EFA cache-disable entry. */
#include "../transition_snapshot_offline/producers.c"

__asm__(".global stock_cache_disable\n"
        ".set stock_cache_disable, pcm22_icache_disable\n"
        ".global stock_cache_enable\n"
        ".set stock_cache_enable, pcm22_icache_enable\n");
