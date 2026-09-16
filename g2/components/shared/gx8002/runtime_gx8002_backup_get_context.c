/* SPDX-License-Identifier: MIT */
/* LvpGetContext, pinned NationalChip lvp/common/lvp_buffer.c adapted to
 * the recovered four-slot backup configuration. */
#include "runtime_gx8002_backup_context_storage.h"
#include <stddef.h>
_Static_assert(sizeof(LVP_CONTEXT)==32,"context prefix");
_Static_assert(offsetof(LVP_CONTEXT,snpu_buffer)==16,"processing buffer pointer");
int open_cfw_gx8002_backup_get_context(unsigned index,
                                     LVP_CONTEXT *volatile *context,
                                     volatile unsigned *size)
{
    unsigned char *slot=backup_context_frames[index & 3u];
    volatile LVP_CONTEXT *record=(volatile LVP_CONTEXT *)slot;
    record->ctx_header=&backup_context_header;
    record->snpu_buffer=slot+sizeof(LVP_CONTEXT);
    *context=(LVP_CONTEXT *)slot;
    *size=BACKUP_CONTEXT_BYTES;
    return 0;
}
