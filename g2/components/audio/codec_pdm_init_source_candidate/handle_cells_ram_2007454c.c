/* Mutable pointer cells populated by the native PDM initialization paths. */
#include <stdint.h>

__attribute__((section(".bss.opencfw.pdm.alternate_handle"), used))
void *g2_pdm_alternate_handle;

__attribute__((section(".bss.opencfw.pdm.production_handle"), used))
void *g2_pdm_production_handle;

_Static_assert(sizeof(g2_pdm_alternate_handle) == 4, "alternate PDM handle cell");
_Static_assert(sizeof(g2_pdm_production_handle) == 4, "production PDM handle cell");
