/* Four mutable 32-byte PDM handle rows selected by the native acquire body. */
#include <stdint.h>

__attribute__((section(".bss.opencfw.pdm.handle_rows"), aligned(4), used))
uint8_t g2_pdm_handle_rows[4u * 32u];

_Static_assert(sizeof(g2_pdm_handle_rows) == 128, "PDM handle row extent");
