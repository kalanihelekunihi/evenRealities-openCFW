/*
 * openR1 fail-closed GH3X2X democode ABI bridge.
 *
 * The executable Goodix algorithm census and goodix_mem implementation now
 * compile from owner-authorized transparent C and are retained in the target
 * image. Those recovered routines expose narrow typed contracts, however,
 * while the public democode drives a large global frame/result ABI. Until a
 * checked adapter maps every enabled function ID, frame layout, lifetime, and
 * result sink onto those typed contracts, this compatibility surface remains
 * deliberately unavailable. No vendor algorithm archive is linked.
 *
 * Every stub below fails closed using the democode's own error codes and
 * never fabricates sensor or biometric data:
 *   - GS8-returning algorithm entry points return GH3X2X_RET_RESOURCE_ERROR
 *     ("resource full or not available"), the democode's own code for an
 *     unavailable resource.
 *   - Version getters write the democode's own "no_ver" marker to report that
 *     this live ABI binding is unavailable (not that the source bodies are
 *     absent).
 *   - The frame/transport hooks of the excluded PC-tool upload protocol
 *     drop their payloads; GH3X2X_UprotocolPacketFormat reports a
 *     zero-length packet.
 *   - The ACC/PPG timestamp-sync helpers retain the matched public democode
 *     behavior: empty hooks and a constant-one frame-data flag.
 *
 * This file is compiled only where the pinned vendor tree is available
 * (host vendor-goodix-test and the Nordic SDK/Zephyr images); it includes vendor
 * headers so the stub signatures are checked against the real prototypes.
 */

#include "gh_drv.h"
#include "gh3x2x_demo_algo_call.h"
#include "gh_uprotocol.h"

/* Marker written by the real algo-call layer when a version is absent. */
static void gh3x2x_stub_write_no_ver(GCHAR version[150]) {
    static const GCHAR marker[] = "no_ver";
    GU8 index = 0u;
    if (version == GH3X2X_PTR_NULL) {
        return;
    }
    while (marker[index] != '\0') {
        version[index] = marker[index];
        ++index;
    }
    version[index] = '\0';
}

/* --- Algorithm-call ABI entry points (typed live binding not yet admitted) --- */

GS8 GH3X2X_AlgoInit(GU32 unFunctionID) {
    UNUSED_VAR(unFunctionID);
    return GH3X2X_RET_RESOURCE_ERROR;
}

GS8 GH3X2X_AlgoDeinit(GU32 unFunctionID) {
    UNUSED_VAR(unFunctionID);
    return GH3X2X_RET_RESOURCE_ERROR;
}

GS8 GH3X2X_AlgoCalculate(GU32 unFunctionID) {
    UNUSED_VAR(unFunctionID);
    return GH3X2X_RET_RESOURCE_ERROR;
}

void GH3X2X_AlgoSensorEnable(GU8 uchAlgoGsensorEnable, GU8 uchAlgoCapEnable,
                             GU8 uchAlgoTempEnable) {
    UNUSED_VAR(uchAlgoGsensorEnable);
    UNUSED_VAR(uchAlgoCapEnable);
    UNUSED_VAR(uchAlgoTempEnable);
}

void GH3X2X_AlgoVersion(GU8 uchFunctionID, GCHAR version[150]) {
    UNUSED_VAR(uchFunctionID);
    gh3x2x_stub_write_no_ver(version);
}

void GH3X2X_AlgoCallConfigInit(
    const STGh3x2xFrameInfo *const pstGh3x2xFrameInfo[],
    GU8 uchAlgoCfgIndex) {
    UNUSED_VAR(pstGh3x2xFrameInfo);
    UNUSED_VAR(uchAlgoCfgIndex);
}

void GH3X2X_WriteAlgConfigWithVirtualReg(GU16 usVirtualRegAddr,
                                         GU16 usVirtualRegValue) {
    /* Algorithm virtual-register window write; dropped because the
     * algorithm layer is absent.  The driver register windows below
     * 0x3000 are still applied by the compiled driver source. */
    UNUSED_VAR(usVirtualRegAddr);
    UNUSED_VAR(usVirtualRegValue);
}

/* --- ACC/PPG timestamp sync helpers (algorithm-call layer, absent) --- */

void GH3X2X_TimestampSyncAccInit(void) {
}

void GH3X2X_TimestampSyncPpgInit(GU32 unFunctionID) {
    UNUSED_VAR(unFunctionID);
}

void GH3X2X_TimestampSyncSetPpgIntFlag(GU8 uchPpgIntFlag) {
    UNUSED_VAR(uchPpgIntFlag);
}

void GH3X2X_TimestampSyncFillAccSyncBuffer(GU32 unTimeStamp, GS16 usAccX,
                                           GS16 usAccY, GS16 usAccZ) {
    UNUSED_VAR(unTimeStamp);
    UNUSED_VAR(usAccX);
    UNUSED_VAR(usAccY);
    UNUSED_VAR(usAccZ);
}

void GH3X2X_TimestampSyncFillPpgSyncBuffer(
    GU32 unTimeStamp, const STGh3x2xFrameInfo *const pstFrameInfo) {
    UNUSED_VAR(unTimeStamp);
    UNUSED_VAR(pstFrameInfo);
}

GU8 GH3X2X_TimestampSyncGetFrameDataFlag(void) {
    /* Exact public-democode/recovered body at 0x0002AE00. */
    return 1u;
}

/* --- PC-tool upload protocol (module/gh_protocol, kernel/gh_demo_protocol;
 *      excluded from the openR1 build: no external command surface) --- */

GU8 GH3X2X_UprotocolPacketFormat(GU8 uchCmd, GU8 *puchPacketBuffer,
                                 GU8 *puchPayloadData,
                                 GU8 uchPayloadDataLen) {
    UNUSED_VAR(uchCmd);
    UNUSED_VAR(puchPacketBuffer);
    UNUSED_VAR(puchPayloadData);
    UNUSED_VAR(uchPayloadDataLen);
    return 0u; /* zero-length packet: nothing to transmit */
}

void Gh2x2xUploadDataToMaster(const STGh3x2xFrameInfo *const pstFrameInfo,
                              GU16 usFrameCnt, GU16 usFrameNum,
                              GU8 *puchTagArray) {
    UNUSED_VAR(pstFrameInfo);
    UNUSED_VAR(usFrameCnt);
    UNUSED_VAR(usFrameNum);
    UNUSED_VAR(puchTagArray);
}

void Gh3x2xDemoSendProtocolData(GU8 *puchProtocolDataBuffer,
                                GU16 usProtocolDataLen) {
    UNUSED_VAR(puchProtocolDataBuffer);
    UNUSED_VAR(usProtocolDataLen);
}

void GH3X2X_GetVersion(GU8 uchGetVersionType, GCHAR pszVersionString[150]) {
    UNUSED_VAR(uchGetVersionType);
    gh3x2x_stub_write_no_ver(pszVersionString);
}
