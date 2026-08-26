/*************************************************************************************************/
/* Clean-room Bluetooth HCI event decoder for the authenticated G2 Cordio callback ABI. */
/*************************************************************************************************/

#include "runtime_cordio_hci_evt.h"

#include <stddef.h>

#define OPEN_CFW_HCI_CB_EVENT_CALLBACK 0x08u
#define OPEN_CFW_HCI_EVENT_COMMAND_COMPLETE 0x0Eu
#define OPEN_CFW_HCI_EVENT_COMMAND_STATUS 0x0Fu
#define OPEN_CFW_HCI_EVENT_DISCONNECT_COMPLETE 0x05u
#define OPEN_CFW_HCI_EVENT_ENCRYPTION_CHANGE 0x08u
#define OPEN_CFW_HCI_EVENT_READ_REMOTE_VERSION 0x0Cu
#define OPEN_CFW_HCI_EVENT_HARDWARE_ERROR 0x10u
#define OPEN_CFW_HCI_EVENT_NUMBER_COMPLETED_PACKETS 0x13u
#define OPEN_CFW_HCI_EVENT_ENCRYPTION_KEY_REFRESH 0x30u
#define OPEN_CFW_HCI_EVENT_LE_META 0x3Eu
#define OPEN_CFW_HCI_EVENT_AUTH_PAYLOAD_TIMEOUT 0x57u
#define OPEN_CFW_HCI_EVENT_VENDOR 0xFFu
#define OPEN_CFW_HCI_INVALID_CALLBACK_EVENT 0xFFu

typedef struct {
    const uint8_t *cursor;
    uint8_t remaining;
    uint8_t failed;
} open_cfw_hci_reader_t;

extern void hciCmdRecvCmpl(uint8_t commands);
extern void hciCoreNumCmplPkts(uint8_t *data);
extern void hciCoreConnOpen(uint16_t handle);
extern void hciCoreConnClose(uint16_t handle);
extern void *hciCoreCisByHandle(uint16_t handle);
extern void hciCoreCisOpen(uint16_t handle);
extern void hciCoreCisClose(uint16_t handle);

#if defined(OPEN_CFW_HCI_EVT_PRODUCTION)
#define OPEN_CFW_HCI_EVT_PTR(type, address) ((type *)(uintptr_t)(address))
#define OPEN_CFW_HCI_EVT_STATS \
    OPEN_CFW_HCI_EVT_PTR(open_cfw_hci_evt_stats_t, 0x20073BC0u)
static hciEvtCback_t open_cfw_hci_evt_callback(void)
{
    return *OPEN_CFW_HCI_EVT_PTR(hciEvtCback_t, 0x20073870u + OPEN_CFW_HCI_CB_EVENT_CALLBACK);
}
#else
static open_cfw_hci_evt_stats_t open_cfw_hci_evt_stats;
static hciEvtCback_t open_cfw_hci_evt_callback_value;
#define OPEN_CFW_HCI_EVT_STATS (&open_cfw_hci_evt_stats)
static hciEvtCback_t open_cfw_hci_evt_callback(void)
{
    return open_cfw_hci_evt_callback_value;
}
#endif

static __attribute__((always_inline)) inline void open_cfw_hci_evt_zero(hciEvt_t *message)
{
    uint16_t index;
    uint8_t *bytes = (uint8_t *)(void *)message;
    for (index = 0u; index < (uint16_t)sizeof(*message); ++index) bytes[index] = 0u;
}

static __attribute__((always_inline)) inline open_cfw_hci_reader_t
open_cfw_hci_evt_reader(const uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t reader = {data, length, data == (const uint8_t *)0 && length != 0u};
    return reader;
}

static __attribute__((always_inline)) inline uint8_t open_cfw_hci_evt_u8(open_cfw_hci_reader_t *reader)
{
    if (reader->remaining == 0u || reader->cursor == (const uint8_t *)0) {
        reader->failed = 1u;
        return 0u;
    }
    --reader->remaining;
    return *reader->cursor++;
}

static __attribute__((always_inline)) inline uint16_t open_cfw_hci_evt_u16(open_cfw_hci_reader_t *reader)
{
    uint16_t value = open_cfw_hci_evt_u8(reader);
    value |= (uint16_t)open_cfw_hci_evt_u8(reader) << 8;
    return value;
}

static __attribute__((always_inline)) inline uint32_t open_cfw_hci_evt_u24(open_cfw_hci_reader_t *reader)
{
    uint32_t value = open_cfw_hci_evt_u16(reader);
    value |= (uint32_t)open_cfw_hci_evt_u8(reader) << 16;
    return value;
}

static __attribute__((always_inline)) inline void open_cfw_hci_evt_copy(
    open_cfw_hci_reader_t *reader, uint8_t *destination, uint8_t count)
{
    uint8_t index;
    for (index = 0u; index < count; ++index) destination[index] = open_cfw_hci_evt_u8(reader);
}

static __attribute__((always_inline)) inline void open_cfw_hci_evt_begin(
    hciEvt_t *message, uint8_t callback_event)
{
    open_cfw_hci_evt_zero(message);
    message->hdr.event = callback_event;
}

static __attribute__((always_inline)) inline void open_cfw_hci_evt_finish(
    hciEvt_t *message, const open_cfw_hci_reader_t *reader)
{
    if (reader->failed != 0u) message->hdr.event = OPEN_CFW_HCI_INVALID_CALLBACK_EVENT;
}

static __attribute__((always_inline)) inline void
open_cfw_hci_evt_deliver(hciEvt_t *message)
{
    hciEvtCback_t callback;
    if (message->hdr.event > HCI_LE_BIG_INFO_ADV_REPORT_CBACK_EVT) {
        ++OPEN_CFW_HCI_EVT_STATS->malformed;
        return;
    }
    callback = open_cfw_hci_evt_callback();
    if (callback != (hciEvtCback_t)0) {
        ++OPEN_CFW_HCI_EVT_STATS->delivered;
        callback(message);
    }
}

#define OPEN_CFW_SIMPLE_STATUS(NAME, MEMBER, EVENT_ID)                                      \
void NAME(hciEvt_t *message, uint8_t *data, uint8_t length)                                \
{                                                                                           \
    open_cfw_hci_reader_t reader = open_cfw_hci_evt_reader(data, length);                   \
    open_cfw_hci_evt_begin(message, EVENT_ID);                                               \
    message->MEMBER.status = open_cfw_hci_evt_u8(&reader);                                   \
    message->hdr.status = message->MEMBER.status;                                            \
    open_cfw_hci_evt_finish(message, &reader);                                               \
}

#define OPEN_CFW_STATUS_HANDLE(NAME, MEMBER, EVENT_ID)                                      \
void NAME(hciEvt_t *message, uint8_t *data, uint8_t length)                                \
{                                                                                           \
    open_cfw_hci_reader_t reader = open_cfw_hci_evt_reader(data, length);                   \
    open_cfw_hci_evt_begin(message, EVENT_ID);                                               \
    message->MEMBER.status = open_cfw_hci_evt_u8(&reader);                                   \
    message->hdr.status = message->MEMBER.status;                                            \
    message->MEMBER.handle = open_cfw_hci_evt_u16(&reader);                                  \
    open_cfw_hci_evt_finish(message, &reader);                                               \
}

void hciEvtParseLeConnCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length);
    open_cfw_hci_evt_begin(message, HCI_LE_CONN_CMPL_CBACK_EVT);
    message->leConnCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leConnCmpl.status;
    message->leConnCmpl.handle = open_cfw_hci_evt_u16(&r); message->leConnCmpl.role = open_cfw_hci_evt_u8(&r);
    message->leConnCmpl.addrType = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_copy(&r, message->leConnCmpl.peerAddr, 6u);
    message->leConnCmpl.connInterval = open_cfw_hci_evt_u16(&r); message->leConnCmpl.connLatency = open_cfw_hci_evt_u16(&r);
    message->leConnCmpl.supTimeout = open_cfw_hci_evt_u16(&r); message->leConnCmpl.clockAccuracy = open_cfw_hci_evt_u8(&r);
    open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeEnhancedConnCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length);
    open_cfw_hci_evt_begin(message, HCI_LE_ENHANCED_CONN_CMPL_CBACK_EVT);
    message->leConnCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leConnCmpl.status;
    message->leConnCmpl.handle = open_cfw_hci_evt_u16(&r); message->leConnCmpl.role = open_cfw_hci_evt_u8(&r);
    message->leConnCmpl.addrType = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_copy(&r, message->leConnCmpl.peerAddr, 6u);
    open_cfw_hci_evt_copy(&r, message->leConnCmpl.localRpa, 6u); open_cfw_hci_evt_copy(&r, message->leConnCmpl.peerRpa, 6u);
    message->leConnCmpl.connInterval = open_cfw_hci_evt_u16(&r); message->leConnCmpl.connLatency = open_cfw_hci_evt_u16(&r);
    message->leConnCmpl.supTimeout = open_cfw_hci_evt_u16(&r); message->leConnCmpl.clockAccuracy = open_cfw_hci_evt_u8(&r);
    open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseDisconnectCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length);
    open_cfw_hci_evt_begin(message, HCI_DISCONNECT_CMPL_CBACK_EVT);
    message->disconnectCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->disconnectCmpl.status;
    message->disconnectCmpl.handle = open_cfw_hci_evt_u16(&r); message->disconnectCmpl.reason = open_cfw_hci_evt_u8(&r);
    open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeConnUpdateCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length);
    open_cfw_hci_evt_begin(message, HCI_LE_CONN_UPDATE_CMPL_CBACK_EVT);
    message->leConnUpdateCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leConnUpdateCmpl.status;
    message->leConnUpdateCmpl.handle = open_cfw_hci_evt_u16(&r); message->leConnUpdateCmpl.connInterval = open_cfw_hci_evt_u16(&r);
    message->leConnUpdateCmpl.connLatency = open_cfw_hci_evt_u16(&r); message->leConnUpdateCmpl.supTimeout = open_cfw_hci_evt_u16(&r);
    open_cfw_hci_evt_finish(message, &r);
}

OPEN_CFW_SIMPLE_STATUS(hciEvtParseLeCreateConnCancelCmdCmpl, leCreateConnCancelCmdCmpl, HCI_LE_CREATE_CONN_CANCEL_CMD_CMPL_CBACK_EVT)

void hciEvtParseReadRssiCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_READ_RSSI_CMD_CMPL_CBACK_EVT);
    message->readRssiCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->readRssiCmdCmpl.status;
    message->readRssiCmdCmpl.handle = open_cfw_hci_evt_u16(&r); message->readRssiCmdCmpl.rssi = (int8_t)open_cfw_hci_evt_u8(&r);
    open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseReadChanMapCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_READ_CHAN_MAP_CMD_CMPL_CBACK_EVT);
    message->readChanMapCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->readChanMapCmdCmpl.status;
    message->readChanMapCmdCmpl.handle = open_cfw_hci_evt_u16(&r); open_cfw_hci_evt_copy(&r, message->readChanMapCmdCmpl.chanMap, HCI_CHAN_MAP_LEN);
    open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseReadTxPwrLvlCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); uint16_t handle;
    open_cfw_hci_evt_begin(message, HCI_READ_TX_PWR_LVL_CMD_CMPL_CBACK_EVT);
    message->readTxPwrLvlCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->readTxPwrLvlCmdCmpl.status;
    handle = open_cfw_hci_evt_u16(&r); message->readTxPwrLvlCmdCmpl.handle = (uint8_t)handle;
    message->readTxPwrLvlCmdCmpl.pwrLvl = (int8_t)open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseReadRemoteVerInfoCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_READ_REMOTE_VER_INFO_CMPL_CBACK_EVT);
    message->readRemoteVerInfoCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->readRemoteVerInfoCmpl.status;
    message->readRemoteVerInfoCmpl.handle = open_cfw_hci_evt_u16(&r); message->readRemoteVerInfoCmpl.version = open_cfw_hci_evt_u8(&r);
    message->readRemoteVerInfoCmpl.mfrName = open_cfw_hci_evt_u16(&r); message->readRemoteVerInfoCmpl.subversion = open_cfw_hci_evt_u16(&r);
    open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseReadLeRemoteFeatCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_READ_REMOTE_FEAT_CMPL_CBACK_EVT);
    message->leReadRemoteFeatCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leReadRemoteFeatCmpl.status;
    message->leReadRemoteFeatCmpl.handle = open_cfw_hci_evt_u16(&r); open_cfw_hci_evt_copy(&r, message->leReadRemoteFeatCmpl.features, HCI_FEAT_LEN);
    open_cfw_hci_evt_finish(message, &r);
}

OPEN_CFW_STATUS_HANDLE(hciEvtParseLeLtkReqReplCmdCmpl, leLtkReqReplCmdCmpl, HCI_LE_LTK_REQ_REPL_CMD_CMPL_CBACK_EVT)
OPEN_CFW_STATUS_HANDLE(hciEvtParseLeLtkReqNegReplCmdCmpl, leLtkReqNegReplCmdCmpl, HCI_LE_LTK_REQ_NEG_REPL_CMD_CMPL_CBACK_EVT)
OPEN_CFW_STATUS_HANDLE(hciEvtParseEncKeyRefreshCmpl, encKeyRefreshCmpl, HCI_ENC_KEY_REFRESH_CMPL_CBACK_EVT)

void hciEvtParseEncChange(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_ENC_CHANGE_CBACK_EVT);
    message->encChange.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->encChange.status;
    message->encChange.handle = open_cfw_hci_evt_u16(&r); message->encChange.enabled = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeLtkReq(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_LTK_REQ_CBACK_EVT);
    message->leLtkReq.handle = open_cfw_hci_evt_u16(&r); open_cfw_hci_evt_copy(&r, message->leLtkReq.randNum, HCI_RAND_LEN);
    message->leLtkReq.encDiversifier = open_cfw_hci_evt_u16(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseVendorSpecCmdStatus(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_VENDOR_SPEC_CMD_STATUS_CBACK_EVT);
    message->vendorSpecCmdStatus.opcode = open_cfw_hci_evt_u16(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseVendorSpecCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); uint8_t index = 0u;
    open_cfw_hci_evt_begin(message, HCI_VENDOR_SPEC_CMD_CMPL_CBACK_EVT);
    message->vendorSpecCmdCmpl.opcode = open_cfw_hci_evt_u16(&r);
    while (r.remaining != 0u && index < (uint8_t)(sizeof(hciEvt_t) - offsetof(hciVendorSpecCmdCmplEvt_t, param))) {
        message->vendorSpecCmdCmpl.param[index++] = open_cfw_hci_evt_u8(&r);
    }
    open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseVendorSpec(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); uint8_t index = 0u;
    open_cfw_hci_evt_begin(message, HCI_VENDOR_SPEC_CBACK_EVT);
    while (r.remaining != 0u && index < (uint8_t)(sizeof(hciEvt_t) - offsetof(hciVendorSpecEvt_t, param))) {
        message->vendorSpec.param[index++] = open_cfw_hci_evt_u8(&r);
    }
    open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseHwError(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_HW_ERROR_CBACK_EVT);
    message->hwError.code = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeEncryptCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_ENCRYPT_CMD_CMPL_CBACK_EVT);
    message->leEncryptCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leEncryptCmdCmpl.status;
    open_cfw_hci_evt_copy(&r, message->leEncryptCmdCmpl.data, HCI_ENCRYPT_DATA_LEN); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeRandCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_RAND_CMD_CMPL_CBACK_EVT);
    message->leRandCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leRandCmdCmpl.status;
    open_cfw_hci_evt_copy(&r, message->leRandCmdCmpl.randNum, HCI_RAND_LEN); open_cfw_hci_evt_finish(message, &r);
}

OPEN_CFW_SIMPLE_STATUS(hciEvtParseLeAddDevToResListCmdCmpl, leAddDevToResListCmdCmpl, HCI_LE_ADD_DEV_TO_RES_LIST_CMD_CMPL_CBACK_EVT)
OPEN_CFW_SIMPLE_STATUS(hciEvtParseLeRemDevFromResListCmdCmpl, leRemDevFromResListCmdCmpl, HCI_LE_REM_DEV_FROM_RES_LIST_CMD_CMPL_CBACK_EVT)
OPEN_CFW_SIMPLE_STATUS(hciEvtParseLeClearResListCmdCmpl, leClearResListCmdCmpl, HCI_LE_CLEAR_RES_LIST_CMD_CMPL_CBACK_EVT)

void hciEvtParseLeReadPeerResAddrCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_READ_PEER_RES_ADDR_CMD_CMPL_CBACK_EVT);
    message->leReadPeerResAddrCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leReadPeerResAddrCmdCmpl.status;
    open_cfw_hci_evt_copy(&r, message->leReadPeerResAddrCmdCmpl.peerRpa, BDA_ADDR_LEN); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeReadLocalResAddrCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_READ_LOCAL_RES_ADDR_CMD_CMPL_CBACK_EVT);
    message->leReadLocalResAddrCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leReadLocalResAddrCmdCmpl.status;
    open_cfw_hci_evt_copy(&r, message->leReadLocalResAddrCmdCmpl.localRpa, BDA_ADDR_LEN); open_cfw_hci_evt_finish(message, &r);
}

OPEN_CFW_SIMPLE_STATUS(hciEvtParseLeSetAddrResEnableCmdCmpl, leSetAddrResEnableCmdCmpl, HCI_LE_SET_ADDR_RES_ENABLE_CMD_CMPL_CBACK_EVT)
OPEN_CFW_STATUS_HANDLE(hciEvtParseRemConnParamRepCmdCmpl, leRemConnParamRepCmdCmpl, HCI_LE_REM_CONN_PARAM_REP_CMD_CMPL_CBACK_EVT)
OPEN_CFW_STATUS_HANDLE(hciEvtParseRemConnParamNegRepCmdCmpl, leRemConnParamNegRepCmdCmpl, HCI_LE_REM_CONN_PARAM_NEG_REP_CMD_CMPL_CBACK_EVT)

void hciEvtParseReadDefDataLenCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_READ_DEF_DATA_LEN_CMD_CMPL_CBACK_EVT);
    message->leReadDefDataLenCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leReadDefDataLenCmdCmpl.status;
    message->leReadDefDataLenCmdCmpl.suggestedMaxTxOctets = open_cfw_hci_evt_u16(&r);
    message->leReadDefDataLenCmdCmpl.suggestedMaxTxTime = open_cfw_hci_evt_u16(&r); open_cfw_hci_evt_finish(message, &r);
}

OPEN_CFW_SIMPLE_STATUS(hciEvtParseWriteDefDataLenCmdCmpl, leWriteDefDataLenCmdCmpl, HCI_LE_WRITE_DEF_DATA_LEN_CMD_CMPL_CBACK_EVT)
OPEN_CFW_STATUS_HANDLE(hciEvtParseSetDataLenCmdCmpl, leSetDataLenCmdCmpl, HCI_LE_SET_DATA_LEN_CMD_CMPL_CBACK_EVT)

void hciEvtParseReadMaxDataLenCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_READ_MAX_DATA_LEN_CMD_CMPL_CBACK_EVT);
    message->leReadMaxDataLenCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leReadMaxDataLenCmdCmpl.status;
    message->leReadMaxDataLenCmdCmpl.supportedMaxTxOctets = open_cfw_hci_evt_u16(&r);
    message->leReadMaxDataLenCmdCmpl.supportedMaxTxTime = open_cfw_hci_evt_u16(&r);
    message->leReadMaxDataLenCmdCmpl.supportedMaxRxOctets = open_cfw_hci_evt_u16(&r);
    message->leReadMaxDataLenCmdCmpl.supportedMaxRxTime = open_cfw_hci_evt_u16(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseRemConnParamReq(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_REM_CONN_PARAM_REQ_CBACK_EVT);
    message->leRemConnParamReq.handle = open_cfw_hci_evt_u16(&r); message->leRemConnParamReq.intervalMin = open_cfw_hci_evt_u16(&r);
    message->leRemConnParamReq.intervalMax = open_cfw_hci_evt_u16(&r); message->leRemConnParamReq.latency = open_cfw_hci_evt_u16(&r);
    message->leRemConnParamReq.timeout = open_cfw_hci_evt_u16(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseDataLenChange(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_DATA_LEN_CHANGE_CBACK_EVT);
    message->leDataLenChange.handle = open_cfw_hci_evt_u16(&r); message->leDataLenChange.maxTxOctets = open_cfw_hci_evt_u16(&r);
    message->leDataLenChange.maxTxTime = open_cfw_hci_evt_u16(&r); message->leDataLenChange.maxRxOctets = open_cfw_hci_evt_u16(&r);
    message->leDataLenChange.maxRxTime = open_cfw_hci_evt_u16(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseReadPubKeyCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_READ_LOCAL_P256_PUB_KEY_CMPL_CBACK_EVT);
    message->leP256.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leP256.status;
    open_cfw_hci_evt_copy(&r, message->leP256.key, HCI_P256_KEY_LEN); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseGenDhKeyCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_GENERATE_DHKEY_CMPL_CBACK_EVT);
    message->leGenDHKey.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leGenDHKey.status;
    open_cfw_hci_evt_copy(&r, message->leGenDHKey.key, HCI_DH_KEY_LEN); open_cfw_hci_evt_finish(message, &r);
}

OPEN_CFW_STATUS_HANDLE(hciEvtParseWriteAuthTimeoutCmdCmpl, writeAuthPayloadToCmdCmpl, HCI_WRITE_AUTH_PAYLOAD_TO_CMD_CMPL_CBACK_EVT)

void hciEvtParseAuthTimeoutExpiredEvt(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_AUTH_PAYLOAD_TO_EXPIRED_CBACK_EVT);
    message->authPayloadToExpired.handle = open_cfw_hci_evt_u16(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseReadPhyCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_READ_PHY_CMD_CMPL_CBACK_EVT);
    message->leReadPhyCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leReadPhyCmdCmpl.status;
    message->leReadPhyCmdCmpl.handle = open_cfw_hci_evt_u16(&r); message->leReadPhyCmdCmpl.txPhy = open_cfw_hci_evt_u8(&r);
    message->leReadPhyCmdCmpl.rxPhy = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

OPEN_CFW_SIMPLE_STATUS(hciEvtParseSetDefPhyCmdCmpl, leSetDefPhyCmdCmpl, HCI_LE_SET_DEF_PHY_CMD_CMPL_CBACK_EVT)

void hciEvtParsePhyUpdateCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_PHY_UPDATE_CMPL_CBACK_EVT);
    message->lePhyUpdate.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->lePhyUpdate.status;
    message->lePhyUpdate.handle = open_cfw_hci_evt_u16(&r); message->lePhyUpdate.txPhy = open_cfw_hci_evt_u8(&r);
    message->lePhyUpdate.rxPhy = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeScanTimeout(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    /* The authenticated stock leaf is a two-byte no-op.  The table/dispatcher
     * owns the callback event identity because this subevent has no payload. */
    (void)message; (void)data; (void)length;
}

void hciEvtParseLeAdvSetTerm(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_ADV_SET_TERM_CBACK_EVT);
    message->leAdvSetTerm.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leAdvSetTerm.status;
    message->leAdvSetTerm.advHandle = open_cfw_hci_evt_u8(&r); message->leAdvSetTerm.handle = open_cfw_hci_evt_u16(&r);
    message->leAdvSetTerm.numComplEvts = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeScanReqRcvd(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_SCAN_REQ_RCVD_CBACK_EVT);
    message->leScanReqRcvd.advHandle = open_cfw_hci_evt_u8(&r); message->leScanReqRcvd.scanAddrType = open_cfw_hci_evt_u8(&r);
    open_cfw_hci_evt_copy(&r, message->leScanReqRcvd.scanAddr, 6u); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLePerAdvSyncEst(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_PER_ADV_SYNC_EST_CBACK_EVT);
    message->lePerAdvSyncEst.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->lePerAdvSyncEst.status;
    message->lePerAdvSyncEst.syncHandle = open_cfw_hci_evt_u16(&r); message->lePerAdvSyncEst.advSid = open_cfw_hci_evt_u8(&r);
    message->lePerAdvSyncEst.advAddrType = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_copy(&r, message->lePerAdvSyncEst.advAddr, 6u);
    message->lePerAdvSyncEst.advPhy = open_cfw_hci_evt_u8(&r); message->lePerAdvSyncEst.perAdvInterval = open_cfw_hci_evt_u16(&r);
    message->lePerAdvSyncEst.clockAccuracy = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_SCAN_ENABLE_CMD_CMPL_CBACK_EVT);
    message->hdr.status = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

OPEN_CFW_STATUS_HANDLE(hciEvtParseLeSetConnCteRcvParm, leSetConnCteRxParamsCmdCmpl, HCI_LE_SET_CONN_CTE_RX_PARAMS_CMD_CMPL_CBACK_EVT)
OPEN_CFW_STATUS_HANDLE(hciEvtParseLeSetConnCteTxParm, leSetConnCteTxParamsCmdCmpl, HCI_LE_SET_CONN_CTE_TX_PARAMS_CMD_CMPL_CBACK_EVT)
OPEN_CFW_STATUS_HANDLE(hciEvtParseLeConnCteReqEn, leConnCteReqEnableCmdCmpl, HCI_LE_CONN_CTE_REQ_ENABLE_CMD_CMPL_CBACK_EVT)
OPEN_CFW_STATUS_HANDLE(hciEvtParseLeConnCteRspEn, leConnCteRspEnableCmdCmpl, HCI_LE_CONN_CTE_RSP_ENABLE_CMD_CMPL_CBACK_EVT)

void hciEvtParseLePerAdvSyncLost(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_PER_ADV_SYNC_LOST_CBACK_EVT);
    message->lePerAdvSyncLost.syncHandle = open_cfw_hci_evt_u16(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeCisEst(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_CIS_EST_CBACK_EVT);
    message->leCisEst.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leCisEst.status;
    message->leCisEst.cisHandle = open_cfw_hci_evt_u16(&r); message->leCisEst.cigSyncDelayUsec = open_cfw_hci_evt_u24(&r);
    message->leCisEst.cisSyncDelayUsec = open_cfw_hci_evt_u24(&r); message->leCisEst.transLatMToSUsec = open_cfw_hci_evt_u24(&r);
    message->leCisEst.transLatSToMUsec = open_cfw_hci_evt_u24(&r); message->leCisEst.phyMToS = open_cfw_hci_evt_u8(&r);
    message->leCisEst.phySToM = open_cfw_hci_evt_u8(&r); message->leCisEst.nse = open_cfw_hci_evt_u8(&r);
    message->leCisEst.bnMToS = open_cfw_hci_evt_u8(&r); message->leCisEst.bnSToM = open_cfw_hci_evt_u8(&r);
    message->leCisEst.ftMToS = open_cfw_hci_evt_u8(&r); message->leCisEst.ftSToM = open_cfw_hci_evt_u8(&r);
    message->leCisEst.maxPduMToS = open_cfw_hci_evt_u16(&r); message->leCisEst.maxPduSToM = open_cfw_hci_evt_u16(&r);
    message->leCisEst.isoInterval = open_cfw_hci_evt_u16(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeCisReq(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_CIS_REQ_CBACK_EVT);
    message->leCisReq.aclHandle = open_cfw_hci_evt_u16(&r); message->leCisReq.cisHandle = open_cfw_hci_evt_u16(&r);
    message->leCisReq.cigId = open_cfw_hci_evt_u8(&r); message->leCisReq.cisId = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeReqPeerScaCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_REQ_PEER_SCA_CBACK_EVT);
    message->leReqPeerSca.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leReqPeerSca.status;
    message->leReqPeerSca.handle = open_cfw_hci_evt_u16(&r); message->leReqPeerSca.peerSca = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeSetCigParamsCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); uint8_t index;
    open_cfw_hci_evt_begin(message, HCI_LE_SET_CIG_PARAMS_CMD_CMPL_CBACK_EVT);
    message->leSetCigParamsCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leSetCigParamsCmdCmpl.status;
    message->leSetCigParamsCmdCmpl.cigId = open_cfw_hci_evt_u8(&r); message->leSetCigParamsCmdCmpl.numCis = open_cfw_hci_evt_u8(&r);
    if (message->leSetCigParamsCmdCmpl.numCis > HCI_MAX_CIS_COUNT) r.failed = 1u;
    for (index = 0u; index < message->leSetCigParamsCmdCmpl.numCis && index < HCI_MAX_CIS_COUNT; ++index)
        message->leSetCigParamsCmdCmpl.cisHandle[index] = open_cfw_hci_evt_u16(&r);
    open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeRemoveCigCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_REMOVE_CIG_CMD_CMPL_CBACK_EVT);
    message->leRemoveCigCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leRemoveCigCmdCmpl.status;
    message->leRemoveCigCmdCmpl.cigId = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeSetupIsoDataPathCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_SETUP_ISO_DATA_PATH_CMD_CMPL_CBACK_EVT);
    message->leSetupIsoDataPathCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leSetupIsoDataPathCmdCmpl.status;
    message->leSetupIsoDataPathCmdCmpl.handle = (uint8_t)open_cfw_hci_evt_u16(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeRemoveIsoDataPathCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_REMOVE_ISO_DATA_PATH_CMD_CMPL_CBACK_EVT);
    message->leRemoveIsoDataPathCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leRemoveIsoDataPathCmdCmpl.status;
    message->leRemoveIsoDataPathCmdCmpl.handle = (uint8_t)open_cfw_hci_evt_u16(&r); open_cfw_hci_evt_finish(message, &r);
}

OPEN_CFW_SIMPLE_STATUS(hciEvtParseConfigDataPathCmdCmpl, configDataPathCmdCmpl, HCI_CONFIG_DATA_PATH_CMD_CMPL_CBACK_EVT)

void hciEvtParseReadLocalSupCodecsCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); uint8_t index;
    open_cfw_hci_evt_begin(message, HCI_READ_LOCAL_SUP_CODECS_CMD_CMPL_CBACK_EVT);
    message->readLocalSupCodecsCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->readLocalSupCodecsCmdCmpl.status;
    message->readLocalSupCodecsCmdCmpl.numStdCodecs = open_cfw_hci_evt_u8(&r);
    if (message->readLocalSupCodecsCmdCmpl.numStdCodecs > HCI_MAX_CODEC) r.failed = 1u;
    for (index = 0u; index < message->readLocalSupCodecsCmdCmpl.numStdCodecs && index < HCI_MAX_CODEC; ++index)
        message->readLocalSupCodecsCmdCmpl.stdCodecs[index].codecId = open_cfw_hci_evt_u8(&r);
    for (index = 0u; index < message->readLocalSupCodecsCmdCmpl.numStdCodecs && index < HCI_MAX_CODEC; ++index)
        message->readLocalSupCodecsCmdCmpl.stdCodecTrans[index] = open_cfw_hci_evt_u8(&r);
    message->readLocalSupCodecsCmdCmpl.numVsCodecs = open_cfw_hci_evt_u8(&r);
    if (message->readLocalSupCodecsCmdCmpl.numVsCodecs > HCI_MAX_CODEC) r.failed = 1u;
    for (index = 0u; index < message->readLocalSupCodecsCmdCmpl.numVsCodecs && index < HCI_MAX_CODEC; ++index) {
        message->readLocalSupCodecsCmdCmpl.vsCodecs[index].compId = open_cfw_hci_evt_u16(&r);
        message->readLocalSupCodecsCmdCmpl.vsCodecs[index].codecId = open_cfw_hci_evt_u16(&r);
    }
    for (index = 0u; index < message->readLocalSupCodecsCmdCmpl.numVsCodecs && index < HCI_MAX_CODEC; ++index)
        message->readLocalSupCodecsCmdCmpl.vsCodecTrans[index] = open_cfw_hci_evt_u8(&r);
    open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseReadLocalSupCodecCapCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); uint8_t index, octet;
    open_cfw_hci_evt_begin(message, HCI_READ_LOCAL_SUP_CODEC_CAP_CMD_CMPL_CBACK_EVT);
    message->readLocalSupCodecCapCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->readLocalSupCodecCapCmdCmpl.status;
    message->readLocalSupCodecCapCmdCmpl.numCodecCaps = open_cfw_hci_evt_u8(&r);
    if (message->readLocalSupCodecCapCmdCmpl.numCodecCaps > HCI_MAX_CODEC) r.failed = 1u;
    for (index = 0u; index < message->readLocalSupCodecCapCmdCmpl.numCodecCaps && index < HCI_MAX_CODEC; ++index) {
        uint8_t count = open_cfw_hci_evt_u8(&r); message->readLocalSupCodecCapCmdCmpl.codecCap[index].len = count;
        if (count > HCI_CODEC_CAP_DATA_LEN) r.failed = 1u;
        for (octet = 0u; octet < count && octet < HCI_CODEC_CAP_DATA_LEN; ++octet)
            message->readLocalSupCodecCapCmdCmpl.codecCap[index].data[octet] = open_cfw_hci_evt_u8(&r);
    }
    open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseReadLocalSupCtrDlyCmdCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_READ_LOCAL_SUP_CTR_DLY_CMD_CMPL_CBACK_EVT);
    message->readLocalSupCtrDlyCmdCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->readLocalSupCtrDlyCmdCmpl.status;
    message->readLocalSupCtrDlyCmdCmpl.minDly = open_cfw_hci_evt_u24(&r); message->readLocalSupCtrDlyCmdCmpl.maxDly = open_cfw_hci_evt_u24(&r);
    open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeCreateBigCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); uint8_t index;
    open_cfw_hci_evt_begin(message, HCI_LE_CREATE_BIG_CMPL_CBACK_EVT);
    message->leCreateBigCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leCreateBigCmpl.status;
    message->leCreateBigCmpl.bigHandle = open_cfw_hci_evt_u8(&r); message->leCreateBigCmpl.syncDelayUsec = open_cfw_hci_evt_u24(&r);
    message->leCreateBigCmpl.transLatUsec = open_cfw_hci_evt_u24(&r); message->leCreateBigCmpl.phy = open_cfw_hci_evt_u8(&r);
    message->leCreateBigCmpl.nse = open_cfw_hci_evt_u8(&r); message->leCreateBigCmpl.bn = open_cfw_hci_evt_u8(&r);
    message->leCreateBigCmpl.pto = open_cfw_hci_evt_u8(&r); message->leCreateBigCmpl.irc = open_cfw_hci_evt_u8(&r);
    message->leCreateBigCmpl.maxPdu = open_cfw_hci_evt_u16(&r); message->leCreateBigCmpl.isoInterval = open_cfw_hci_evt_u16(&r);
    message->leCreateBigCmpl.numBis = open_cfw_hci_evt_u8(&r); if (message->leCreateBigCmpl.numBis > HCI_MAX_BIS_COUNT) r.failed = 1u;
    for (index = 0u; index < message->leCreateBigCmpl.numBis && index < HCI_MAX_BIS_COUNT; ++index)
        message->leCreateBigCmpl.bisHandle[index] = open_cfw_hci_evt_u16(&r);
    open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeTerminateBigCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_TERM_BIG_CMPL_CBACK_EVT);
    message->leTerminateBigCmpl.bigHandle = open_cfw_hci_evt_u8(&r); message->leTerminateBigCmpl.reason = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeBigSyncEst(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); uint8_t index;
    open_cfw_hci_evt_begin(message, HCI_LE_BIG_SYNC_EST_CBACK_EVT);
    message->leBigSyncEst.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leBigSyncEst.status;
    message->leBigSyncEst.bigHandle = open_cfw_hci_evt_u8(&r); message->leBigSyncEst.transLatUsec = open_cfw_hci_evt_u24(&r);
    message->leBigSyncEst.nse = open_cfw_hci_evt_u8(&r); message->leBigSyncEst.bn = open_cfw_hci_evt_u8(&r);
    message->leBigSyncEst.pto = open_cfw_hci_evt_u8(&r); message->leBigSyncEst.irc = open_cfw_hci_evt_u8(&r);
    message->leBigSyncEst.maxPdu = open_cfw_hci_evt_u16(&r); message->leBigSyncEst.isoInterval = open_cfw_hci_evt_u16(&r);
    message->leBigSyncEst.numBis = open_cfw_hci_evt_u8(&r); if (message->leBigSyncEst.numBis > HCI_MAX_BIS_COUNT) r.failed = 1u;
    for (index = 0u; index < message->leBigSyncEst.numBis && index < HCI_MAX_BIS_COUNT; ++index)
        message->leBigSyncEst.bisHandle[index] = open_cfw_hci_evt_u16(&r);
    open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeBigSyncLost(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_BIG_SYNC_LOST_CBACK_EVT);
    message->leBigSyncLost.bigHandle = open_cfw_hci_evt_u8(&r); message->leBigSyncLost.reason = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeBigTermSyncCmpl(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_BIG_TERM_SYNC_CMPL_CBACK_EVT);
    message->leBigTermSyncCmpl.status = open_cfw_hci_evt_u8(&r); message->hdr.status = message->leBigTermSyncCmpl.status;
    message->leBigTermSyncCmpl.bigHandle = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtParseLeBigInfoAdvRpt(hciEvt_t *message, uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); open_cfw_hci_evt_begin(message, HCI_LE_BIG_INFO_ADV_REPORT_CBACK_EVT);
    message->leBigInfoAdvRpt.syncHandle = open_cfw_hci_evt_u16(&r); message->leBigInfoAdvRpt.numBis = open_cfw_hci_evt_u8(&r);
    message->leBigInfoAdvRpt.nse = open_cfw_hci_evt_u8(&r); message->leBigInfoAdvRpt.isoInterv = open_cfw_hci_evt_u16(&r);
    message->leBigInfoAdvRpt.bn = open_cfw_hci_evt_u8(&r); message->leBigInfoAdvRpt.pto = open_cfw_hci_evt_u8(&r);
    message->leBigInfoAdvRpt.irc = open_cfw_hci_evt_u8(&r); message->leBigInfoAdvRpt.maxPdu = open_cfw_hci_evt_u16(&r);
    message->leBigInfoAdvRpt.sduInterv = open_cfw_hci_evt_u24(&r); message->leBigInfoAdvRpt.maxSdu = open_cfw_hci_evt_u16(&r);
    message->leBigInfoAdvRpt.phy = open_cfw_hci_evt_u8(&r); message->leBigInfoAdvRpt.framing = open_cfw_hci_evt_u8(&r);
    message->leBigInfoAdvRpt.encrypt = open_cfw_hci_evt_u8(&r); open_cfw_hci_evt_finish(message, &r);
}

void hciEvtProcessLeAdvReport(uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); uint8_t reports = open_cfw_hci_evt_u8(&r), report;
    for (report = 0u; report < reports && r.failed == 0u; ++report) {
        hciEvt_t message; uint8_t data_length; open_cfw_hci_evt_begin(&message, HCI_LE_ADV_REPORT_CBACK_EVT);
        message.leAdvReport.eventType = open_cfw_hci_evt_u8(&r); message.leAdvReport.addrType = open_cfw_hci_evt_u8(&r);
        open_cfw_hci_evt_copy(&r, message.leAdvReport.addr, 6u); data_length = open_cfw_hci_evt_u8(&r);
        if (r.remaining < (uint8_t)(data_length + 1u)) { r.failed = 1u; break; }
        message.leAdvReport.len = data_length; message.leAdvReport.pData = (uint8_t *)(uintptr_t)r.cursor;
        r.cursor += data_length; r.remaining = (uint8_t)(r.remaining - data_length); message.leAdvReport.rssi = (int8_t)open_cfw_hci_evt_u8(&r);
        open_cfw_hci_evt_finish(&message, &r); open_cfw_hci_evt_deliver(&message);
    }
    if (r.failed != 0u) ++OPEN_CFW_HCI_EVT_STATS->malformed;
}

void hciEvtProcessLeDirectAdvReport(uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); uint8_t reports = open_cfw_hci_evt_u8(&r), report;
    for (report = 0u; report < reports && r.failed == 0u; ++report) {
        hciEvt_t message; open_cfw_hci_evt_begin(&message, HCI_LE_ADV_REPORT_CBACK_EVT);
        message.leAdvReport.eventType = open_cfw_hci_evt_u8(&r); message.leAdvReport.addrType = open_cfw_hci_evt_u8(&r);
        open_cfw_hci_evt_copy(&r, message.leAdvReport.addr, 6u); message.leAdvReport.directAddrType = open_cfw_hci_evt_u8(&r);
        open_cfw_hci_evt_copy(&r, message.leAdvReport.directAddr, 6u); message.leAdvReport.rssi = (int8_t)open_cfw_hci_evt_u8(&r);
        open_cfw_hci_evt_finish(&message, &r); open_cfw_hci_evt_deliver(&message);
    }
    if (r.failed != 0u) ++OPEN_CFW_HCI_EVT_STATS->malformed;
}

void hciEvtProcessLeExtAdvReport(uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); uint8_t reports = open_cfw_hci_evt_u8(&r), report;
    for (report = 0u; report < reports && r.failed == 0u; ++report) {
        hciEvt_t message; uint8_t data_length; open_cfw_hci_evt_begin(&message, HCI_LE_EXT_ADV_REPORT_CBACK_EVT);
        message.leExtAdvReport.eventType = open_cfw_hci_evt_u16(&r); message.leExtAdvReport.addrType = open_cfw_hci_evt_u8(&r);
        open_cfw_hci_evt_copy(&r, message.leExtAdvReport.addr, 6u); message.leExtAdvReport.priPhy = open_cfw_hci_evt_u8(&r);
        message.leExtAdvReport.secPhy = open_cfw_hci_evt_u8(&r); message.leExtAdvReport.advSid = open_cfw_hci_evt_u8(&r);
        message.leExtAdvReport.txPower = (int8_t)open_cfw_hci_evt_u8(&r); message.leExtAdvReport.rssi = (int8_t)open_cfw_hci_evt_u8(&r);
        message.leExtAdvReport.perAdvInter = (int16_t)open_cfw_hci_evt_u16(&r); message.leExtAdvReport.directAddrType = open_cfw_hci_evt_u8(&r);
        open_cfw_hci_evt_copy(&r, message.leExtAdvReport.directAddr, 6u); data_length = open_cfw_hci_evt_u8(&r);
        if (r.remaining < data_length) { r.failed = 1u; break; }
        message.leExtAdvReport.len = data_length; message.leExtAdvReport.pData = (uint8_t *)(uintptr_t)r.cursor;
        r.cursor += data_length; r.remaining = (uint8_t)(r.remaining - data_length);
        open_cfw_hci_evt_finish(&message, &r); open_cfw_hci_evt_deliver(&message);
    }
    if (r.failed != 0u) ++OPEN_CFW_HCI_EVT_STATS->malformed;
}

void hciEvtProcessLePerAdvReport(uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); hciEvt_t message; uint8_t data_length;
    open_cfw_hci_evt_begin(&message, HCI_LE_PER_ADV_REPORT_CBACK_EVT);
    message.lePerAdvReport.syncHandle = open_cfw_hci_evt_u16(&r); message.lePerAdvReport.txPower = open_cfw_hci_evt_u8(&r);
    message.lePerAdvReport.rssi = open_cfw_hci_evt_u8(&r); message.lePerAdvReport.unused = open_cfw_hci_evt_u8(&r);
    message.lePerAdvReport.status = open_cfw_hci_evt_u8(&r); data_length = open_cfw_hci_evt_u8(&r);
    if (r.remaining < data_length) r.failed = 1u; else { message.lePerAdvReport.len = data_length; message.lePerAdvReport.pData = (uint8_t *)(uintptr_t)r.cursor; }
    open_cfw_hci_evt_finish(&message, &r); open_cfw_hci_evt_deliver(&message);
}

void hciEvtProcessLeConnIQReport(uint8_t *data, uint8_t length)
{
    open_cfw_hci_reader_t r = open_cfw_hci_evt_reader(data, length); hciEvt_t message; uint8_t count;
    open_cfw_hci_evt_begin(&message, HCI_LE_CONN_IQ_REPORT_CBACK_EVT);
    message.leConnIQReport.handle = open_cfw_hci_evt_u16(&r); message.leConnIQReport.rxPhy = open_cfw_hci_evt_u8(&r);
    message.leConnIQReport.dataChIdx = open_cfw_hci_evt_u8(&r); message.leConnIQReport.rssi = (int16_t)open_cfw_hci_evt_u16(&r);
    message.leConnIQReport.rssiAntennaId = open_cfw_hci_evt_u8(&r); message.leConnIQReport.cteType = open_cfw_hci_evt_u8(&r);
    message.leConnIQReport.slotDurations = open_cfw_hci_evt_u8(&r); message.leConnIQReport.pktStatus = open_cfw_hci_evt_u8(&r);
    message.leConnIQReport.connEvtCnt = open_cfw_hci_evt_u16(&r); count = open_cfw_hci_evt_u8(&r); message.leConnIQReport.sampleCnt = count;
    if (r.remaining < (uint8_t)(count * 2u) || count > 82u) r.failed = 1u;
    else { message.leConnIQReport.pISample = (int8_t *)(uintptr_t)r.cursor; message.leConnIQReport.pQSample = (int8_t *)(uintptr_t)(r.cursor + count); }
    open_cfw_hci_evt_finish(&message, &r); open_cfw_hci_evt_deliver(&message);
}

void hciEvtProcessLeConlessIQReport(uint8_t *data, uint8_t length)
{
    /* Cordio's public callback ABI has no separate connectionless IQ type in
     * this release.  Decode it through the common bounded IQ representation. */
    hciEvtProcessLeConnIQReport(data, length);
}

static __attribute__((always_inline)) inline uint8_t
open_cfw_hci_evt_opcode_event(uint16_t opcode)
{
    switch (opcode) {
    case 0x200Eu: return HCI_LE_CREATE_CONN_CANCEL_CMD_CMPL_CBACK_EVT;
    case 0x1405u: return HCI_READ_RSSI_CMD_CMPL_CBACK_EVT;
    case 0x2015u: return HCI_LE_READ_CHAN_MAP_CMD_CMPL_CBACK_EVT;
    case 0x0C2Du: return HCI_READ_TX_PWR_LVL_CMD_CMPL_CBACK_EVT;
    case 0x201Au: return HCI_LE_LTK_REQ_REPL_CMD_CMPL_CBACK_EVT;
    case 0x201Bu: return HCI_LE_LTK_REQ_NEG_REPL_CMD_CMPL_CBACK_EVT;
    case 0x2017u: return HCI_LE_ENCRYPT_CMD_CMPL_CBACK_EVT;
    case 0x2018u: return HCI_LE_RAND_CMD_CMPL_CBACK_EVT;
    case 0x2027u: return HCI_LE_ADD_DEV_TO_RES_LIST_CMD_CMPL_CBACK_EVT;
    case 0x2028u: return HCI_LE_REM_DEV_FROM_RES_LIST_CMD_CMPL_CBACK_EVT;
    case 0x2029u: return HCI_LE_CLEAR_RES_LIST_CMD_CMPL_CBACK_EVT;
    case 0x202Bu: return HCI_LE_READ_PEER_RES_ADDR_CMD_CMPL_CBACK_EVT;
    case 0x202Cu: return HCI_LE_READ_LOCAL_RES_ADDR_CMD_CMPL_CBACK_EVT;
    case 0x202Du: return HCI_LE_SET_ADDR_RES_ENABLE_CMD_CMPL_CBACK_EVT;
    case 0x2020u: return HCI_LE_REM_CONN_PARAM_REP_CMD_CMPL_CBACK_EVT;
    case 0x2021u: return HCI_LE_REM_CONN_PARAM_NEG_REP_CMD_CMPL_CBACK_EVT;
    case 0x2023u: return HCI_LE_READ_DEF_DATA_LEN_CMD_CMPL_CBACK_EVT;
    case 0x2024u: return HCI_LE_WRITE_DEF_DATA_LEN_CMD_CMPL_CBACK_EVT;
    case 0x2022u: return HCI_LE_SET_DATA_LEN_CMD_CMPL_CBACK_EVT;
    case 0x202Fu: return HCI_LE_READ_MAX_DATA_LEN_CMD_CMPL_CBACK_EVT;
    case 0x0C7Cu: return HCI_WRITE_AUTH_PAYLOAD_TO_CMD_CMPL_CBACK_EVT;
    case 0x2030u: return HCI_LE_READ_PHY_CMD_CMPL_CBACK_EVT;
    case 0x2031u: return HCI_LE_SET_DEF_PHY_CMD_CMPL_CBACK_EVT;
    case 0x200Cu: return HCI_LE_SCAN_ENABLE_CMD_CMPL_CBACK_EVT;
    case 0x200Au: return HCI_LE_ADV_ENABLE_CMD_CMPL_CBACK_EVT;
    case 0x2042u: return HCI_LE_EXT_SCAN_ENABLE_CMD_CMPL_CBACK_EVT;
    case 0x2039u: return HCI_LE_EXT_ADV_ENABLE_CMD_CMPL_CBACK_EVT;
    case 0x2040u: return HCI_LE_PER_ADV_ENABLE_CMD_CMPL_CBACK_EVT;
    case 0x2005u: return HCI_LE_SET_RAND_ADDR_CMD_CMPL_CBACK_EVT;
    case 0x2054u: return HCI_LE_SET_CONN_CTE_RX_PARAMS_CMD_CMPL_CBACK_EVT;
    case 0x2055u: return HCI_LE_SET_CONN_CTE_TX_PARAMS_CMD_CMPL_CBACK_EVT;
    case 0x2056u: return HCI_LE_CONN_CTE_REQ_ENABLE_CMD_CMPL_CBACK_EVT;
    case 0x2057u: return HCI_LE_CONN_CTE_RSP_ENABLE_CMD_CMPL_CBACK_EVT;
    case 0x2062u: return HCI_LE_SET_CIG_PARAMS_CMD_CMPL_CBACK_EVT;
    case 0x2065u: return HCI_LE_REMOVE_CIG_CMD_CMPL_CBACK_EVT;
    case 0x206Eu: return HCI_LE_SETUP_ISO_DATA_PATH_CMD_CMPL_CBACK_EVT;
    case 0x206Fu: return HCI_LE_REMOVE_ISO_DATA_PATH_CMD_CMPL_CBACK_EVT;
    case 0x0C83u: return HCI_CONFIG_DATA_PATH_CMD_CMPL_CBACK_EVT;
    case 0x100Bu: return HCI_READ_LOCAL_SUP_CODECS_CMD_CMPL_CBACK_EVT;
    case 0x100Du: return HCI_READ_LOCAL_SUP_CODEC_CAP_CMD_CMPL_CBACK_EVT;
    case 0x100Eu: return HCI_READ_LOCAL_SUP_CTR_DLY_CMD_CMPL_CBACK_EVT;
    default: return OPEN_CFW_HCI_INVALID_CALLBACK_EVENT;
    }
}

static __attribute__((always_inline)) inline void
open_cfw_hci_evt_dispatch_parser(uint8_t event, hciEvt_t *message,
                                 uint8_t *data, uint8_t length)
{
    switch (event) {
    case 5: hciEvtParseLeCreateConnCancelCmdCmpl(message,data,length); break;
    case 7: hciEvtParseReadRssiCmdCmpl(message,data,length); break;
    case 8: hciEvtParseReadChanMapCmdCmpl(message,data,length); break;
    case 9: hciEvtParseReadTxPwrLvlCmdCmpl(message,data,length); break;
    case 12: hciEvtParseLeLtkReqReplCmdCmpl(message,data,length); break;
    case 13: hciEvtParseLeLtkReqNegReplCmdCmpl(message,data,length); break;
    case 21: hciEvtParseLeAddDevToResListCmdCmpl(message,data,length); break;
    case 22: hciEvtParseLeRemDevFromResListCmdCmpl(message,data,length); break;
    case 23: hciEvtParseLeClearResListCmdCmpl(message,data,length); break;
    case 24: hciEvtParseLeReadPeerResAddrCmdCmpl(message,data,length); break;
    case 25: hciEvtParseLeReadLocalResAddrCmdCmpl(message,data,length); break;
    case 26: hciEvtParseLeSetAddrResEnableCmdCmpl(message,data,length); break;
    case 27: hciEvtParseLeEncryptCmdCmpl(message,data,length); break;
    case 28: hciEvtParseLeRandCmdCmpl(message,data,length); break;
    case 29: hciEvtParseRemConnParamRepCmdCmpl(message,data,length); break;
    case 30: hciEvtParseRemConnParamNegRepCmdCmpl(message,data,length); break;
    case 31: hciEvtParseReadDefDataLenCmdCmpl(message,data,length); break;
    case 32: hciEvtParseWriteDefDataLenCmdCmpl(message,data,length); break;
    case 33: hciEvtParseSetDataLenCmdCmpl(message,data,length); break;
    case 34: hciEvtParseReadMaxDataLenCmdCmpl(message,data,length); break;
    case 39: hciEvtParseWriteAuthTimeoutCmdCmpl(message,data,length); break;
    case 41: hciEvtParseReadPhyCmdCmpl(message,data,length); break;
    case 42: hciEvtParseSetDefPhyCmdCmpl(message,data,length); break;
    case 52: case 53: case 54: case 55: case 56: case 57:
        hciEvtParseLeCmdCmpl(message,data,length); message->hdr.event = event; break;
    case 63: hciEvtParseLeSetConnCteRcvParm(message,data,length); break;
    case 64: hciEvtParseLeSetConnCteTxParm(message,data,length); break;
    case 65: hciEvtParseLeConnCteReqEn(message,data,length); break;
    case 66: hciEvtParseLeConnCteRspEn(message,data,length); break;
    case 72: hciEvtParseLeSetCigParamsCmdCmpl(message,data,length); break;
    case 73: hciEvtParseLeRemoveCigCmdCmpl(message,data,length); break;
    case 74: hciEvtParseLeSetupIsoDataPathCmdCmpl(message,data,length); break;
    case 75: hciEvtParseLeRemoveIsoDataPathCmdCmpl(message,data,length); break;
    case 76: hciEvtParseConfigDataPathCmdCmpl(message,data,length); break;
    case 77: hciEvtParseReadLocalSupCodecsCmdCmpl(message,data,length); break;
    case 78: hciEvtParseReadLocalSupCodecCapCmdCmpl(message,data,length); break;
    case 79: hciEvtParseReadLocalSupCtrDlyCmdCmpl(message,data,length); break;
    default: open_cfw_hci_evt_begin(message, OPEN_CFW_HCI_INVALID_CALLBACK_EVENT); break;
    }
}

void hciEvtCmdStatusFailure(uint8_t status, uint16_t opcode)
{
    uint8_t event = open_cfw_hci_evt_opcode_event(opcode); hciEvt_t message; uint8_t data[3];
    if (event == OPEN_CFW_HCI_INVALID_CALLBACK_EVENT) return;
    data[0] = status; data[1] = 0u; data[2] = 0u;
    open_cfw_hci_evt_dispatch_parser(event, &message, data, 3u);
    message.hdr.status = status; open_cfw_hci_evt_deliver(&message);
}

void hciEvtProcessCmdStatus(uint8_t *data)
{
    uint8_t status, commands; uint16_t opcode;
    if (data == (uint8_t *)0) { ++OPEN_CFW_HCI_EVT_STATS->malformed; return; }
    status = data[0]; commands = data[1]; opcode = (uint16_t)(data[2] | ((uint16_t)data[3] << 8));
    hciCmdRecvCmpl(commands);
    if (status != 0u) hciEvtCmdStatusFailure(status, opcode);
    else if (opcode >= 0xFC00u) {
        hciEvt_t message; uint8_t encoded[2] = {(uint8_t)opcode, (uint8_t)(opcode >> 8)};
        hciEvtParseVendorSpecCmdStatus(&message, encoded, 2u); open_cfw_hci_evt_deliver(&message);
    }
}

void hciEvtProcessCmdCmpl(uint8_t *data, uint8_t length)
{
    uint8_t commands, event; uint16_t opcode; hciEvt_t message;
    if (data == (uint8_t *)0 || length < 3u) { ++OPEN_CFW_HCI_EVT_STATS->malformed; return; }
    commands = data[0]; opcode = (uint16_t)(data[1] | ((uint16_t)data[2] << 8)); data += 3u; length = (uint8_t)(length - 3u);
    hciCmdRecvCmpl(commands);
    if (opcode >= 0xFC00u) {
        uint8_t encoded[130]; uint8_t index;
        if (length > 127u) { ++OPEN_CFW_HCI_EVT_STATS->malformed; return; }
        encoded[0] = (uint8_t)opcode; encoded[1] = (uint8_t)(opcode >> 8);
        for (index = 0u; index < length; ++index) encoded[index + 2u] = data[index];
        hciEvtParseVendorSpecCmdCmpl(&message, encoded, (uint8_t)(length + 2u)); open_cfw_hci_evt_deliver(&message); return;
    }
    event = open_cfw_hci_evt_opcode_event(opcode);
    if (event != OPEN_CFW_HCI_INVALID_CALLBACK_EVENT) {
        open_cfw_hci_evt_dispatch_parser(event, &message, data, length); open_cfw_hci_evt_deliver(&message);
    }
}

static __attribute__((always_inline)) inline void
open_cfw_hci_evt_process_le(uint8_t *data, uint8_t length)
{
    uint8_t subevent; hciEvt_t message;
    if (length == 0u) { ++OPEN_CFW_HCI_EVT_STATS->malformed; return; }
    subevent = *data++; --length;
    switch (subevent) {
    case 0x01: hciEvtParseLeConnCmpl(&message,data,length); if (message.hdr.status==0u) hciCoreConnOpen(message.leConnCmpl.handle); break;
    case 0x0A: hciEvtParseLeEnhancedConnCmpl(&message,data,length); if (message.hdr.status==0u) hciCoreConnOpen(message.leConnCmpl.handle); break;
    case 0x02: hciEvtProcessLeAdvReport(data,length); return;
    case 0x03: hciEvtParseLeConnUpdateCmpl(&message,data,length); break;
    case 0x04: hciEvtParseReadLeRemoteFeatCmpl(&message,data,length); break;
    case 0x05: hciEvtParseLeLtkReq(&message,data,length); break;
    case 0x06: hciEvtParseRemConnParamReq(&message,data,length); break;
    case 0x07: hciEvtParseDataLenChange(&message,data,length); break;
    case 0x08: hciEvtParseReadPubKeyCmdCmpl(&message,data,length); break;
    case 0x09: hciEvtParseGenDhKeyCmdCmpl(&message,data,length); break;
    case 0x0B: hciEvtProcessLeDirectAdvReport(data,length); return;
    case 0x0C: hciEvtParsePhyUpdateCmpl(&message,data,length); break;
    case 0x0D: hciEvtProcessLeExtAdvReport(data,length); return;
    case 0x0E: hciEvtParseLePerAdvSyncEst(&message,data,length); break;
    case 0x0F: hciEvtProcessLePerAdvReport(data,length); return;
    case 0x10: hciEvtParseLePerAdvSyncLost(&message,data,length); break;
    case 0x11:
        open_cfw_hci_evt_begin(&message, HCI_LE_SCAN_TIMEOUT_CBACK_EVT);
        if (length != 0u) message.hdr.event = OPEN_CFW_HCI_INVALID_CALLBACK_EVENT;
        hciEvtParseLeScanTimeout(&message,data,length); break;
    case 0x12: hciEvtParseLeAdvSetTerm(&message,data,length); break;
    case 0x13: hciEvtParseLeScanReqRcvd(&message,data,length); break;
    case 0x15: hciEvtProcessLeConlessIQReport(data,length); return;
    case 0x16: hciEvtProcessLeConnIQReport(data,length); return;
    case 0x1A: hciEvtParseLeCisEst(&message,data,length); if (message.hdr.status==0u) hciCoreCisOpen(message.leCisEst.cisHandle); break;
    case 0x1B: hciEvtParseLeCisReq(&message,data,length); break;
    case 0x1C: hciEvtParseLeCreateBigCmpl(&message,data,length); break;
    case 0x1D: hciEvtParseLeTerminateBigCmpl(&message,data,length); break;
    case 0x1E: hciEvtParseLeBigSyncEst(&message,data,length); break;
    case 0x1F: hciEvtParseLeBigSyncLost(&message,data,length); break;
    case 0x20: hciEvtParseLeBigInfoAdvRpt(&message,data,length); break;
    case 0x21: hciEvtParseLeReqPeerScaCmpl(&message,data,length); break;
    default: ++OPEN_CFW_HCI_EVT_STATS->unknown; return;
    }
    open_cfw_hci_evt_deliver(&message);
}

void hciEvtProcessMsg(uint8_t *event)
{
    uint8_t code, length; uint8_t *data; hciEvt_t message;
    ++OPEN_CFW_HCI_EVT_STATS->received;
    if (event == (uint8_t *)0) { ++OPEN_CFW_HCI_EVT_STATS->malformed; return; }
    code = event[0]; length = event[1]; data = event + 2u;
    switch (code) {
    case OPEN_CFW_HCI_EVENT_COMMAND_COMPLETE: hciEvtProcessCmdCmpl(data,length); return;
    case OPEN_CFW_HCI_EVENT_COMMAND_STATUS:
        if (length < 4u) { ++OPEN_CFW_HCI_EVT_STATS->malformed; return; } hciEvtProcessCmdStatus(data); return;
    case OPEN_CFW_HCI_EVENT_NUMBER_COMPLETED_PACKETS:
        if (length < 1u || length != (uint8_t)(1u + data[0] * 4u)) { ++OPEN_CFW_HCI_EVT_STATS->malformed; return; }
        hciCoreNumCmplPkts(data); return;
    case OPEN_CFW_HCI_EVENT_LE_META: open_cfw_hci_evt_process_le(data,length); return;
    case OPEN_CFW_HCI_EVENT_DISCONNECT_COMPLETE:
        hciEvtParseDisconnectCmpl(&message,data,length);
        if (message.hdr.event <= HCI_LE_BIG_INFO_ADV_REPORT_CBACK_EVT) {
            if (hciCoreCisByHandle(message.disconnectCmpl.handle) != (void *)0) {
                message.hdr.event = HCI_CIS_DISCONNECT_CMPL_CBACK_EVT; hciCoreCisClose(message.disconnectCmpl.handle);
            } else hciCoreConnClose(message.disconnectCmpl.handle);
        }
        break;
    case OPEN_CFW_HCI_EVENT_ENCRYPTION_CHANGE: hciEvtParseEncChange(&message,data,length); break;
    case OPEN_CFW_HCI_EVENT_READ_REMOTE_VERSION: hciEvtParseReadRemoteVerInfoCmpl(&message,data,length); break;
    case OPEN_CFW_HCI_EVENT_ENCRYPTION_KEY_REFRESH: hciEvtParseEncKeyRefreshCmpl(&message,data,length); break;
    case OPEN_CFW_HCI_EVENT_AUTH_PAYLOAD_TIMEOUT: hciEvtParseAuthTimeoutExpiredEvt(&message,data,length); break;
    case OPEN_CFW_HCI_EVENT_HARDWARE_ERROR:
        hciEvtParseHwError(&message,data,length); break;
    case OPEN_CFW_HCI_EVENT_VENDOR:
        hciEvtParseVendorSpec(&message,data,length); break;
    default: ++OPEN_CFW_HCI_EVT_STATS->unknown; return;
    }
    open_cfw_hci_evt_deliver(&message);
}

open_cfw_hci_evt_stats_t *hciEvtGetStats(void)
{
    return OPEN_CFW_HCI_EVT_STATS;
}

#if defined(OPEN_CFW_HCI_EVT_TEST)
void open_cfw_hci_evt_reset_for_test(void)
{
    OPEN_CFW_HCI_EVT_STATS->received = 0u; OPEN_CFW_HCI_EVT_STATS->delivered = 0u;
    OPEN_CFW_HCI_EVT_STATS->malformed = 0u; OPEN_CFW_HCI_EVT_STATS->unknown = 0u;
    open_cfw_hci_evt_callback_value = (hciEvtCback_t)0;
}
void open_cfw_hci_evt_set_callback_for_test(hciEvtCback_t callback)
{
    open_cfw_hci_evt_callback_value = callback;
}
#endif
