/*************************************************************************************************/
/* Packetcraft Apache-2.0 common HCI core adapted to the authenticated G2 ABI. */
/*************************************************************************************************/

#include "runtime_cordio_hci_core.h"

#include <stddef.h>

#define CONN_COUNT 3u
#define CIS_COUNT 6u
#define HANDLE_NONE 0xffffu
#define HANDLE_MASK 0x0fffu
#define PB_MASK 0x3000u
#define PB_START 0x2000u
#define PB_CONTINUE 0x1000u
#define ACL_HEADER 4u
#define L2C_HEADER 4u
#define CORE_QUEUE 0x70u
#define CORE_MAX_RX 0x7cu
#define CORE_BUF_SIZE 0x7eu
#define CORE_QUEUE_HI 0x80u
#define CORE_QUEUE_LO 0x81u
#define CORE_AVAIL 0x82u
#define CORE_NUM_BUFS 0x83u
#define CORE_EXT_RESET 0xa0u
#define HCI_FLOW_CALLBACK 0x14u
#define HCI_RESETTING 0x21u

typedef struct {
    uint8_t *tx_packet;
    uint8_t *next_tx;
    uint8_t *rx_packet;
    uint8_t *next_rx;
    uint16_t handle;
    uint16_t tx_remaining;
    uint16_t rx_remaining;
    uint8_t fragmenting;
    uint8_t flow_disabled;
    uint8_t queued;
    uint8_t outstanding;
} open_cfw_hci_conn_t;

extern uint16_t hciTrSendAclData(void *connection, const uint8_t *data);
extern uint16_t HciGetBufSize(void);
extern void hciCoreInit(void);
extern void hciCoreResetStart(void);
extern void WsfMsgEnq(void *queue, uint8_t handler_id, void *message);
extern void *WsfMsgDeq(void *queue, uint8_t *handler_id);
extern void WsfMsgFree(void *message);
extern void *WsfMsgDataAlloc(uint16_t length, uint8_t tailroom);

#if defined(OPEN_CFW_HCI_CORE_PRODUCTION)
_Static_assert(sizeof(open_cfw_hci_conn_t) == 28u, "G2 HCI connection ABI");
#define CORE ((uint8_t *)(uintptr_t)0x20071478u)
#define CONNECTIONS ((open_cfw_hci_conn_t *)(void *)CORE)
#define CIS ((uint16_t *)(void *)(CORE + 0x54u))
#define HCI_CB ((uint8_t *)(uintptr_t)0x20073870u)
#define FEATURE_CONFIG (*(uint64_t *)(uintptr_t)0x20000028u)
#else
static uint8_t open_cfw_core_bytes[0xa4];
static open_cfw_hci_conn_t open_cfw_connections[CONN_COUNT];
static uint16_t open_cfw_cis[CIS_COUNT];
static uint64_t open_cfw_feature_config;
static void (*open_cfw_flow_callback_storage)(uint16_t, bool);
static bool open_cfw_queue_empty_storage = true;
#define CORE open_cfw_core_bytes
#define CONNECTIONS open_cfw_connections
#define CIS open_cfw_cis
#define FEATURE_CONFIG open_cfw_feature_config
#endif

static uint16_t get16(const uint8_t *data)
{
    return (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}

static void put16(uint8_t *data, uint16_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
}

static void copy_bytes(uint8_t *destination, const uint8_t *source, uint16_t length)
{
    while (length-- != 0u) *destination++ = *source++;
}

static uint16_t core16(uint16_t offset) { return get16(CORE + offset); }
static void set_core16(uint16_t offset, uint16_t value) { put16(CORE + offset, value); }

static void (*flow_callback(void))(uint16_t, bool)
{
#if defined(OPEN_CFW_HCI_CORE_PRODUCTION)
    return *(void (**)(uint16_t, bool))(void *)(HCI_CB + HCI_FLOW_CALLBACK);
#else
    return open_cfw_flow_callback_storage;
#endif
}

static bool queue_empty(void)
{
#if defined(OPEN_CFW_HCI_CORE_PRODUCTION)
    return *(const uint32_t *)(const void *)(CORE + CORE_QUEUE) == 0u;
#else
    return open_cfw_queue_empty_storage;
#endif
}

void hciCoreConnAlloc(uint16_t handle)
{
    uint8_t index;
    for (index = 0u; index < CONN_COUNT; ++index) {
        open_cfw_hci_conn_t *connection = &CONNECTIONS[index];
        if (connection->handle == HANDLE_NONE) {
            connection->handle = handle;
            connection->flow_disabled = 0u;
            connection->queued = 0u;
            connection->outstanding = 0u;
            return;
        }
    }
}

void *hciCoreConnByHandle(uint16_t handle)
{
    uint8_t index;
    handle &= HANDLE_MASK;
    for (index = 0u; index < CONN_COUNT; ++index) {
        if (CONNECTIONS[index].handle == handle) return &CONNECTIONS[index];
    }
    return (void *)0;
}

void hciCoreConnFree(uint16_t handle)
{
    open_cfw_hci_conn_t *connection = hciCoreConnByHandle(handle);
    if (connection == (open_cfw_hci_conn_t *)0) return;
    if (connection->tx_packet != (uint8_t *)0) WsfMsgFree(connection->tx_packet);
    if (connection->rx_packet != (uint8_t *)0) WsfMsgFree(connection->rx_packet);
    connection->tx_packet = connection->next_tx = (uint8_t *)0;
    connection->rx_packet = connection->next_rx = (uint8_t *)0;
    connection->fragmenting = 0u;
    connection->handle = HANDLE_NONE;
    (void)hciCoreTxReady(connection->outstanding);
    connection->outstanding = connection->queued = 0u;
}

void hciCoreConnOpen(uint16_t handle) { hciCoreConnAlloc(handle & HANDLE_MASK); }
void hciCoreConnClose(uint16_t handle) { hciCoreConnFree(handle); }

void *hciCoreNextConnFragment(void)
{
    uint8_t index;
    for (index = 0u; index < CONN_COUNT; ++index) {
        if (CONNECTIONS[index].handle != HANDLE_NONE && CONNECTIONS[index].fragmenting)
            return &CONNECTIONS[index];
    }
    return (open_cfw_hci_conn_t *)0;
}

bool hciCoreSendAclData(void *context, uint8_t *data)
{
    open_cfw_hci_conn_t *connection = context;
    if (connection == (open_cfw_hci_conn_t *)0 || data == (uint8_t *)0) return false;
    if (hciTrSendAclData(connection, data) == 0u) return false;
    if (connection->outstanding != UINT8_MAX) ++connection->outstanding;
    if (CORE[CORE_AVAIL] != 0u) --CORE[CORE_AVAIL];
    return true;
}

bool hciCoreTxAclStart(void *context, uint16_t length, uint8_t *data)
{
    open_cfw_hci_conn_t *connection = context;
    uint16_t controller_length = HciGetBufSize();
    if (connection == (open_cfw_hci_conn_t *)0 || data == (uint8_t *)0 || controller_length == 0u)
        return false;
    if (connection->fragmenting) return false;
    if (length <= controller_length) return hciCoreSendAclData(connection, data);

    connection->tx_remaining = (uint16_t)(length - controller_length);
    connection->next_tx = data + controller_length;
    connection->tx_packet = data;
    connection->fragmenting = 1u;
    put16(data + 2u, controller_length);
    if (!hciCoreSendAclData(connection, data)) {
        connection->tx_packet = connection->next_tx = (uint8_t *)0;
        connection->fragmenting = 0u;
        put16(data + 2u, length);
        return false;
    }
    return true;
}

bool hciCoreTxAclContinue(void *context)
{
    open_cfw_hci_conn_t *connection = context;
    uint16_t controller_length;
    uint16_t fragment;
    uint8_t *sent;
    if (connection == (open_cfw_hci_conn_t *)0) connection = hciCoreNextConnFragment();
    if (connection == (open_cfw_hci_conn_t *)0 || connection->tx_remaining == 0u) return false;
    controller_length = HciGetBufSize();
    if (controller_length == 0u) return false;
    fragment = connection->tx_remaining < controller_length
        ? connection->tx_remaining : controller_length;
    sent = connection->next_tx;
    put16(sent, (uint16_t)(connection->handle | PB_CONTINUE));
    put16(sent + 2u, fragment);
    if (!hciCoreSendAclData(connection, sent)) return false;
    connection->tx_remaining = (uint16_t)(connection->tx_remaining - fragment);
    if (connection->tx_remaining != 0u) connection->next_tx += fragment;
    hciCoreTxAclComplete(connection, sent);
    return true;
}

void hciCoreTxAclComplete(void *context, uint8_t *data)
{
    open_cfw_hci_conn_t *connection = context;
    if (connection == (open_cfw_hci_conn_t *)0) return;
    if (connection->fragmenting) {
        if (connection->tx_remaining == 0u) {
            WsfMsgFree(connection->tx_packet);
            connection->tx_packet = connection->next_tx = (uint8_t *)0;
            connection->fragmenting = 0u;
        }
    } else if (data != (uint8_t *)0) {
        WsfMsgFree(data);
    }
}

bool hciCoreTxReady(uint8_t buffers)
{
    bool sent_any = false;
    uint8_t handler;
    if (buffers != 0u) {
        uint16_t available = (uint16_t)CORE[CORE_AVAIL] + buffers;
        CORE[CORE_AVAIL] = available > CORE[CORE_NUM_BUFS]
            ? CORE[CORE_NUM_BUFS] : (uint8_t)available;
    }
    while (CORE[CORE_AVAIL] != 0u) {
        uint8_t *data;
        open_cfw_hci_conn_t *connection;
        uint16_t handle;
        uint16_t length;
        if (hciCoreTxAclContinue((void *)0)) { sent_any = true; continue; }
        data = WsfMsgDeq(CORE + CORE_QUEUE, &handler);
        if (data == (uint8_t *)0) break;
#if !defined(OPEN_CFW_HCI_CORE_PRODUCTION)
        open_cfw_queue_empty_storage = true;
#endif
        handle = get16(data) & HANDLE_MASK;
        length = get16(data + 2u);
        connection = hciCoreConnByHandle(handle);
        if (connection == (open_cfw_hci_conn_t *)0 ||
            !hciCoreTxAclStart(connection, length, data)) {
            if (connection == (open_cfw_hci_conn_t *)0) WsfMsgFree(data);
            break;
        }
        hciCoreTxAclComplete(connection, data);
        sent_any = true;
    }
    return sent_any;
}

uint8_t *hciCoreAclReassembly(uint8_t *data)
{
    open_cfw_hci_conn_t *connection;
    uint16_t raw_handle, handle, flags, acl_length, expected, accumulated;
    uint8_t *result = (uint8_t *)0;
    bool free_input = true;
    if (data == (uint8_t *)0) return (uint8_t *)0;
    raw_handle = get16(data); handle = raw_handle & HANDLE_MASK; flags = raw_handle & PB_MASK;
    acl_length = get16(data + 2u); connection = hciCoreConnByHandle(handle);
    if (connection == (open_cfw_hci_conn_t *)0) goto done;

    if (flags == PB_START) {
        if (connection->rx_packet != (uint8_t *)0) WsfMsgFree(connection->rx_packet);
        connection->rx_packet = connection->next_rx = (uint8_t *)0;
        if (acl_length >= L2C_HEADER) {
            expected = (uint16_t)(get16(data + ACL_HEADER) + L2C_HEADER);
            if (expected > core16(CORE_MAX_RX) || expected < acl_length) goto done;
            if (expected == acl_length) { result = data; free_input = false; goto done; }
            connection->rx_packet = WsfMsgDataAlloc((uint16_t)(expected + ACL_HEADER), 0u);
            connection->rx_remaining = (uint16_t)(expected - acl_length);
        } else {
            if (core16(CORE_MAX_RX) < L2C_HEADER) goto done;
            connection->rx_packet = WsfMsgDataAlloc((uint16_t)(core16(CORE_MAX_RX) + ACL_HEADER), 0u);
            connection->rx_remaining = UINT16_MAX;
        }
        if (connection->rx_packet == (uint8_t *)0) goto done;
        put16(connection->rx_packet, handle);
        put16(connection->rx_packet + 2u,
              connection->rx_remaining == UINT16_MAX ? 0u : expected);
        copy_bytes(connection->rx_packet + ACL_HEADER, data + ACL_HEADER, acl_length);
        connection->next_rx = connection->rx_packet + ACL_HEADER + acl_length;
    } else if (flags == PB_CONTINUE && connection->rx_packet != (uint8_t *)0) {
        accumulated = (uint16_t)(connection->next_rx - connection->rx_packet - ACL_HEADER);
        if (connection->rx_remaining == UINT16_MAX) {
            if ((uint32_t)accumulated + acl_length > core16(CORE_MAX_RX)) goto reject_rx;
            copy_bytes(connection->next_rx, data + ACL_HEADER, acl_length);
            connection->next_rx += acl_length; accumulated = (uint16_t)(accumulated + acl_length);
            if (accumulated < L2C_HEADER) goto done;
            expected = (uint16_t)(get16(connection->rx_packet + ACL_HEADER) + L2C_HEADER);
            if (expected > core16(CORE_MAX_RX) || expected < accumulated) goto reject_rx;
            put16(connection->rx_packet + 2u, expected);
            connection->rx_remaining = (uint16_t)(expected - accumulated);
        } else {
            if (acl_length > connection->rx_remaining) goto reject_rx;
            copy_bytes(connection->next_rx, data + ACL_HEADER, acl_length);
            connection->next_rx += acl_length;
            connection->rx_remaining = (uint16_t)(connection->rx_remaining - acl_length);
        }
        if (connection->rx_remaining == 0u) {
            result = connection->rx_packet; connection->rx_packet = connection->next_rx = (uint8_t *)0;
        }
    }
    goto done;
reject_rx:
    WsfMsgFree(connection->rx_packet); connection->rx_packet = connection->next_rx = (uint8_t *)0;
done:
    if (free_input) WsfMsgFree(data);
    return result;
}

bool hciCoreTxAclDataFragmented(void *context)
{
    return context != (void *)0 && ((open_cfw_hci_conn_t *)context)->fragmenting != 0u;
}

void HciCoreInit(void)
{
    uint8_t index;
    for (index = 0u; index < CONN_COUNT; ++index) {
        CONNECTIONS[index].tx_packet = CONNECTIONS[index].next_tx = (uint8_t *)0;
        CONNECTIONS[index].rx_packet = CONNECTIONS[index].next_rx = (uint8_t *)0;
        CONNECTIONS[index].handle = HANDLE_NONE;
        CONNECTIONS[index].fragmenting = CONNECTIONS[index].flow_disabled = 0u;
        CONNECTIONS[index].queued = CONNECTIONS[index].outstanding = 0u;
    }
    for (index = 0u; index < CIS_COUNT; ++index) CIS[index] = HANDLE_NONE;
    *(uint32_t *)(void *)(CORE + CORE_QUEUE) = 0u;
    *(uint32_t *)(void *)(CORE + CORE_QUEUE + 4u) = 0u;
    set_core16(CORE_MAX_RX, 27u); CORE[CORE_QUEUE_HI] = 14u; CORE[CORE_QUEUE_LO] = 13u;
    *(uint32_t *)(void *)(CORE + CORE_EXT_RESET) = 0u;
    hciCoreInit();
}

void HciResetSequence(void)
{
    uint8_t handler;
    uint8_t *message;
    uint8_t returned = 0u;
    uint8_t index;
    while ((message = WsfMsgDeq(CORE + CORE_QUEUE, &handler)) != (uint8_t *)0) {
        WsfMsgFree(message);
    }
    for (index = 0u; index < CONN_COUNT; ++index) {
        open_cfw_hci_conn_t *connection = &CONNECTIONS[index];
        if (connection->tx_packet != (uint8_t *)0) WsfMsgFree(connection->tx_packet);
        if (connection->rx_packet != (uint8_t *)0) WsfMsgFree(connection->rx_packet);
        returned = (uint8_t)(returned + connection->outstanding);
        connection->tx_packet = connection->next_tx = (uint8_t *)0;
        connection->rx_packet = connection->next_rx = (uint8_t *)0;
        connection->handle = HANDLE_NONE;
        connection->tx_remaining = connection->rx_remaining = 0u;
        connection->fragmenting = connection->flow_disabled = 0u;
        connection->queued = connection->outstanding = 0u;
    }
    for (index = 0u; index < CIS_COUNT; ++index) CIS[index] = HANDLE_NONE;
    if (returned != 0u) (void)hciCoreTxReady(returned);
#if defined(OPEN_CFW_HCI_CORE_PRODUCTION)
    HCI_CB[HCI_RESETTING] = 1u;
#endif
    hciCoreResetStart();
}

void HciSetMaxRxAclLen(uint16_t length) { set_core16(CORE_MAX_RX, length < 27u ? 27u : length); }
void HciSetAclQueueWatermarks(uint8_t high, uint8_t low)
{
    if (high == 0u || low > high) return;
    CORE[CORE_QUEUE_HI] = high; CORE[CORE_QUEUE_LO] = low;
}
void HciSetLeSupFeat(uint64_t features, bool enable)
{
    if (enable) FEATURE_CONFIG |= features; else FEATURE_CONFIG &= ~features;
}

void HciSendAclData(uint8_t *data)
{
    open_cfw_hci_conn_t *connection;
    uint16_t handle, length, controller_length, fragments;
    if (data == (uint8_t *)0) return;
    handle = get16(data) & HANDLE_MASK; length = get16(data + 2u);
    connection = hciCoreConnByHandle(handle); controller_length = HciGetBufSize();
    if (connection == (open_cfw_hci_conn_t *)0 || controller_length == 0u) {
        WsfMsgFree(data); return;
    }
    if (queue_empty() && CORE[CORE_AVAIL] != 0u) {
        if (hciCoreTxAclStart(connection, length, data)) hciCoreTxAclComplete(connection, data);
        else { WsfMsgFree(data); return; }
    } else {
        WsfMsgEnq(CORE + CORE_QUEUE, 0u, data);
#if !defined(OPEN_CFW_HCI_CORE_PRODUCTION)
        open_cfw_queue_empty_storage = false;
#endif
    }
    fragments = (uint16_t)(length / controller_length + (length % controller_length != 0u));
    if (fragments == 0u) fragments = 1u;
    connection->queued = fragments > (uint16_t)(UINT8_MAX - connection->queued)
        ? UINT8_MAX : (uint8_t)(connection->queued + fragments);
    if (connection->queued >= CORE[CORE_QUEUE_HI] && !connection->flow_disabled) {
        void (*callback)(uint16_t, bool) = flow_callback();
        connection->flow_disabled = 1u;
        if (callback != (void (*)(uint16_t, bool))0) callback(handle, true);
    }
}

void *hciCoreCisByHandle(uint16_t handle)
{
    uint8_t index;
    for (index = 0u; index < CIS_COUNT; ++index) if (CIS[index] == handle) return &CIS[index];
    return (void *)0;
}
void hciCoreCisAlloc(uint16_t handle)
{
    uint8_t index;
    if (hciCoreCisByHandle(handle) != (void *)0) return;
    for (index = 0u; index < CIS_COUNT; ++index) if (CIS[index] == HANDLE_NONE) { CIS[index] = handle; return; }
}
void hciCoreCisFree(uint16_t handle)
{
    uint16_t *slot = hciCoreCisByHandle(handle); if (slot) *slot = HANDLE_NONE;
}
void hciCoreCisOpen(uint16_t handle) { hciCoreCisAlloc(handle); }
void hciCoreCisClose(uint16_t handle) { hciCoreCisFree(handle); }

#if defined(OPEN_CFW_HCI_CORE_TEST)
void open_cfw_hci_core_reset_for_test(void)
{
    uint16_t index; for (index = 0u; index < sizeof(open_cfw_core_bytes); ++index) CORE[index] = 0u;
    open_cfw_flow_callback_storage = (void (*)(uint16_t, bool))0; open_cfw_queue_empty_storage = true;
    for (index = 0u; index < CONN_COUNT; ++index) CONNECTIONS[index].handle = HANDLE_NONE;
    for (index = 0u; index < CIS_COUNT; ++index) CIS[index] = HANDLE_NONE;
}
void open_cfw_hci_core_set_controller_for_test(uint16_t buffer_size, uint8_t buffers)
{ set_core16(CORE_BUF_SIZE, buffer_size); CORE[CORE_NUM_BUFS] = CORE[CORE_AVAIL] = buffers; }
void open_cfw_hci_core_set_flow_callback_for_test(void (*callback)(uint16_t, bool))
{ open_cfw_flow_callback_storage = callback; }
void open_cfw_hci_core_set_queue_empty_for_test(bool empty) { open_cfw_queue_empty_storage = empty; }
#endif
