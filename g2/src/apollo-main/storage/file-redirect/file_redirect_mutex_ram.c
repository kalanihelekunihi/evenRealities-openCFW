/* Companion redirect mutex pointer cell initialized at stock 0x474d9c. */
#include <stdint.h>

void *g2_codec_redirect_mutex
    __attribute__((section(".bss.opencfw.fileheap.redirect_mutex"), aligned(4), used));
_Static_assert(sizeof(g2_codec_redirect_mutex) == 4u, "stock pointer cell");

/* Stock RAM 0x200748f4 is one cell: redirect_init (0x474d9c) stores the
 * redirect mutex here and file_open/read/write/close lock it under the name
 * audio_file_api_mutex. Two separate objects left the file-API handle NULL,
 * so osMutexAcquire returned osErrorParameter and every file_open failed
 * (2026-10-31 sim OTA check). */
extern void *audio_file_api_mutex __attribute__((alias("g2_codec_redirect_mutex")));
