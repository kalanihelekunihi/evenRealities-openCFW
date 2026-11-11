/* SPDX-License-Identifier: GPL-3.0-or-later
 * Quantum Leaps QP/C 6.5.1 src/qk/qk.c (commit 416dcec8820b9cdb5827497e645d0d9375db53c6,
 * third-party/upstream/qpc), compiled unmodified through the EM9305 port in this directory.
 * See qp_unit.h for the two port adaptations. Stock counterpart: libs/third_party/QPC/lib_QPC.a:qk.c.obj
 * (g2/symbols/ble_em9305.tsv).
 */
#define QP_UNIT_MODULE opencfw_em9305_qp_module_qk
/* Stock QF_init (0x311014) differs from upstream (no QF_timeEvtHead_ clear, extra QF_subscrList_ / QF_maxPubSignal_
 * stores) and QF_run (0x311230) never returns, so framework_init.c / framework_run.c provide both; the upstream
 * copies are renamed and discarded by the link script. */
#define QF_init QF_init_upstream_unused
#define QF_run QF_run_upstream_unused
#include "qp_unit.h"
#include "qk.c"
