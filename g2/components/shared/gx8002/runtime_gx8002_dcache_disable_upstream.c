/* SPDX-License-Identifier: MIT */
/* Implementation supplied by the pinned Apache-2.0 CSI header. */
#include <core_ck804.h>
void open_cfw_gx8002_dcache_disable_upstream(void)
{
    csi_dcache_disable();
}
