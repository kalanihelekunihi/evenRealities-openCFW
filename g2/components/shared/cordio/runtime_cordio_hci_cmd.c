/*************************************************************************************************/
/* Clean-room Cordio HCI command queue, timeout, and reset core for the authenticated G2 ABI. */
/*************************************************************************************************/

#include "runtime_cordio_hci_cmd.h"

#include <stddef.h>

#define CMD_TIMER 0u
#define CMD_QUEUE 0x10u
#define CMD_OPCODE 0x18u
#define CMD_CREDIT 0x1au
#define HCI_HANDLER_ID 0x20u
#define HCI_CMD_TIMEOUT_EVENT 1u
#define HCI_RESET_NOTICE_EVENT 0x14u
#define HCI_RESET_OPCODE 0x0c03u

extern void *WsfMsgAlloc(uint16_t length);
extern void WsfMsgFree(void *message);
extern void WsfMsgEnq(void *queue, uint8_t handler_id, void *message);
extern void *WsfMsgDeq(void *queue, uint8_t *handler_id);
extern void *WsfMsgPeek(void *queue, uint8_t *handler_id);
extern void WsfTimerStartSec(void *timer, uint32_t seconds);
extern void WsfTimerStop(void *timer);
extern uint16_t hciTrSendCmd(const uint8_t *command);
extern void HciDrvShutdown(void);
extern void HciDrvRadioBoot(uint8_t cold_boot);
extern void DmDevReset(void);

#if defined(OPEN_CFW_HCI_CMD_PRODUCTION)
#define CMD ((uint8_t *)(uintptr_t)0x20073a90u)
#define HCI_CB ((uint8_t *)(uintptr_t)0x20073870u)
#else
static uint8_t open_cfw_cmd[0x1cu];
static void (*open_cfw_hci_callback)(void *event);
#define CMD open_cfw_cmd
#endif

static __attribute__((always_inline)) inline uint16_t get16(const uint8_t *data)
{
    return (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}

static __attribute__((always_inline)) inline void put16(uint8_t *data, uint16_t value)
{
    data[0] = (uint8_t)value; data[1] = (uint8_t)(value >> 8);
}

static void (*hci_callback(void))(void *)
{
#if defined(OPEN_CFW_HCI_CMD_PRODUCTION)
    return *(void (**)(void *))(void *)(HCI_CB + 0x0cu);
#else
    return open_cfw_hci_callback;
#endif
}

uint8_t *hciCmdAlloc(uint16_t opcode, uint16_t length)
{
    uint8_t *command;
    if (length > 255u) return (uint8_t *)0;
    command = (uint8_t *)WsfMsgAlloc((uint16_t)(length + 3u));
    if (command != (uint8_t *)0) {
        put16(command, opcode); command[2] = (uint8_t)length;
    }
    return command;
}

bool hciCmdSend(uint8_t *command)
{
    uint8_t handler_id;
    uint8_t *front;
    if (command != (uint8_t *)0) WsfMsgEnq(CMD + CMD_QUEUE, 0u, command);
    if (CMD[CMD_CREDIT] == 0u) return false;
    front = (uint8_t *)WsfMsgPeek(CMD + CMD_QUEUE, &handler_id);
    if (front == (uint8_t *)0) return false;
    put16(CMD + CMD_OPCODE, get16(front));
    WsfTimerStartSec(CMD + CMD_TIMER, 10u);
    if (hciTrSendCmd(front) != 1u) return false;
    front = (uint8_t *)WsfMsgDeq(CMD + CMD_QUEUE, &handler_id);
    if (front == (uint8_t *)0) return false;
    --CMD[CMD_CREDIT];
    WsfMsgFree(front);
    return true;
}

void hciCmdInit(void)
{
    uint8_t index;
    for (index = 0u; index < 0x1cu; ++index) CMD[index] = 0u;
    CMD[2] = HCI_CMD_TIMEOUT_EVENT;
#if defined(OPEN_CFW_HCI_CMD_PRODUCTION)
    CMD[3] = HCI_CB[HCI_HANDLER_ID];
#endif
    CMD[CMD_CREDIT] = 1u;
}

void hciCmdTimeout(void *message)
{
    (void)message;
    HciDrvShutdown();
    HciDrvRadioBoot(0u);
    DmDevReset();
}

void hciCmdRecvCmpl(uint8_t num_commands)
{
    (void)num_commands;
    WsfTimerStop(CMD + CMD_TIMER);
    CMD[CMD_CREDIT] = 1u;
    (void)hciCmdSend((uint8_t *)0);
}

void hciClearCmdQueue(void)
{
    uint8_t handler_id;
    uint8_t *message;
    while ((message = (uint8_t *)WsfMsgDeq(CMD + CMD_QUEUE, &handler_id)) != (uint8_t *)0) {
        WsfMsgFree(message);
    }
    CMD[CMD_CREDIT] = 1u;
}

void HciResetCmd(void)
{
    uint8_t event[4] = {0u, 0u, HCI_RESET_NOTICE_EVENT, 0u};
    uint8_t *command;
    void (*callback)(void *) = hci_callback();
    if (callback != (void (*)(void *))0) callback(event);
    hciClearCmdQueue();
    command = hciCmdAlloc(HCI_RESET_OPCODE, 0u);
    if (command != (uint8_t *)0) (void)hciCmdSend(command);
}

#define HCI_OPCODE_VALUE(ogf, ocf) ((uint16_t)(((uint16_t)(ogf) << 10) | (ocf)))
#define HCI_LINK_OPCODE(ocf) HCI_OPCODE_VALUE(0x01u, (ocf))
#define HCI_CONTROLLER_OPCODE(ocf) HCI_OPCODE_VALUE(0x03u, (ocf))
#define HCI_INFO_OPCODE(ocf) HCI_OPCODE_VALUE(0x04u, (ocf))
#define HCI_STATUS_OPCODE(ocf) HCI_OPCODE_VALUE(0x05u, (ocf))
#define HCI_LE_OPCODE(ocf) HCI_OPCODE_VALUE(0x08u, (ocf))

static __attribute__((always_inline)) inline uint8_t *command_begin(
    uint16_t opcode, uint8_t length)
{
    uint8_t *command = hciCmdAlloc(opcode, length);
    return command == (uint8_t *)0 ? command : command + 3u;
}

static __attribute__((always_inline)) inline void stream8(uint8_t **cursor,
                                                           uint8_t value)
{
    *(*cursor)++ = value;
}

static __attribute__((always_inline)) inline void stream16(uint8_t **cursor,
                                                            uint16_t value)
{
    stream8(cursor, (uint8_t)value);
    stream8(cursor, (uint8_t)(value >> 8));
}

static __attribute__((always_inline)) inline void stream_bytes(
    uint8_t **cursor, const uint8_t *source, uint8_t length)
{
    uint8_t index;
    for (index = 0u; index < length; ++index) stream8(cursor, source[index]);
}

static __attribute__((always_inline)) inline void stream_zeros(uint8_t **cursor,
                                                                uint8_t length)
{
    uint8_t index;
    for (index = 0u; index < length; ++index) stream8(cursor, 0u);
}

static __attribute__((always_inline)) inline void command_finish(uint8_t *params)
{
    if (params != (uint8_t *)0) (void)hciCmdSend(params - 3u);
}

static __attribute__((always_inline)) inline void command_empty(uint16_t opcode)
{
    command_finish(command_begin(opcode, 0u));
}

void HciDisconnectCmd(uint16_t handle, uint8_t reason)
{
    uint8_t *p = command_begin(HCI_LINK_OPCODE(0x06u), 3u);
    if (p == (uint8_t *)0) return;
    stream16(&p, handle); stream8(&p, reason); command_finish(p - 3u);
}

static __attribute__((always_inline)) inline void white_list_command(
    uint16_t opcode, uint8_t address_type, const uint8_t *address)
{
    uint8_t *p;
    if (address == (const uint8_t *)0) return;
    p = command_begin(opcode, 7u);
    if (p == (uint8_t *)0) return;
    stream8(&p, address_type); stream_bytes(&p, address, 6u);
    command_finish(p - 7u);
}

void HciLeAddDevWhiteListCmd(uint8_t address_type, uint8_t *address)
{ white_list_command(HCI_LE_OPCODE(0x11u), address_type, address); }

void HciLeClearWhiteListCmd(void) { command_empty(HCI_LE_OPCODE(0x10u)); }

static __attribute__((always_inline)) inline void stream_connection_spec(
    uint8_t **p, const open_cfw_hci_conn_spec_t *spec)
{
    stream16(p, spec->conn_interval_min);
    stream16(p, spec->conn_interval_max);
    stream16(p, spec->conn_latency);
    stream16(p, spec->supervision_timeout);
    stream16(p, spec->min_ce_length);
    stream16(p, spec->max_ce_length);
}

void HciLeConnUpdateCmd(uint16_t handle, open_cfw_hci_conn_spec_t *spec)
{
    uint8_t *p;
    if (spec == (open_cfw_hci_conn_spec_t *)0) return;
    p = command_begin(HCI_LE_OPCODE(0x13u), 14u);
    if (p == (uint8_t *)0) return;
    stream16(&p, handle); stream_connection_spec(&p, spec); command_finish(p - 14u);
}

void HciLeCreateConnCmd(uint16_t scan_interval, uint16_t scan_window,
                        uint8_t filter_policy, uint8_t peer_address_type,
                        uint8_t *peer_address, uint8_t own_address_type,
                        open_cfw_hci_conn_spec_t *spec)
{
    uint8_t *p;
    if (peer_address == (uint8_t *)0 || spec == (open_cfw_hci_conn_spec_t *)0) return;
    p = command_begin(HCI_LE_OPCODE(0x0du), 25u);
    if (p == (uint8_t *)0) return;
    stream16(&p, scan_interval); stream16(&p, scan_window);
    stream8(&p, filter_policy); stream8(&p, peer_address_type);
    stream_bytes(&p, peer_address, 6u); stream8(&p, own_address_type);
    stream_connection_spec(&p, spec); command_finish(p - 25u);
}

void HciLeCreateConnCancelCmd(void) { command_empty(HCI_LE_OPCODE(0x0eu)); }

void HciLeRemoteConnParamReqReply(uint16_t handle, uint16_t interval_min,
                                  uint16_t interval_max, uint16_t latency,
                                  uint16_t timeout, uint16_t min_ce_length,
                                  uint16_t max_ce_length)
{
    uint8_t *p = command_begin(HCI_LE_OPCODE(0x20u), 14u);
    if (p == (uint8_t *)0) return;
    stream16(&p, handle); stream16(&p, interval_min); stream16(&p, interval_max);
    stream16(&p, latency); stream16(&p, timeout); stream16(&p, min_ce_length);
    stream16(&p, max_ce_length); command_finish(p - 14u);
}

void HciLeRemoteConnParamReqNegReply(uint16_t handle, uint8_t reason)
{
    uint8_t *p = command_begin(HCI_LE_OPCODE(0x21u), 3u);
    if (p == (uint8_t *)0) return;
    stream16(&p, handle); stream8(&p, reason); command_finish(p - 3u);
}

void HciLeSetDataLen(uint16_t handle, uint16_t tx_octets, uint16_t tx_time)
{
    uint8_t *p = command_begin(HCI_LE_OPCODE(0x22u), 6u);
    if (p == (uint8_t *)0) return;
    stream16(&p, handle); stream16(&p, tx_octets); stream16(&p, tx_time);
    command_finish(p - 6u);
}

void HciLeReadDefDataLen(void) { command_empty(HCI_LE_OPCODE(0x23u)); }

void HciLeWriteDefDataLen(uint16_t max_tx_octets, uint16_t max_tx_time)
{
    uint8_t *p = command_begin(HCI_LE_OPCODE(0x24u), 4u);
    if (p == (uint8_t *)0) return;
    stream16(&p, max_tx_octets); stream16(&p, max_tx_time); command_finish(p - 4u);
}

void HciLeReadLocalP256PubKey(void) { command_empty(HCI_LE_OPCODE(0x25u)); }

void HciLeGenerateDHKey(uint8_t *public_key_x, uint8_t *public_key_y)
{
    uint8_t *p;
    if (public_key_x == (uint8_t *)0 || public_key_y == (uint8_t *)0) return;
    p = command_begin(HCI_LE_OPCODE(0x26u), 64u);
    if (p == (uint8_t *)0) return;
    stream_bytes(&p, public_key_x, 32u); stream_bytes(&p, public_key_y, 32u);
    command_finish(p - 64u);
}

void HciLeReadMaxDataLen(void) { command_empty(HCI_LE_OPCODE(0x2fu)); }

void HciLeEncryptCmd(uint8_t *key, uint8_t *data)
{
    uint8_t *p;
    if (key == (uint8_t *)0 || data == (uint8_t *)0) return;
    p = command_begin(HCI_LE_OPCODE(0x17u), 32u);
    if (p == (uint8_t *)0) return;
    stream_bytes(&p, key, 16u); stream_bytes(&p, data, 16u);
    command_finish(p - 32u);
}

void HciLeLtkReqNegReplCmd(uint16_t handle)
{
    uint8_t *p = command_begin(HCI_LE_OPCODE(0x1bu), 2u);
    if (p == (uint8_t *)0) return;
    stream16(&p, handle); command_finish(p - 2u);
}

void HciLeLtkReqReplCmd(uint16_t handle, uint8_t *key)
{
    uint8_t *p;
    if (key == (uint8_t *)0) return;
    p = command_begin(HCI_LE_OPCODE(0x1au), 18u);
    if (p == (uint8_t *)0) return;
    stream16(&p, handle); stream_bytes(&p, key, 16u); command_finish(p - 18u);
}

void HciLeRandCmd(void) { command_empty(HCI_LE_OPCODE(0x18u)); }
void HciLeReadAdvTXPowerCmd(void) { command_empty(HCI_LE_OPCODE(0x07u)); }
void HciLeReadBufSizeCmd(void) { command_empty(HCI_LE_OPCODE(0x02u)); }

static __attribute__((always_inline)) inline void command_handle(uint16_t opcode,
                                                                 uint16_t handle)
{
    uint8_t *p = command_begin(opcode, 2u);
    if (p == (uint8_t *)0) return;
    stream16(&p, handle); command_finish(p - 2u);
}

void HciLeReadChanMapCmd(uint16_t handle) { command_handle(HCI_LE_OPCODE(0x15u), handle); }
void HciLeReadLocalSupFeatCmd(void) { command_empty(HCI_LE_OPCODE(0x03u)); }
void HciLeReadRemoteFeatCmd(uint16_t handle) { command_handle(HCI_LE_OPCODE(0x16u), handle); }
void HciLeReadSupStatesCmd(void) { command_empty(HCI_LE_OPCODE(0x1cu)); }
void HciLeReadWhiteListSizeCmd(void) { command_empty(HCI_LE_OPCODE(0x0fu)); }
void HciLeRemoveDevWhiteListCmd(uint8_t address_type, uint8_t *address)
{ white_list_command(HCI_LE_OPCODE(0x12u), address_type, address); }

void HciLeSetAdvEnableCmd(uint8_t enable)
{
    uint8_t *p = command_begin(HCI_LE_OPCODE(0x0au), 1u);
    if (p == (uint8_t *)0) return;
    stream8(&p, enable); command_finish(p - 1u);
}

static __attribute__((always_inline)) inline void advertising_data_command(
    uint16_t opcode, uint8_t length, const uint8_t *data)
{
    uint8_t *p;
    if (length > 31u || (length != 0u && data == (const uint8_t *)0)) return;
    p = command_begin(opcode, 32u);
    if (p == (uint8_t *)0) return;
    stream8(&p, length);
    if (length != 0u) stream_bytes(&p, data, length);
    stream_zeros(&p, (uint8_t)(31u - length)); command_finish(p - 32u);
}

void HciLeSetAdvDataCmd(uint8_t length, uint8_t *data)
{ advertising_data_command(HCI_LE_OPCODE(0x08u), length, data); }

void HciLeSetAdvParamCmd(uint16_t interval_min, uint16_t interval_max,
                         uint8_t advertising_type, uint8_t own_address_type,
                         uint8_t peer_address_type, uint8_t *peer_address,
                         uint8_t channel_map, uint8_t filter_policy)
{
    uint8_t *p = command_begin(HCI_LE_OPCODE(0x06u), 15u);
    if (p == (uint8_t *)0) return;
    stream16(&p, interval_min); stream16(&p, interval_max);
    stream8(&p, advertising_type); stream8(&p, own_address_type);
    stream8(&p, peer_address_type);
    if (peer_address != (uint8_t *)0) stream_bytes(&p, peer_address, 6u);
    else stream_zeros(&p, 6u);
    stream8(&p, channel_map); stream8(&p, filter_policy); command_finish(p - 15u);
}

static __attribute__((always_inline)) inline void event_mask_command(
    uint16_t opcode, const uint8_t *event_mask)
{
    uint8_t *p;
    if (event_mask == (const uint8_t *)0) return;
    p = command_begin(opcode, 8u);
    if (p == (uint8_t *)0) return;
    stream_bytes(&p, event_mask, 8u); command_finish(p - 8u);
}

void HciLeSetEventMaskCmd(uint8_t *event_mask)
{ event_mask_command(HCI_LE_OPCODE(0x01u), event_mask); }

void HciLeSetHostChanClassCmd(uint8_t *channel_map)
{
    uint8_t *p;
    if (channel_map == (uint8_t *)0) return;
    p = command_begin(HCI_LE_OPCODE(0x14u), 5u);
    if (p == (uint8_t *)0) return;
    stream_bytes(&p, channel_map, 5u); command_finish(p - 5u);
}

void HciLeSetRandAddrCmd(uint8_t *address)
{
    uint8_t *p;
    if (address == (uint8_t *)0) return;
    p = command_begin(HCI_LE_OPCODE(0x05u), 6u);
    if (p == (uint8_t *)0) return;
    stream_bytes(&p, address, 6u); command_finish(p - 6u);
}

void HciLeSetScanEnableCmd(uint8_t enable, uint8_t filter_duplicates)
{
    uint8_t *p = command_begin(HCI_LE_OPCODE(0x0cu), 2u);
    if (p == (uint8_t *)0) return;
    stream8(&p, enable); stream8(&p, filter_duplicates); command_finish(p - 2u);
}

void HciLeSetScanParamCmd(uint8_t scan_type, uint16_t scan_interval,
                          uint16_t scan_window, uint8_t own_address_type,
                          uint8_t filter_policy)
{
    uint8_t *p = command_begin(HCI_LE_OPCODE(0x0bu), 7u);
    if (p == (uint8_t *)0) return;
    stream8(&p, scan_type); stream16(&p, scan_interval); stream16(&p, scan_window);
    stream8(&p, own_address_type); stream8(&p, filter_policy); command_finish(p - 7u);
}

void HciLeSetScanRespDataCmd(uint8_t length, uint8_t *data)
{ advertising_data_command(HCI_LE_OPCODE(0x09u), length, data); }

void HciLeStartEncryptionCmd(uint16_t handle, uint8_t *random,
                             uint16_t diversifier, uint8_t *key)
{
    uint8_t *p;
    if (random == (uint8_t *)0 || key == (uint8_t *)0) return;
    p = command_begin(HCI_LE_OPCODE(0x19u), 28u);
    if (p == (uint8_t *)0) return;
    stream16(&p, handle); stream_bytes(&p, random, 8u); stream16(&p, diversifier);
    stream_bytes(&p, key, 16u); command_finish(p - 28u);
}

void HciReadBdAddrCmd(void) { command_empty(HCI_INFO_OPCODE(0x09u)); }
void HciReadBufSizeCmd(void) { command_empty(HCI_INFO_OPCODE(0x05u)); }
void HciReadLocalSupFeatCmd(void) { command_empty(HCI_INFO_OPCODE(0x03u)); }
void HciReadLocalVerInfoCmd(void) { command_empty(HCI_INFO_OPCODE(0x01u)); }
void HciReadRemoteVerInfoCmd(uint16_t handle)
{ command_handle(HCI_LINK_OPCODE(0x1du), handle); }
void HciReadRssiCmd(uint16_t handle) { command_handle(HCI_STATUS_OPCODE(0x05u), handle); }

void HciReadTxPwrLvlCmd(uint16_t handle, uint8_t type)
{
    uint8_t *p = command_begin(HCI_CONTROLLER_OPCODE(0x2du), 3u);
    if (p == (uint8_t *)0) return;
    stream16(&p, handle); stream8(&p, type); command_finish(p - 3u);
}

void HciSetEventMaskCmd(uint8_t *event_mask)
{ event_mask_command(HCI_CONTROLLER_OPCODE(0x01u), event_mask); }
void HciSetEventMaskPage2Cmd(uint8_t *event_mask)
{ event_mask_command(HCI_CONTROLLER_OPCODE(0x63u), event_mask); }
void HciReadAuthPayloadTimeout(uint16_t handle)
{ command_handle(HCI_CONTROLLER_OPCODE(0x7bu), handle); }

void HciWriteAuthPayloadTimeout(uint16_t handle, uint16_t timeout)
{
    uint8_t *p = command_begin(HCI_CONTROLLER_OPCODE(0x7cu), 4u);
    if (p == (uint8_t *)0) return;
    stream16(&p, handle); stream16(&p, timeout); command_finish(p - 4u);
}

void HciLeAddDeviceToResolvingListCmd(uint8_t peer_address_type,
                                      const uint8_t *peer_identity_address,
                                      const uint8_t *peer_irk,
                                      const uint8_t *local_irk)
{
    uint8_t *p;
    if (peer_identity_address == (const uint8_t *)0 ||
        peer_irk == (const uint8_t *)0 || local_irk == (const uint8_t *)0) return;
    p = command_begin(HCI_LE_OPCODE(0x27u), 39u);
    if (p == (uint8_t *)0) return;
    stream8(&p, peer_address_type); stream_bytes(&p, peer_identity_address, 6u);
    stream_bytes(&p, peer_irk, 16u); stream_bytes(&p, local_irk, 16u);
    command_finish(p - 39u);
}

static __attribute__((always_inline)) inline void resolving_address_command(
    uint16_t opcode, uint8_t address_type, const uint8_t *identity_address)
{
    uint8_t *p;
    if (identity_address == (const uint8_t *)0) return;
    p = command_begin(opcode, 7u);
    if (p == (uint8_t *)0) return;
    stream8(&p, address_type); stream_bytes(&p, identity_address, 6u);
    command_finish(p - 7u);
}

void HciLeRemoveDeviceFromResolvingList(uint8_t peer_address_type,
                                        const uint8_t *peer_identity_address)
{ resolving_address_command(HCI_LE_OPCODE(0x28u), peer_address_type, peer_identity_address); }
void HciLeClearResolvingList(void) { command_empty(HCI_LE_OPCODE(0x29u)); }
void HciLeReadResolvingListSize(void) { command_empty(HCI_LE_OPCODE(0x2au)); }
void HciLeReadPeerResolvableAddr(uint8_t address_type, const uint8_t *identity_address)
{ resolving_address_command(HCI_LE_OPCODE(0x2bu), address_type, identity_address); }
void HciLeReadLocalResolvableAddr(uint8_t address_type, const uint8_t *identity_address)
{ resolving_address_command(HCI_LE_OPCODE(0x2cu), address_type, identity_address); }

void HciLeSetAddrResolutionEnable(uint8_t enable)
{
    uint8_t *p = command_begin(HCI_LE_OPCODE(0x2du), 1u);
    if (p == (uint8_t *)0) return;
    stream8(&p, enable); command_finish(p - 1u);
}

void HciLeSetResolvablePrivateAddrTimeout(uint16_t timeout)
{ command_handle(HCI_LE_OPCODE(0x2eu), timeout); }

void HciLeSetPrivacyModeCmd(uint8_t address_type, uint8_t *address, uint8_t mode)
{
    uint8_t *p;
    if (address == (uint8_t *)0) return;
    p = command_begin(HCI_LE_OPCODE(0x4eu), 8u);
    if (p == (uint8_t *)0) return;
    stream8(&p, address_type); stream_bytes(&p, address, 6u); stream8(&p, mode);
    command_finish(p - 8u);
}

void HciLeReceiverTestCmd(uint8_t channel)
{
    uint8_t *p = command_begin(HCI_LE_OPCODE(0x1du), 1u);
    if (p == (uint8_t *)0) return;
    stream8(&p, channel); command_finish(p - 1u);
}

void HciLeTransmitterTestCmd(uint8_t channel, uint8_t data_length,
                             uint8_t packet_payload)
{
    uint8_t *p = command_begin(HCI_LE_OPCODE(0x1eu), 3u);
    if (p == (uint8_t *)0) return;
    stream8(&p, channel); stream8(&p, data_length); stream8(&p, packet_payload);
    command_finish(p - 3u);
}

void HciLeTestEndCmd(void) { command_empty(HCI_LE_OPCODE(0x1fu)); }

void HciLeReceiverTestCmdV3(open_cfw_hci_rx_test_v3_t *parameters)
{
    uint8_t *p;
    if (parameters == (open_cfw_hci_rx_test_v3_t *)0 ||
        parameters->switching_pattern_length > OPEN_CFW_HCI_MAX_SWITCHING_PATTERN_LEN) return;
    p = command_begin(HCI_LE_OPCODE(0x4fu), 82u);
    if (p == (uint8_t *)0) return;
    stream8(&p, parameters->rx_channel); stream8(&p, parameters->phy);
    stream8(&p, parameters->modulation_index); stream8(&p, parameters->expected_cte_length);
    stream8(&p, parameters->expected_cte_type); stream8(&p, parameters->slot_duration);
    stream8(&p, parameters->switching_pattern_length);
    stream_bytes(&p, parameters->antenna_id, OPEN_CFW_HCI_MAX_SWITCHING_PATTERN_LEN);
    command_finish(p - 82u);
}

void HciLeTransmitterTestCmdV3(open_cfw_hci_tx_test_v3_t *parameters)
{
    uint8_t *p;
    if (parameters == (open_cfw_hci_tx_test_v3_t *)0 ||
        parameters->switching_pattern_length > OPEN_CFW_HCI_MAX_SWITCHING_PATTERN_LEN) return;
    p = command_begin(HCI_LE_OPCODE(0x50u), 82u);
    if (p == (uint8_t *)0) return;
    stream8(&p, parameters->tx_channel); stream8(&p, parameters->test_data_length);
    stream8(&p, parameters->packet_payload); stream8(&p, parameters->phy);
    stream8(&p, parameters->cte_length); stream8(&p, parameters->cte_type);
    stream8(&p, parameters->switching_pattern_length);
    stream_bytes(&p, parameters->antenna_id, OPEN_CFW_HCI_MAX_SWITCHING_PATTERN_LEN);
    command_finish(p - 82u);
}

void HciVendorSpecificCmd(uint16_t opcode, uint8_t length, uint8_t *data)
{
    uint8_t *p;
    if (length != 0u && data == (uint8_t *)0) return;
    p = command_begin(opcode, length);
    if (p == (uint8_t *)0) return;
    if (length != 0u) stream_bytes(&p, data, length);
    command_finish(p - length);
}

void HciLeRequestPeerScaCmd(uint16_t handle)
{ command_handle(HCI_LE_OPCODE(0x6du), handle); }
void HciLeReadBufSizeCmdV2(void) { command_empty(HCI_LE_OPCODE(0x60u)); }

void HciLeSetHostFeatureCmd(uint8_t bit_number, bool bit_value)
{
    uint8_t *p = command_begin(HCI_LE_OPCODE(0x74u), 2u);
    if (p == (uint8_t *)0) return;
    stream8(&p, bit_number); stream8(&p, bit_value ? 1u : 0u);
    command_finish(p - 2u);
}

#if defined(OPEN_CFW_HCI_CMD_TEST)
void open_cfw_hci_cmd_reset_for_test(void)
{
    uint8_t index; for (index = 0u; index < sizeof(open_cfw_cmd); ++index) CMD[index] = 0u;
    open_cfw_hci_callback = (void (*)(void *))0;
}
uint8_t *open_cfw_hci_cmd_state_for_test(void) { return CMD; }
void open_cfw_hci_cmd_set_callback_for_test(void (*callback)(void *))
{ open_cfw_hci_callback = callback; }
#endif
