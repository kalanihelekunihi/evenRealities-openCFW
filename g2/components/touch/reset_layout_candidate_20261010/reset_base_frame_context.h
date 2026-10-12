/* SPDX-License-Identifier: MIT */
#ifndef TOUCH_BASE_FRAME_CONTEXT_H
#define TOUCH_BASE_FRAME_CONTEXT_H
#include <stdint.h>
/* Exact field order from pinned PDL cy_msclp.h; local declaration avoids
 * pulling its unrelated libc-dependent inline helper bodies into this TU. */
typedef struct {
 uint32_t senseDutyCtl, swSelCdacFl, swSelTop, swSelComp;
 uint32_t swSelSh, swSelCmod1, swSelCmod2;
} touch_msclp_mode_config;
typedef struct {
 uint32_t ctl, scanCtl1, scanCtl2;
 uint32_t initCtl1, initCtl2, initCtl3, initCtl4;
 uint32_t senseDutyCtl, sensePeriodCtl, filterCtl;
 uint32_t ccompCdacCtl, ditherCdacCtl, mscCmpCtl;
 uint32_t obsCtl, aosCtl, ceCtl, pumpCtl, imoCtl;
 uint32_t intr, intrSet, intrMask, intrLp, intrLpSet, intrLpMask;
 uint32_t swSelCdacRe, swSelCdacCo, swSelCdacCf, swSelBgr;
 uint32_t swSelCswFunc[8];
 touch_msclp_mode_config mode[4];
} touch_msclp_base_config;
extern touch_msclp_base_config touch_generated_base_frame_context;
#endif
