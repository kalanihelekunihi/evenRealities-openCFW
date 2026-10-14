/* Experimental source-linked Apollo Main HCI decoder table.
 * Pinned Cordio hci_evt.c contains 85 source decoder slots; native ROM
 * 0x6c910c has the same null and shared-pointer equivalence classes.
 * Its next word, reached by the selected native type-85 path, is zero;
 * retain it as an explicit sentinel in this experimental C table.
 * Stock decoder body equality and final link addresses remain unproven.
 */
#include "third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio/ble-host/sources/hci/ambiq/hci_evt.c"
#include <stddef.h>
#include <stdint.h>
_Static_assert(sizeof(void *) == 4u, "Apollo Main pointer width");
/* Pinned hciCb_t overlays the selected callback and handler offsets in
 * Main RAM 0x20073870. This does not allocate the adjacent product state. */
_Static_assert(sizeof(hciCb_t) == 36u, "HCI control block size");
_Static_assert(offsetof(hciCb_t, evtCback) == 8u, "event callback offset");
_Static_assert(offsetof(hciCb_t, secCback) == 12u, "security callback offset");
_Static_assert(offsetof(hciCb_t, aclCback) == 16u, "ACL callback offset");
_Static_assert(offsetof(hciCb_t, flowCback) == 20u, "flow callback offset");
_Static_assert(offsetof(hciCb_t, handlerId) == 32u, "handler offset");
_Static_assert(offsetof(hciCb_t, resetting) == 33u, "resetting offset");
const hciEvtParse_t audio_ble_hci_event_decoders_6c910c[86] = {
    NULL,
    hciEvtParseLeConnCmpl,
    hciEvtParseLeEnhancedConnCmpl,
    hciEvtParseDisconnectCmpl,
    hciEvtParseLeConnUpdateCmpl,
    hciEvtParseLeCreateConnCancelCmdCmpl,
    NULL,
    hciEvtParseReadRssiCmdCmpl,
    hciEvtParseReadChanMapCmdCmpl,
    hciEvtParseReadTxPwrLvlCmdCmpl,
    hciEvtParseReadRemoteVerInfoCmpl,
    hciEvtParseReadLeRemoteFeatCmpl,
    hciEvtParseLeLtkReqReplCmdCmpl,
    hciEvtParseLeLtkReqNegReplCmdCmpl,
    hciEvtParseEncKeyRefreshCmpl,
    hciEvtParseEncChange,
    hciEvtParseLeLtkReq,
    hciEvtParseVendorSpecCmdStatus,
    hciEvtParseVendorSpecCmdCmpl,
    hciEvtParseVendorSpec,
    hciEvtParseHwError,
    hciEvtParseLeAddDevToResListCmdCmpl,
    hciEvtParseLeRemDevFromResListCmdCmpl,
    hciEvtParseLeClearResListCmdCmpl,
    hciEvtParseLeReadPeerResAddrCmdCmpl,
    hciEvtParseLeReadLocalResAddrCmdCmpl,
    hciEvtParseLeSetAddrResEnableCmdCmpl,
    hciEvtParseLeEncryptCmdCmpl,
    hciEvtParseLeRandCmdCmpl,
    hciEvtParseRemConnParamRepCmdCmpl,
    hciEvtParseRemConnParamNegRepCmdCmpl,
    hciEvtParseReadDefDataLenCmdCmpl,
    hciEvtParseWriteDefDataLenCmdCmpl,
    hciEvtParseSetDataLenCmdCmpl,
    hciEvtParseReadMaxDataLenCmdCmpl,
    hciEvtParseRemConnParamReq,
    hciEvtParseDataLenChange,
    hciEvtParseReadPubKeyCmdCmpl,
    hciEvtParseGenDhKeyCmdCmpl,
    hciEvtParseWriteAuthTimeoutCmdCmpl,
    hciEvtParseAuthTimeoutExpiredEvt,
    hciEvtParseReadPhyCmdCmpl,
    hciEvtParseSetDefPhyCmdCmpl,
    hciEvtParsePhyUpdateCmpl,
    NULL,
    hciEvtParseLeScanTimeout,
    hciEvtParseLeAdvSetTerm,
    hciEvtParseLeScanReqRcvd,
    hciEvtParseLePerAdvSyncEst,
    NULL,
    hciEvtParseLePerAdvSyncLost,
    NULL,
    hciEvtParseLeCmdCmpl,
    hciEvtParseLeCmdCmpl,
    hciEvtParseLeCmdCmpl,
    hciEvtParseLeCmdCmpl,
    hciEvtParseLeCmdCmpl,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    hciEvtParseLeSetConnCteRcvParm,
    hciEvtParseLeSetConnCteTxParm,
    hciEvtParseLeConnCteReqEn,
    hciEvtParseLeConnCteRspEn,
    hciEvtParseLeCisEst,
    hciEvtParseLeCisReq,
    hciEvtParseDisconnectCmpl,
    hciEvtParseLeReqPeerScaCmpl,
    hciEvtParseLeSetCigParamsCmdCmpl,
    hciEvtParseLeRemoveCigCmdCmpl,
    hciEvtParseLeSetupIsoDataPathCmdCmpl,
    hciEvtParseLeRemoveIsoDataPathCmdCmpl,
    hciEvtParseConfigDataPathCmdCmpl,
    hciEvtParseReadLocalSupCodecsCmdCmpl,
    hciEvtParseReadLocalSupCodecCapCmdCmpl,
    hciEvtParseReadLocalSupCtrDlyCmdCmpl,
    hciEvtParseLeCreateBigCmpl,
    hciEvtParseLeTerminateBigCmpl,
    hciEvtParseLeBigSyncEst,
    hciEvtParseLeBigSyncLost,
    hciEvtParseLeBigTermSyncCmpl,
    hciEvtParseLeBigInfoAdvRpt,
    NULL,
};
_Static_assert(sizeof(audio_ble_hci_event_decoders_6c910c) == 86u * 4u, "HCI decoder table size");
