/* SPDX-License-Identifier: GPL-3.0-or-later
 * Prolog shared by the EM9305 QP/C 6.5.1 unit wrappers (the *_unit.c files in this directory).
 * Each wrapper defines QP_UNIT_MODULE (the existing module-name string symbol in
 * qpc-scheduler/qp_module_names.c), includes this header, then #includes the unmodified
 * upstream .c file from third-party/upstream/qpc. Two project-specific adaptations:
 *  1. Q_this_module_ resolves to the shared stock module-name strings (stock rodata
 *     0x33451c..0x334538) instead of a per-file static copy.
 *  2. QP's global objects live at their stock SRAM addresses (the rest of the image and the
 *     lowered stock code address them absolutely); linker pins in g2-em9305.ld.
 */
#ifndef qp_unit_h
#define qp_unit_h

#define QP_IMPL /* every upstream QP source defines this before its first include */
#include "qf_port.h"
#include "qassert.h"

#undef Q_DEFINE_THIS_MODULE
#define Q_DEFINE_THIS_MODULE(name_) extern char_t const Q_this_module_[];
#define Q_this_module_ QP_UNIT_MODULE

#define OPENCFW_PIN(sym_) __attribute__((section(".bss.opencfw_" sym_)))
extern QActive *QF_active_[QF_MAX_ACTIVE + 1U] OPENCFW_PIN("qf_active_80131c");
extern uint_fast8_t QF_maxPool_ OPENCFW_PIN("qf_maxpool_801360");
extern QMPool QF_pool_[QF_MAX_EPOOL] OPENCFW_PIN("qf_pool_801368");
extern QK_Attr QK_attr_ OPENCFW_PIN("qk_attr_801394");
/* qf_ps.c is not part of the stock image; QF_init zeroes these two (declared in qf_pkg.h) */
extern QSubscrList *QF_subscrList_ OPENCFW_PIN("qf_subscrlist_801390");
extern enum_t QF_maxPubSignal_ OPENCFW_PIN("qf_maxpubsignal_801364");

#endif
