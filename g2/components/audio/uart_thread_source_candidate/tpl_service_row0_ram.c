/* Observed TPL service-zero row; later service indices remain unbounded. */
#include <stdint.h>

__attribute__((section(".bss.opencfw.tpl.service.row0"), used, aligned(4)))
uint8_t audio_tpl_service_table[20];
