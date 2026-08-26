/* SPDX-License-Identifier: Apache-2.0 */
#ifndef OPEN_CFW_RUNTIME_CORDIO_DM_CONN_H
#define OPEN_CFW_RUNTIME_CORDIO_DM_CONN_H

#include "wsf_types.h"
#include "dm_api.h"
#include "dm_main.h"
#include "dm_conn.h"

dmConnCcb_t *dmConnCmplStates(void);
void dmConn2ActRssiRead(dmConnCcb_t *pCcb, hciEvt_t *pEvent);
void dmConn2ActRemoteConnParamReq(dmConnCcb_t *pCcb, hciEvt_t *pEvent);
void dmConn2ActDataLenChange(dmConnCcb_t *pCcb, hciEvt_t *pEvent);
void dmConn2ActWriteAuthToCmpl(dmConnCcb_t *pCcb, hciEvt_t *pEvent);
void dmConn2ActAuthToExpired(dmConnCcb_t *pCcb, hciEvt_t *pEvent);
void dmConn2ActReadRemoteFeaturesCmpl(dmConnCcb_t *pCcb, hciEvt_t *pEvent);
void dmConn2ActReadRemoteVerInfoCmpl(dmConnCcb_t *pCcb, hciEvt_t *pEvent);
void dmConn2ActReqPeerSca(dmConnCcb_t *pCcb, hciEvt_t *pEvent);
void dmConnSetConnSpec(uint8_t initPhy, hciConnSpec_t *pConnSpec);
void dmConnSetScanInterval(uint8_t initPhy, uint16_t scanInterval, uint16_t scanWindow);
void vendorCcbInitLike(void);

#if DM_CONN_MAX == 3 && DM_NUM_PHYS == 2 && UINTPTR_MAX == 0xFFFFFFFFU
_Static_assert(sizeof(dmConnCcb_t) == 0x30U, "G2 DM connection CCB ABI");
_Static_assert(sizeof(dmConnCb_t) == 0xC4U, "G2 DM connection control-block ABI");
#endif

#endif
