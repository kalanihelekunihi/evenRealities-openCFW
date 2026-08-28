/*
 * SPDX-License-Identifier: MIT
 *
 * This descriptor intentionally does not implement or forward qsort.  The
 * stock body is attributable only to the IAR DLIB family; its exact release,
 * source archive, and redistribution authority are not authenticated.  The
 * separate MIT scalar-runtime insertion sort is a behavior oracle, not an
 * exact algorithmic or binary provider for this bootloader span.
 */

#include "runtime_bootloader_qsort_boundary.h"

static const open_cfw_boot_qsort_boundary open_cfw_qsort_boundary = {
    0x00423A48U,
    0x00423D08U,
    0x00423D08U,
    0x00423D20U,
    0x0041FA22U,
    0x0041F9F1U,
    8U,
    "9c13dd0e980154026e6c64019ce90997dcbd5abafb79aabbbf7d3def82215bb8",
    "ebab1f26584cfab24667fa6bd4a9c63641d5676a46affda15c6478a5d697d474",
    "IAR DLIB (exact EWARM release and archive variant unresolved)",
    "proprietary provider; source and binary redistribution authority unresolved",
    OPEN_CFW_BOOT_QSORT_EXACT_PROVIDER_UNSUPPORTED
};

const open_cfw_boot_qsort_boundary *
open_cfw_bootloader_qsort_boundary(void)
{
    return &open_cfw_qsort_boundary;
}

open_cfw_boot_qsort_admission_status
open_cfw_bootloader_qsort_admission_status(void)
{
    return OPEN_CFW_BOOT_QSORT_EXACT_PROVIDER_UNSUPPORTED;
}
