#include <stdint.h>
/* SDK extent and pointer addends bound; startup/lifecycle and final placement remain open. */
_Alignas(4) uint8_t opencfw_em9305_ext_init_records_802d20[3][704] __attribute__((section(".bss.opencfw_ext_init_records_802d20")));
uint8_t *const opencfw_em9305_ext_init_records_3357a8[3] __attribute__((section(".rodata.opencfw_ext_init_records"))) = {opencfw_em9305_ext_init_records_802d20[0],opencfw_em9305_ext_init_records_802d20[1],opencfw_em9305_ext_init_records_802d20[2]};
_Static_assert(sizeof(opencfw_em9305_ext_init_records_802d20)==2112,"record allocation extent");
_Static_assert(sizeof(opencfw_em9305_ext_init_records_3357a8)==12,"pointer table extent");
