/*************************************************************************************************/
/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Packetcraft Apache-2.0 dual-chip HCI platform behavior adapted to the
 * authenticated G2 control-block ABI.  Ambiq proprietary source is not used.
 */
/*************************************************************************************************/

#include "runtime_cordio_hci_core_ps.h"

#include <stddef.h>

#define OPEN_CFW_HCI_EVT_TYPE            0x04u
#define OPEN_CFW_HCI_ACL_TYPE            0x02u
#define OPEN_CFW_HCI_ISO_TYPE            0x05u
#define OPEN_CFW_HCI_EVENT_RX             0x01u
#define OPEN_CFW_HCI_MSG_CMD_TIMEOUT      0x01u

#define OPEN_CFW_CORE_LE_STATES           0x60u
#define OPEN_CFW_CORE_BD_ADDR             0x68u
#define OPEN_CFW_CORE_MAX_RX_ACL_LEN      0x7Cu
#define OPEN_CFW_CORE_BUF_SIZE            0x7Eu
#define OPEN_CFW_CORE_ACL_QUEUE_LO        0x81u
#define OPEN_CFW_CORE_NUM_BUFS            0x83u
#define OPEN_CFW_CORE_WHITE_LIST_SIZE     0x84u
#define OPEN_CFW_CORE_LE_FEATURES         0x88u
#define OPEN_CFW_CORE_ADV_TX_POWER        0x90u
#define OPEN_CFW_CORE_RES_LIST_SIZE       0x91u
#define OPEN_CFW_CORE_MAX_ADV_DATA_LEN    0x92u
#define OPEN_CFW_CORE_NUM_ADV_SETS        0x94u
#define OPEN_CFW_CORE_PER_ADV_LIST_SIZE   0x95u
#define OPEN_CFW_CORE_LOCAL_VERSION       0x96u
#define OPEN_CFW_CORE_BYTES               0xA4u

#define OPEN_CFW_HCI_RX_QUEUE             0x00u
#define OPEN_CFW_HCI_EVENT_CALLBACK       0x08u
#define OPEN_CFW_HCI_ACL_CALLBACK         0x10u
#define OPEN_CFW_HCI_FLOW_CALLBACK        0x14u
#define OPEN_CFW_HCI_ISO_CALLBACK         0x18u
#define OPEN_CFW_HCI_HANDLER_ID           0x20u
#define OPEN_CFW_HCI_RESETTING            0x21u
#define OPEN_CFW_HCI_BYTES                0x24u

#define OPEN_CFW_CONN_FLOW_DISABLED       0x17u
#define OPEN_CFW_CONN_QUEUED_BUFS         0x18u
#define OPEN_CFW_CONN_OUT_BUFS            0x19u

extern void hciCmdInit(void);
extern void *hciCoreConnByHandle(uint16_t handle);
extern void hciCoreTxReady(uint8_t buffers);
extern void hciCmdTimeout(void *message);
extern void hciEvtProcessMsg(uint8_t *message);
extern void hciCoreResetSequence(uint8_t *message);
extern uint8_t *hciCoreAclReassembly(uint8_t *message);
extern void WsfMsgEnq(void *queue, uint8_t handler_id, void *message);
extern void *WsfMsgDeq(void *queue, uint8_t *handler_id);
extern void WsfMsgFree(void *message);
extern void WsfSetEvent(uint8_t handler_id, uint8_t event);

#if defined(OPEN_CFW_HCI_CORE_PS_PRODUCTION)
#define OPEN_CFW_HCI_CORE ((uint8_t *)(uintptr_t)0x20071478u)
#define OPEN_CFW_HCI_CB ((uint8_t *)(uintptr_t)0x20073870u)
#else
static uint8_t open_cfw_hci_core_storage[OPEN_CFW_CORE_BYTES];
static uint8_t open_cfw_hci_cb_storage[OPEN_CFW_HCI_BYTES];
static open_cfw_hci_acl_callback_t open_cfw_hci_acl_callback_storage;
static open_cfw_hci_flow_callback_t open_cfw_hci_flow_callback_storage;
static open_cfw_hci_iso_callback_t open_cfw_hci_iso_callback_storage;
#define OPEN_CFW_HCI_CORE open_cfw_hci_core_storage
#define OPEN_CFW_HCI_CB open_cfw_hci_cb_storage
#endif

static uint16_t open_cfw_read_u16(const uint8_t *data)
{
    return (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}

static uint64_t open_cfw_read_u64(const uint8_t *data)
{
    uint64_t value = 0u;
    uint8_t index;
    for (index = 0u; index < 8u; ++index) {
        value |= (uint64_t)data[index] << (8u * index);
    }
    return value;
}

static open_cfw_hci_acl_callback_t open_cfw_hci_acl_callback(void)
{
#if defined(OPEN_CFW_HCI_CORE_PS_PRODUCTION)
    return *(open_cfw_hci_acl_callback_t *)(void *)(OPEN_CFW_HCI_CB + OPEN_CFW_HCI_ACL_CALLBACK);
#else
    return open_cfw_hci_acl_callback_storage;
#endif
}

static open_cfw_hci_flow_callback_t open_cfw_hci_flow_callback(void)
{
#if defined(OPEN_CFW_HCI_CORE_PS_PRODUCTION)
    return *(open_cfw_hci_flow_callback_t *)(void *)(OPEN_CFW_HCI_CB + OPEN_CFW_HCI_FLOW_CALLBACK);
#else
    return open_cfw_hci_flow_callback_storage;
#endif
}

static open_cfw_hci_iso_callback_t open_cfw_hci_iso_callback(void)
{
#if defined(OPEN_CFW_HCI_CORE_PS_PRODUCTION)
    return *(open_cfw_hci_iso_callback_t *)(void *)(OPEN_CFW_HCI_CB + OPEN_CFW_HCI_ISO_CALLBACK);
#else
    return open_cfw_hci_iso_callback_storage;
#endif
}

void hciCoreInit(void)
{
    hciCmdInit();
}

void hciCoreNumCmplPkts(uint8_t *message)
{
    uint8_t handles;
    uint8_t available = 0u;

    if (message == (uint8_t *)0) {
        return;
    }
    handles = *message++;
    while (handles-- != 0u) {
        uint16_t handle = open_cfw_read_u16(message);
        uint16_t claimed = open_cfw_read_u16(message + 2u);
        uint8_t *connection;
        uint8_t completed;
        message += 4u;

        connection = (uint8_t *)hciCoreConnByHandle(handle);
        if (connection == (uint8_t *)0) {
            continue;
        }
        completed = claimed > UINT8_MAX ? UINT8_MAX : (uint8_t)claimed;
        if (completed > connection[OPEN_CFW_CONN_OUT_BUFS]) {
            completed = connection[OPEN_CFW_CONN_OUT_BUFS];
        }
        if (completed > connection[OPEN_CFW_CONN_QUEUED_BUFS]) {
            completed = connection[OPEN_CFW_CONN_QUEUED_BUFS];
        }
        connection[OPEN_CFW_CONN_OUT_BUFS] -= completed;
        connection[OPEN_CFW_CONN_QUEUED_BUFS] -= completed;
        available = (uint8_t)(available + completed);

        if (connection[OPEN_CFW_CONN_FLOW_DISABLED] != 0u &&
            connection[OPEN_CFW_CONN_QUEUED_BUFS] <=
                OPEN_CFW_HCI_CORE[OPEN_CFW_CORE_ACL_QUEUE_LO]) {
            open_cfw_hci_flow_callback_t callback = open_cfw_hci_flow_callback();
            connection[OPEN_CFW_CONN_FLOW_DISABLED] = 0u;
            if (callback != (open_cfw_hci_flow_callback_t)0) {
                callback(handle, false);
            }
        }
    }
    hciCoreTxReady(available);
}

void hciCoreRecv(uint8_t message_type, uint8_t *message)
{
    if (message == (uint8_t *)0 ||
        (message_type != OPEN_CFW_HCI_EVT_TYPE &&
         message_type != OPEN_CFW_HCI_ACL_TYPE &&
         message_type != OPEN_CFW_HCI_ISO_TYPE)) {
        if (message != (uint8_t *)0) {
            WsfMsgFree(message);
        }
        return;
    }
    WsfMsgEnq(OPEN_CFW_HCI_CB + OPEN_CFW_HCI_RX_QUEUE, message_type, message);
    WsfSetEvent(OPEN_CFW_HCI_CB[OPEN_CFW_HCI_HANDLER_ID], OPEN_CFW_HCI_EVENT_RX);
}

void HciCoreHandler(uint8_t event, void *message)
{
    uint8_t *buffer;
    uint8_t handler_id;

    if (message != (void *)0) {
        const uint8_t *header = (const uint8_t *)message;
        if (header[2] == OPEN_CFW_HCI_MSG_CMD_TIMEOUT) {
            hciCmdTimeout(message);
        }
        return;
    }
    if ((event & OPEN_CFW_HCI_EVENT_RX) == 0u) {
        return;
    }

    while ((buffer = (uint8_t *)WsfMsgDeq(
                OPEN_CFW_HCI_CB + OPEN_CFW_HCI_RX_QUEUE, &handler_id)) != (uint8_t *)0) {
        if (handler_id == OPEN_CFW_HCI_EVT_TYPE) {
            hciEvtProcessMsg(buffer);
            if (OPEN_CFW_HCI_CB[OPEN_CFW_HCI_RESETTING] != 0u) {
                hciCoreResetSequence(buffer);
            }
            WsfMsgFree(buffer);
        } else if (handler_id == OPEN_CFW_HCI_ACL_TYPE) {
            open_cfw_hci_acl_callback_t callback;
            buffer = hciCoreAclReassembly(buffer);
            callback = open_cfw_hci_acl_callback();
            if (buffer != (uint8_t *)0) {
                if (callback != (open_cfw_hci_acl_callback_t)0) {
                    callback(buffer);
                } else {
                    WsfMsgFree(buffer);
                }
            }
        } else if (handler_id == OPEN_CFW_HCI_ISO_TYPE) {
            open_cfw_hci_iso_callback_t callback = open_cfw_hci_iso_callback();
            if (callback != (open_cfw_hci_iso_callback_t)0) {
                callback(buffer);
            } else {
                WsfMsgFree(buffer);
            }
        } else {
            WsfMsgFree(buffer);
        }
    }
}

uint8_t *HciGetBdAddr(void) { return OPEN_CFW_HCI_CORE + OPEN_CFW_CORE_BD_ADDR; }
uint8_t HciGetWhiteListSize(void) { return OPEN_CFW_HCI_CORE[OPEN_CFW_CORE_WHITE_LIST_SIZE]; }
int8_t HciGetAdvTxPwr(void) { return (int8_t)OPEN_CFW_HCI_CORE[OPEN_CFW_CORE_ADV_TX_POWER]; }
uint16_t HciGetBufSize(void) { return open_cfw_read_u16(OPEN_CFW_HCI_CORE + OPEN_CFW_CORE_BUF_SIZE); }
uint8_t HciGetNumBufs(void) { return OPEN_CFW_HCI_CORE[OPEN_CFW_CORE_NUM_BUFS]; }
uint8_t *HciGetSupStates(void) { return OPEN_CFW_HCI_CORE + OPEN_CFW_CORE_LE_STATES; }
uint64_t HciGetLeSupFeat(void)
{
    /* Match G2: do not advertise unsupported connection-parameter request. */
    return open_cfw_read_u64(OPEN_CFW_HCI_CORE + OPEN_CFW_CORE_LE_FEATURES) & ~UINT64_C(2);
}
uint32_t HciGetLeSupFeat32(void) { return (uint32_t)HciGetLeSupFeat(); }
uint16_t HciGetMaxRxAclLen(void)
{
    return open_cfw_read_u16(OPEN_CFW_HCI_CORE + OPEN_CFW_CORE_MAX_RX_ACL_LEN);
}
uint8_t HciGetResolvingListSize(void) { return OPEN_CFW_HCI_CORE[OPEN_CFW_CORE_RES_LIST_SIZE]; }
bool HciLlPrivacySupported(void) { return HciGetResolvingListSize() != 0u; }
uint16_t HciGetMaxAdvDataLen(void)
{
    return open_cfw_read_u16(OPEN_CFW_HCI_CORE + OPEN_CFW_CORE_MAX_ADV_DATA_LEN);
}
uint8_t HciGetNumSupAdvSets(void) { return OPEN_CFW_HCI_CORE[OPEN_CFW_CORE_NUM_ADV_SETS]; }
bool HciLeAdvExtSupported(void) { return HciGetNumSupAdvSets() != 0u; }
uint8_t HciGetPerAdvListSize(void) { return OPEN_CFW_HCI_CORE[OPEN_CFW_CORE_PER_ADV_LIST_SIZE]; }
void *HciGetLocalVerInfo(void) { return OPEN_CFW_HCI_CORE + OPEN_CFW_CORE_LOCAL_VERSION; }

#if defined(OPEN_CFW_HCI_CORE_PS_TEST)
void open_cfw_hci_core_ps_reset_for_test(void)
{
    uint16_t index;
    for (index = 0u; index < OPEN_CFW_CORE_BYTES; ++index) {
        OPEN_CFW_HCI_CORE[index] = 0u;
    }
    for (index = 0u; index < OPEN_CFW_HCI_BYTES; ++index) {
        OPEN_CFW_HCI_CB[index] = 0u;
    }
    open_cfw_hci_acl_callback_storage = (open_cfw_hci_acl_callback_t)0;
    open_cfw_hci_flow_callback_storage = (open_cfw_hci_flow_callback_t)0;
    open_cfw_hci_iso_callback_storage = (open_cfw_hci_iso_callback_t)0;
}
void open_cfw_hci_core_ps_set_core_u8_for_test(uint16_t offset, uint8_t value)
{
    if (offset < OPEN_CFW_CORE_BYTES) OPEN_CFW_HCI_CORE[offset] = value;
}
void open_cfw_hci_core_ps_set_core_u16_for_test(uint16_t offset, uint16_t value)
{
    if (offset + 1u < OPEN_CFW_CORE_BYTES) {
        OPEN_CFW_HCI_CORE[offset] = (uint8_t)value;
        OPEN_CFW_HCI_CORE[offset + 1u] = (uint8_t)(value >> 8);
    }
}
void open_cfw_hci_core_ps_set_core_u64_for_test(uint16_t offset, uint64_t value)
{
    uint8_t index;
    if (offset + 7u < OPEN_CFW_CORE_BYTES) {
        for (index = 0u; index < 8u; ++index) {
            OPEN_CFW_HCI_CORE[offset + index] = (uint8_t)(value >> (8u * index));
        }
    }
}
void open_cfw_hci_core_ps_set_callbacks_for_test(
    open_cfw_hci_acl_callback_t acl,
    open_cfw_hci_flow_callback_t flow,
    open_cfw_hci_iso_callback_t iso)
{
    open_cfw_hci_acl_callback_storage = acl;
    open_cfw_hci_flow_callback_storage = flow;
    open_cfw_hci_iso_callback_storage = iso;
}
void open_cfw_hci_core_ps_set_handler_for_test(uint8_t handler_id, bool resetting)
{
    OPEN_CFW_HCI_CB[OPEN_CFW_HCI_HANDLER_ID] = handler_id;
    OPEN_CFW_HCI_CB[OPEN_CFW_HCI_RESETTING] = resetting ? 1u : 0u;
}
#endif
