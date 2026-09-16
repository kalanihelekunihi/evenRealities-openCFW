/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_BACKUP_EXCEPTION_STATE_H
#define OPEN_CFW_GX8002_BACKUP_EXCEPTION_STATE_H
#include <stdint.h>
#include <stddef.h>

/* Layout stored by backup exception entry 0x3bb40..0x3bb80.
 * Control registers retain their architectural numbers pending broader
 * exception-handler reconstruction. This does not implement entry/return.
 */
struct open_cfw_gx8002_exception_frame {
    uint32_t r0_r12[13];
    uint32_t r13;
    uint32_t interrupted_sp;
    uint32_t r15;
    uint32_t control_register_2;
    uint32_t control_register_4;
};
_Static_assert(sizeof(struct open_cfw_gx8002_exception_frame)==72,"frame size");
_Static_assert(offsetof(struct open_cfw_gx8002_exception_frame,r13)==52,"r13 slot");
_Static_assert(offsetof(struct open_cfw_gx8002_exception_frame,interrupted_sp)==56,"sp slot");
_Static_assert(offsetof(struct open_cfw_gx8002_exception_frame,r15)==60,"r15 slot");
_Static_assert(offsetof(struct open_cfw_gx8002_exception_frame,control_register_2)==64,"cr2 slot");
_Static_assert(offsetof(struct open_cfw_gx8002_exception_frame,control_register_4)==68,"cr4 slot");
extern uint32_t open_cfw_gx8002_backup_exception_stack[192];
extern volatile uint32_t open_cfw_gx8002_backup_interrupted_sp;
#endif
