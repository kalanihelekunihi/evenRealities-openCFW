#include <stdint.h>

/* Synthetic bytes only. Their sizes test the stock descriptor geometry. */
__attribute__((used,section(".touch_data")))
uint32_t touch_fixture_data[241] = {1u,2u,3u,4u};

__attribute__((used,section(".touch_bss")))
uint32_t touch_fixture_bss[428];
