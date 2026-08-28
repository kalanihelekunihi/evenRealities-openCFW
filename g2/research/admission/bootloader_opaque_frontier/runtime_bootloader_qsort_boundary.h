/* SPDX-License-Identifier: MIT */
/* Typed admission boundary for the retained G2 bootloader qsort cluster. */

#ifndef OPEN_CFW_BOOTLOADER_QSORT_BOUNDARY_H
#define OPEN_CFW_BOOTLOADER_QSORT_BOUNDARY_H

typedef __UINT32_TYPE__ open_cfw_boot_qsort_u32;
typedef __INT32_TYPE__ open_cfw_boot_qsort_s32;

typedef open_cfw_boot_qsort_s32 (*open_cfw_boot_qsort_compare_fn)(
    const void *, const void *);

typedef void (*open_cfw_boot_qsort_public_fn)(
    void *, open_cfw_boot_qsort_u32, open_cfw_boot_qsort_u32,
    open_cfw_boot_qsort_compare_fn);

typedef void (*open_cfw_boot_qsort_core_fn)(
    void *, open_cfw_boot_qsort_u32, open_cfw_boot_qsort_u32,
    open_cfw_boot_qsort_u32, open_cfw_boot_qsort_compare_fn);

typedef enum open_cfw_boot_qsort_admission_status {
    OPEN_CFW_BOOT_QSORT_EXACT_PROVIDER_UNSUPPORTED = 1,
    OPEN_CFW_BOOT_QSORT_GENERIC_BEHAVIOR_CANDIDATE_ONLY = 2
} open_cfw_boot_qsort_admission_status;

typedef struct open_cfw_boot_qsort_boundary {
    open_cfw_boot_qsort_u32 core_start;
    open_cfw_boot_qsort_u32 core_end;
    open_cfw_boot_qsort_u32 wrapper_start;
    open_cfw_boot_qsort_u32 wrapper_end;
    open_cfw_boot_qsort_u32 direct_caller;
    open_cfw_boot_qsort_u32 comparator_pointer;
    open_cfw_boot_qsort_u32 record_width;
    const char *core_sha256;
    const char *wrapper_sha256;
    const char *provider_family;
    const char *license_status;
    open_cfw_boot_qsort_admission_status status;
} open_cfw_boot_qsort_boundary;

const open_cfw_boot_qsort_boundary *
open_cfw_bootloader_qsort_boundary(void);

open_cfw_boot_qsort_admission_status
open_cfw_bootloader_qsort_admission_status(void);

#endif
