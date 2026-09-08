/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip lvp/common/snpu_engine/lvp_kws.c and
 * lvp/common/lvp_audio_in.c at 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Copyright (C) 2001-2020 NationalChip Co., Ltd.
 * See NATIONALCHIP-STREAM-NOTICE.txt. */
#include <stddef.h>
#include <driver/gx_snpu.h>
#include <stream-shutdown-interfaces.h>
GX_SNPU_CALLBACK open_cfw_gx8002_snpu_callback;
_Static_assert(sizeof(open_cfw_gx8002_snpu_callback) == 4, "callback slot");
int LvpKwsDone(void)
{
    gx_snpu_exit();
    open_cfw_gx8002_snpu_callback = NULL;
    return 0;
}
int LvpAudioInDone(void)
{
    gx_audio_in_exit();
    return 0;
}
