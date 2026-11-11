/* SPDX-License-Identifier: GPL-3.0-or-later
 * Quantum Leaps QP/C 6.5.1 src/qf/qf_act.c (commit 416dcec8820b9cdb5827497e645d0d9375db53c6,
 * third-party/upstream/qpc), compiled unmodified through the EM9305 port in this directory.
 * See qp_unit.h for the two port adaptations. Stock counterpart: libs/third_party/QPC/lib_QPC.a:qf_act.c.obj
 * (g2/symbols/ble_em9305.tsv).
 */
#define QP_UNIT_MODULE opencfw_em9305_qp_module_qf_act
/* Stock QF_bzero (0x310fac) is `if (len != 0) memset(p, 0, len)`, not upstream's byte loop, so the
 * hand-written QF_bzero in qpc-scheduler/framework_init.c provides the symbol and this copy is discarded. */
#define QF_bzero QF_bzero_upstream_unused
#include "qp_unit.h"
#include "qf_act.c"
