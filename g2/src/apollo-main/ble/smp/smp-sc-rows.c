/* Experimental source-owned storage for three SMP SC rows observed by
 * SmpScInit at native SRAM 0x200728f4. This does not establish the original
 * allocation boundary or a final linker address. */
#include <stdint.h>

__attribute__((aligned(4))) uint8_t audio_ble_smp_sc_rows[3u][28u];
_Static_assert(sizeof(audio_ble_smp_sc_rows) == 84u, "three SMP SC rows");
