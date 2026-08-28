/*************************************************************************************************/
/* SPDX-License-Identifier: MIT */
/*
 * Clean-room Ambiq Cordio HCI byte transport.
 *
 * This implementation is based on authenticated G2 machine-code behavior
 * and public HCI/WSF interfaces.  No proprietary Cordio source is included.
 */
/*************************************************************************************************/

#include "runtime_cordio_hci_tr.h"

#include <stddef.h>

#define OPEN_CFW_HCI_CMD_TYPE       0x01u
#define OPEN_CFW_HCI_ACL_TYPE       0x02u
#define OPEN_CFW_HCI_EVT_TYPE       0x04u
#define OPEN_CFW_HCI_CMD_HDR_LEN    3u
#define OPEN_CFW_HCI_ACL_HDR_LEN    4u
#define OPEN_CFW_HCI_EVT_HDR_LEN    2u

enum open_cfw_hci_rx_state {
    OPEN_CFW_HCI_RX_PACKET_INDICATOR = 0,
    OPEN_CFW_HCI_RX_HEADER = 1,
    OPEN_CFW_HCI_RX_DATA = 2,
    OPEN_CFW_HCI_RX_COMPLETE = 3
};

extern uint16_t HciDrvWrite(uint8_t type, uint16_t length, const uint8_t *data);
extern uint16_t HciGetMaxRxAclLen(void);
extern void hciCoreRecv(uint8_t type, uint8_t *data);
extern void *WsfMsgDataAlloc(uint16_t length, uint8_t tailroom);
extern void *WsfMsgAlloc(uint16_t length);

#if defined(OPEN_CFW_HCI_TR_PRODUCTION)
#define OPEN_CFW_HCI_TR_PTR(type, address) ((type *)(uintptr_t)(address))
#define OPEN_CFW_HCI_TR_DATA_RX \
    (*OPEN_CFW_HCI_TR_PTR(uint8_t *, 0x20074654u))
#define OPEN_CFW_HCI_TR_I_RX \
    (*OPEN_CFW_HCI_TR_PTR(uint16_t, 0x20074F30u))
#define OPEN_CFW_HCI_TR_RECEIVING \
    (*OPEN_CFW_HCI_TR_PTR(uint8_t, 0x20074FCDu))
#define OPEN_CFW_HCI_TR_PACKET_RX \
    (*OPEN_CFW_HCI_TR_PTR(uint8_t *, 0x20074650u))
#define OPEN_CFW_HCI_TR_PACKET_INDICATOR \
    (*OPEN_CFW_HCI_TR_PTR(uint8_t, 0x20074FCFu))
#define OPEN_CFW_HCI_TR_STATE \
    (*OPEN_CFW_HCI_TR_PTR(uint8_t, 0x20074FCEu))
#define OPEN_CFW_HCI_TR_HEADER \
    OPEN_CFW_HCI_TR_PTR(uint8_t, 0x2007464Cu)
#else
static uint8_t *open_cfw_hci_tr_data_rx;
static uint16_t open_cfw_hci_tr_i_rx;
static uint8_t open_cfw_hci_tr_receiving;
static uint8_t *open_cfw_hci_tr_packet_rx;
static uint8_t open_cfw_hci_tr_packet_indicator;
static uint8_t open_cfw_hci_tr_state;
static uint8_t open_cfw_hci_tr_header[OPEN_CFW_HCI_ACL_HDR_LEN];

#define OPEN_CFW_HCI_TR_DATA_RX open_cfw_hci_tr_data_rx
#define OPEN_CFW_HCI_TR_I_RX open_cfw_hci_tr_i_rx
#define OPEN_CFW_HCI_TR_RECEIVING open_cfw_hci_tr_receiving
#define OPEN_CFW_HCI_TR_PACKET_RX open_cfw_hci_tr_packet_rx
#define OPEN_CFW_HCI_TR_PACKET_INDICATOR open_cfw_hci_tr_packet_indicator
#define OPEN_CFW_HCI_TR_STATE open_cfw_hci_tr_state
#define OPEN_CFW_HCI_TR_HEADER open_cfw_hci_tr_header
#endif

static void open_cfw_hci_tr_reset_receive(void)
{
    OPEN_CFW_HCI_TR_DATA_RX = (uint8_t *)0;
    OPEN_CFW_HCI_TR_I_RX = 0u;
    OPEN_CFW_HCI_TR_RECEIVING = 0u;
    OPEN_CFW_HCI_TR_PACKET_RX = (uint8_t *)0;
    OPEN_CFW_HCI_TR_PACKET_INDICATOR = 0u;
    OPEN_CFW_HCI_TR_STATE = OPEN_CFW_HCI_RX_PACKET_INDICATOR;
}

static uint16_t open_cfw_hci_tr_header_length(uint8_t type)
{
    if (type == OPEN_CFW_HCI_EVT_TYPE) {
        return OPEN_CFW_HCI_EVT_HDR_LEN;
    }
    if (type == OPEN_CFW_HCI_ACL_TYPE) {
        return OPEN_CFW_HCI_ACL_HDR_LEN;
    }
    return 0u;
}

static uint16_t open_cfw_hci_tr_payload_length(void)
{
    if (OPEN_CFW_HCI_TR_PACKET_INDICATOR == OPEN_CFW_HCI_EVT_TYPE) {
        return OPEN_CFW_HCI_TR_HEADER[1];
    }
    return (uint16_t)((uint16_t)OPEN_CFW_HCI_TR_HEADER[2] |
                      ((uint16_t)OPEN_CFW_HCI_TR_HEADER[3] << 8));
}

static bool open_cfw_hci_tr_allocate_packet(uint16_t header_length)
{
    uint16_t payload_length = open_cfw_hci_tr_payload_length();
    uint16_t packet_length;
    uint8_t *packet;
    uint16_t index;

    if (payload_length > (uint16_t)(UINT16_MAX - header_length)) {
        return false;
    }
    packet_length = (uint16_t)(payload_length + header_length);

    if (OPEN_CFW_HCI_TR_PACKET_INDICATOR == OPEN_CFW_HCI_ACL_TYPE) {
        if (payload_length > HciGetMaxRxAclLen()) {
            return false;
        }
        packet = (uint8_t *)WsfMsgDataAlloc(packet_length, 0u);
    } else {
        /* The event length is one byte; retaining this explicit bound keeps
         * the allocation contract self-contained and fail closed. */
        if (payload_length > UINT8_MAX) {
            return false;
        }
        packet = (uint8_t *)WsfMsgAlloc(packet_length);
    }
    if (packet == (uint8_t *)0) {
        return false;
    }

    OPEN_CFW_HCI_TR_PACKET_RX = packet;
    OPEN_CFW_HCI_TR_DATA_RX = packet;
    for (index = 0u; index < header_length; ++index) {
        *OPEN_CFW_HCI_TR_DATA_RX++ = OPEN_CFW_HCI_TR_HEADER[index];
    }
    OPEN_CFW_HCI_TR_I_RX = payload_length;
    OPEN_CFW_HCI_TR_STATE = payload_length == 0u
        ? OPEN_CFW_HCI_RX_COMPLETE : OPEN_CFW_HCI_RX_DATA;
    return true;
}

static void open_cfw_hci_tr_deliver_complete(void)
{
    uint8_t type = OPEN_CFW_HCI_TR_PACKET_INDICATOR;
    uint8_t *packet = OPEN_CFW_HCI_TR_PACKET_RX;

    /* Clear retained ownership before calling upward.  This prevents a
     * reentrant receive or a rejected next packet from reusing queued data. */
    open_cfw_hci_tr_reset_receive();
    if (packet != (uint8_t *)0) {
        hciCoreRecv(type, packet);
    }
}

uint16_t hciTrSendAclData(void *context, const uint8_t *data)
{
    uint16_t length;

    (void)context;
    if (data == (const uint8_t *)0) {
        return 0u;
    }
    length = (uint16_t)((uint16_t)data[2] | ((uint16_t)data[3] << 8));
    if (length > (uint16_t)(UINT16_MAX - OPEN_CFW_HCI_ACL_HDR_LEN)) {
        return 0u;
    }
    length = (uint16_t)(length + OPEN_CFW_HCI_ACL_HDR_LEN);
    return HciDrvWrite(OPEN_CFW_HCI_ACL_TYPE, length, data) == length ? length : 0u;
}

bool hciTrSendCmd(const uint8_t *data)
{
    uint16_t length;

    if (data == (const uint8_t *)0) {
        return false;
    }
    length = (uint16_t)((uint16_t)data[2] + OPEN_CFW_HCI_CMD_HDR_LEN);
    return HciDrvWrite(OPEN_CFW_HCI_CMD_TYPE, length, data) == length;
}

uint16_t hciTrSerialRxIncoming(const uint8_t *data, uint16_t length)
{
    uint16_t consumed = 0u;
    uint16_t original_length = length;

    if (data == (const uint8_t *)0 && length != 0u) {
        open_cfw_hci_tr_reset_receive();
        return original_length;
    }

    while (true) {
        uint16_t header_length;

        if (OPEN_CFW_HCI_TR_STATE == OPEN_CFW_HCI_RX_COMPLETE) {
            open_cfw_hci_tr_deliver_complete();
        }
        if (length == 0u) {
            return consumed;
        }

        if (OPEN_CFW_HCI_TR_STATE == OPEN_CFW_HCI_RX_PACKET_INDICATOR) {
            OPEN_CFW_HCI_TR_PACKET_INDICATOR = *data++;
            OPEN_CFW_HCI_TR_I_RX = 0u;
            OPEN_CFW_HCI_TR_STATE = OPEN_CFW_HCI_RX_HEADER;
            OPEN_CFW_HCI_TR_RECEIVING = 1u;
            --length;
            ++consumed;
            continue;
        }

        if (OPEN_CFW_HCI_TR_STATE == OPEN_CFW_HCI_RX_HEADER) {
            header_length = open_cfw_hci_tr_header_length(
                OPEN_CFW_HCI_TR_PACKET_INDICATOR);
            if (header_length == 0u) {
                open_cfw_hci_tr_reset_receive();
                return original_length;
            }
            OPEN_CFW_HCI_TR_HEADER[OPEN_CFW_HCI_TR_I_RX++] = *data++;
            --length;
            ++consumed;
            if (OPEN_CFW_HCI_TR_I_RX == header_length &&
                !open_cfw_hci_tr_allocate_packet(header_length)) {
                open_cfw_hci_tr_reset_receive();
                return original_length;
            }
            continue;
        }

        if (OPEN_CFW_HCI_TR_STATE == OPEN_CFW_HCI_RX_DATA) {
            *OPEN_CFW_HCI_TR_DATA_RX++ = *data++;
            --OPEN_CFW_HCI_TR_I_RX;
            --length;
            ++consumed;
            if (OPEN_CFW_HCI_TR_I_RX == 0u) {
                OPEN_CFW_HCI_TR_STATE = OPEN_CFW_HCI_RX_COMPLETE;
            }
            continue;
        }

        /* A corrupted retained state must never index the header or packet. */
        open_cfw_hci_tr_reset_receive();
        return original_length;
    }
}

bool hciTrReceivingPacket(void)
{
    return OPEN_CFW_HCI_TR_RECEIVING != 0u;
}

#if defined(OPEN_CFW_HCI_TR_TEST)
void open_cfw_hci_tr_reset_for_test(void)
{
    open_cfw_hci_tr_reset_receive();
}
#endif
