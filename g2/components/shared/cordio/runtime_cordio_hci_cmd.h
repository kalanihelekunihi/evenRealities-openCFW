#ifndef OPEN_CFW_RUNTIME_CORDIO_HCI_CMD_H
#define OPEN_CFW_RUNTIME_CORDIO_HCI_CMD_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    uint16_t conn_interval_min;
    uint16_t conn_interval_max;
    uint16_t conn_latency;
    uint16_t supervision_timeout;
    uint16_t min_ce_length;
    uint16_t max_ce_length;
} open_cfw_hci_conn_spec_t;

#define OPEN_CFW_HCI_MAX_SWITCHING_PATTERN_LEN 75u
typedef struct {
    uint8_t rx_channel;
    uint8_t phy;
    uint8_t modulation_index;
    uint8_t expected_cte_length;
    uint8_t expected_cte_type;
    uint8_t slot_duration;
    uint8_t switching_pattern_length;
    uint8_t antenna_id[OPEN_CFW_HCI_MAX_SWITCHING_PATTERN_LEN];
} open_cfw_hci_rx_test_v3_t;

typedef struct {
    uint8_t tx_channel;
    uint8_t test_data_length;
    uint8_t packet_payload;
    uint8_t phy;
    uint8_t cte_length;
    uint8_t cte_type;
    uint8_t switching_pattern_length;
    uint8_t antenna_id[OPEN_CFW_HCI_MAX_SWITCHING_PATTERN_LEN];
} open_cfw_hci_tx_test_v3_t;

uint8_t *hciCmdAlloc(uint16_t opcode, uint16_t length);
bool hciCmdSend(uint8_t *command);
void hciCmdInit(void);
void hciCmdTimeout(void *message);
void hciCmdRecvCmpl(uint8_t num_commands);
void hciClearCmdQueue(void);
void HciResetCmd(void);
void HciDisconnectCmd(uint16_t handle, uint8_t reason);
void HciLeAddDevWhiteListCmd(uint8_t address_type, uint8_t *address);
void HciLeClearWhiteListCmd(void);
void HciLeConnUpdateCmd(uint16_t handle, open_cfw_hci_conn_spec_t *spec);
void HciLeCreateConnCmd(uint16_t scan_interval, uint16_t scan_window,
                        uint8_t filter_policy, uint8_t peer_address_type,
                        uint8_t *peer_address, uint8_t own_address_type,
                        open_cfw_hci_conn_spec_t *spec);
void HciLeCreateConnCancelCmd(void);
void HciLeRemoteConnParamReqReply(uint16_t handle, uint16_t interval_min,
                                  uint16_t interval_max, uint16_t latency,
                                  uint16_t timeout, uint16_t min_ce_length,
                                  uint16_t max_ce_length);
void HciLeRemoteConnParamReqNegReply(uint16_t handle, uint8_t reason);
void HciLeSetDataLen(uint16_t handle, uint16_t tx_octets, uint16_t tx_time);
void HciLeReadDefDataLen(void);
void HciLeWriteDefDataLen(uint16_t max_tx_octets, uint16_t max_tx_time);
void HciLeReadLocalP256PubKey(void);
void HciLeGenerateDHKey(uint8_t *public_key_x, uint8_t *public_key_y);
void HciLeReadMaxDataLen(void);
void HciLeEncryptCmd(uint8_t *key, uint8_t *data);
void HciLeLtkReqNegReplCmd(uint16_t handle);
void HciLeLtkReqReplCmd(uint16_t handle, uint8_t *key);
void HciLeRandCmd(void);
void HciLeReadAdvTXPowerCmd(void);
void HciLeReadBufSizeCmd(void);
void HciLeReadChanMapCmd(uint16_t handle);
void HciLeReadLocalSupFeatCmd(void);
void HciLeReadRemoteFeatCmd(uint16_t handle);
void HciLeReadSupStatesCmd(void);
void HciLeReadWhiteListSizeCmd(void);
void HciLeRemoveDevWhiteListCmd(uint8_t address_type, uint8_t *address);
void HciLeSetAdvEnableCmd(uint8_t enable);
void HciLeSetAdvDataCmd(uint8_t length, uint8_t *data);
void HciLeSetAdvParamCmd(uint16_t interval_min, uint16_t interval_max,
                         uint8_t advertising_type, uint8_t own_address_type,
                         uint8_t peer_address_type, uint8_t *peer_address,
                         uint8_t channel_map, uint8_t filter_policy);
void HciLeSetEventMaskCmd(uint8_t *event_mask);
void HciLeSetHostChanClassCmd(uint8_t *channel_map);
void HciLeSetRandAddrCmd(uint8_t *address);
void HciLeSetScanEnableCmd(uint8_t enable, uint8_t filter_duplicates);
void HciLeSetScanParamCmd(uint8_t scan_type, uint16_t scan_interval,
                          uint16_t scan_window, uint8_t own_address_type,
                          uint8_t filter_policy);
void HciLeSetScanRespDataCmd(uint8_t length, uint8_t *data);
void HciLeStartEncryptionCmd(uint16_t handle, uint8_t *random,
                             uint16_t diversifier, uint8_t *key);
void HciReadBdAddrCmd(void);
void HciReadBufSizeCmd(void);
void HciReadLocalSupFeatCmd(void);
void HciReadLocalVerInfoCmd(void);
void HciReadRemoteVerInfoCmd(uint16_t handle);
void HciReadRssiCmd(uint16_t handle);
void HciReadTxPwrLvlCmd(uint16_t handle, uint8_t type);
void HciSetEventMaskCmd(uint8_t *event_mask);
void HciSetEventMaskPage2Cmd(uint8_t *event_mask);
void HciReadAuthPayloadTimeout(uint16_t handle);
void HciWriteAuthPayloadTimeout(uint16_t handle, uint16_t timeout);
void HciLeAddDeviceToResolvingListCmd(uint8_t peer_address_type,
                                      const uint8_t *peer_identity_address,
                                      const uint8_t *peer_irk,
                                      const uint8_t *local_irk);
void HciLeRemoveDeviceFromResolvingList(uint8_t peer_address_type,
                                        const uint8_t *peer_identity_address);
void HciLeClearResolvingList(void);
void HciLeReadResolvingListSize(void);
void HciLeReadPeerResolvableAddr(uint8_t address_type,
                                 const uint8_t *identity_address);
void HciLeReadLocalResolvableAddr(uint8_t address_type,
                                  const uint8_t *identity_address);
void HciLeSetAddrResolutionEnable(uint8_t enable);
void HciLeSetResolvablePrivateAddrTimeout(uint16_t timeout);
void HciLeSetPrivacyModeCmd(uint8_t address_type, uint8_t *address,
                            uint8_t mode);
void HciLeReceiverTestCmd(uint8_t channel);
void HciLeTransmitterTestCmd(uint8_t channel, uint8_t data_length,
                             uint8_t packet_payload);
void HciLeTestEndCmd(void);
void HciLeReceiverTestCmdV3(open_cfw_hci_rx_test_v3_t *parameters);
void HciLeTransmitterTestCmdV3(open_cfw_hci_tx_test_v3_t *parameters);
void HciVendorSpecificCmd(uint16_t opcode, uint8_t length, uint8_t *data);
void HciLeRequestPeerScaCmd(uint16_t handle);
void HciLeReadBufSizeCmdV2(void);
void HciLeSetHostFeatureCmd(uint8_t bit_number, bool bit_value);

#if defined(OPEN_CFW_HCI_CMD_TEST)
void open_cfw_hci_cmd_reset_for_test(void);
uint8_t *open_cfw_hci_cmd_state_for_test(void);
void open_cfw_hci_cmd_set_callback_for_test(void (*callback)(void *));
#endif

#endif
