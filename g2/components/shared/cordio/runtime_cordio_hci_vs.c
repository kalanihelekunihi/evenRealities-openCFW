/* SPDX-License-Identifier: MIT */
/*************************************************************************************************/
/* Clean-room G2 Cordio vendor reset sequence over authenticated public HCI command seams. */
/*************************************************************************************************/

#include "runtime_cordio_hci_vs.h"

#include <stddef.h>

#define CORE_FEATURES 0x88u
#define CORE_RESOLVING_LIST_SIZE 0x91u
#define CORE_MAX_TX_OCTETS 0x92u
#define CORE_MAX_TX_TIME_LOW 0x94u
#define CORE_MAX_TX_TIME_HIGH 0x95u
#define CORE_BUF_SIZE 0x7eu
#define CORE_AVAIL_BUFS 0x82u
#define CORE_NUM_BUFS 0x83u
#define CORE_WHITE_LIST_SIZE 0x84u
#define CORE_LE_STATES 0x60u
#define CORE_BD_ADDR 0x68u
#define CORE_EXT_RESET 0xa0u
#define HCI_RESETTING 0x21u

#define HCI_EVT_COMMAND_COMPLETE 0x0eu
#define HCI_OPCODE_SET_EVENT_MASK 0x0c01u
#define HCI_OPCODE_RESET 0x0c03u
#define HCI_OPCODE_SET_EVENT_MASK_PAGE_2 0x0c63u
#define HCI_OPCODE_READ_LOCAL_VERSION 0x1001u
#define HCI_OPCODE_READ_BD_ADDR 0x1009u
#define HCI_OPCODE_LE_SET_EVENT_MASK 0x2001u
#define HCI_OPCODE_LE_READ_BUF_SIZE 0x2002u
#define HCI_OPCODE_LE_READ_LOCAL_FEATURES 0x2003u
#define HCI_OPCODE_LE_READ_WHITE_LIST_SIZE 0x200fu
#define HCI_OPCODE_LE_RAND 0x2018u
#define HCI_OPCODE_LE_READ_SUPPORTED_STATES 0x201cu
#define HCI_OPCODE_LE_READ_MAX_DATA_LEN 0x2024u
#define HCI_OPCODE_LE_READ_RESOLVING_LIST_SIZE 0x202au
#define HCI_OPCODE_LE_WRITE_DEFAULT_DATA_LEN 0x202fu
#define HCI_OPCODE_LE_READ_MAX_ADV_DATA_LEN 0x203au
#define HCI_OPCODE_LE_READ_NUM_ADV_SETS 0x203bu
#define HCI_OPCODE_LE_READ_PERIODIC_ADV_LIST_SIZE 0x204au
#define HCI_OPCODE_VS_RF_POWER 0xfcc4u
#define HCI_OPCODE_VS_NVDS_UPDATE 0xfff2u

extern void HciLeReadResolvingListSize(void);
extern void HciLeReadMaxDataLen(void);
extern void HciLeRandCmd(void);
extern void HciResetCmd(void);
extern void HciVscUpdateBDAddress(void);
extern void HciVscUpdateNvdsParam(void);
extern void HciVscSetRfPowerLevelEx(uint8_t level);
extern void HciSetEventMaskCmd(const uint8_t *mask);
extern void HciLeSetEventMaskCmd(const uint8_t *mask);
extern void HciSetEventMaskPage2Cmd(const uint8_t *mask);
extern void HciReadBdAddrCmd(void);
extern void HciLeReadBufSizeCmd(void);
extern void HciLeReadSupStatesCmd(void);
extern void HciLeReadWhiteListSizeCmd(void);
extern void HciLeReadLocalSupFeatCmd(void);
extern void HciLeWriteDefDataLen(uint16_t octets, uint16_t time);

#if defined(OPEN_CFW_HCI_VS_PRODUCTION)
#define CORE ((uint8_t *)(uintptr_t)0x20071478u)
#define HCI_CB ((uint8_t *)(uintptr_t)0x20073870u)
#define FEATURE_CONFIG (*(const uint64_t *)(uintptr_t)0x20000028u)
#define RAND_COUNT (*(uint8_t *)(uintptr_t)0x20074fd0u)
#define EVENT_MASK ((const uint8_t *)(uintptr_t)0x0078d6dcu)
#define LE_EVENT_MASK ((const uint8_t *)(uintptr_t)0x0078d6e4u)
#define EVENT_MASK_PAGE_2 ((const uint8_t *)(uintptr_t)0x0078d6ecu)
#else
static uint8_t open_cfw_core[0xa4];
static uint8_t open_cfw_hci_cb[0x24];
static uint64_t open_cfw_feature_config;
static uint8_t open_cfw_rand_count;
static uint8_t open_cfw_event_mask[8];
static uint8_t open_cfw_le_event_mask[8];
static uint8_t open_cfw_event_mask_page_2[8];
static void (*open_cfw_reset_callback)(void *event);
static void (*open_cfw_extended_callback)(const uint8_t *parameters, uint16_t opcode);
#define CORE open_cfw_core
#define HCI_CB open_cfw_hci_cb
#define FEATURE_CONFIG open_cfw_feature_config
#define RAND_COUNT open_cfw_rand_count
#define EVENT_MASK open_cfw_event_mask
#define LE_EVENT_MASK open_cfw_le_event_mask
#define EVENT_MASK_PAGE_2 open_cfw_event_mask_page_2
#endif

static __attribute__((always_inline)) inline uint16_t get16(const uint8_t *data)
{
    return (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}

static __attribute__((always_inline)) inline uint64_t get64(const uint8_t *data)
{
    uint64_t value = 0u;
    uint8_t index;
    for (index = 0u; index < 8u; ++index) value |= (uint64_t)data[index] << (index * 8u);
    return value;
}

static __attribute__((always_inline)) inline void copy_bytes(
    uint8_t *destination, const uint8_t *source, uint8_t length)
{
    while (length-- != 0u) *destination++ = *source++;
}

static __attribute__((always_inline)) inline void (*reset_callback(void))(void *)
{
#if defined(OPEN_CFW_HCI_VS_PRODUCTION)
    return *(void (**)(void *))(void *)(HCI_CB + 8u);
#else
    return open_cfw_reset_callback;
#endif
}

static __attribute__((always_inline)) inline void (*extended_callback(void))(
    const uint8_t *, uint16_t)
{
#if defined(OPEN_CFW_HCI_VS_PRODUCTION)
    return *(void (**)(const uint8_t *, uint16_t))(void *)(CORE + CORE_EXT_RESET);
#else
    return open_cfw_extended_callback;
#endif
}

void hciCoreReadResolvingListSize(void)
{
    uint64_t controller = *(const uint64_t *)(const void *)(CORE + CORE_FEATURES);
    if ((controller & (UINT64_C(1) << 6)) != 0u &&
        (FEATURE_CONFIG & (UINT64_C(1) << 6)) != 0u) {
        HciLeReadResolvingListSize();
    } else {
        CORE[CORE_RESOLVING_LIST_SIZE] = 0u;
        hciCoreReadMaxDataLen();
    }
}

void hciCoreReadMaxDataLen(void)
{
    uint64_t controller = *(const uint64_t *)(const void *)(CORE + CORE_FEATURES);
    if ((controller & (UINT64_C(1) << 5)) != 0u &&
        (FEATURE_CONFIG & (UINT64_C(1) << 5)) != 0u) {
        HciLeReadMaxDataLen();
    } else {
        HciLeRandCmd();
    }
}

void hciCoreResetStart(void)
{
    HciResetCmd();
    HciVscUpdateBDAddress();
}

void hciCoreResetSequence(uint8_t *message)
{
    uint16_t opcode;
    uint8_t *parameters;
    void (*extended)(const uint8_t *, uint16_t);
    if (message == (uint8_t *)0 || message[0] != HCI_EVT_COMMAND_COMPLETE) return;
    opcode = get16(message + 3u);
    parameters = message + 6u;
    extended = extended_callback();

    switch (opcode) {
    case HCI_OPCODE_SET_EVENT_MASK:
        HciLeSetEventMaskCmd(LE_EVENT_MASK);
        break;
    case HCI_OPCODE_RESET:
        RAND_COUNT = 0u;
        HciVscUpdateNvdsParam();
        break;
    case HCI_OPCODE_SET_EVENT_MASK_PAGE_2:
        HciReadBdAddrCmd();
        break;
    case HCI_OPCODE_READ_BD_ADDR:
        copy_bytes(CORE + CORE_BD_ADDR, parameters, 6u);
        HciLeReadBufSizeCmd();
        break;
    case HCI_OPCODE_LE_SET_EVENT_MASK:
        HciSetEventMaskPage2Cmd(EVENT_MASK_PAGE_2);
        break;
    case HCI_OPCODE_LE_READ_BUF_SIZE:
        CORE[CORE_BUF_SIZE] = parameters[0];
        CORE[CORE_BUF_SIZE + 1u] = parameters[1];
        CORE[CORE_NUM_BUFS] = parameters[2];
        CORE[CORE_AVAIL_BUFS] = parameters[2];
        HciLeReadSupStatesCmd();
        break;
    case HCI_OPCODE_LE_READ_LOCAL_FEATURES:
        *(uint64_t *)(void *)(CORE + CORE_FEATURES) = get64(parameters);
        hciCoreReadResolvingListSize();
        break;
    case HCI_OPCODE_LE_READ_WHITE_LIST_SIZE:
        CORE[CORE_WHITE_LIST_SIZE] = parameters[0];
        HciLeReadLocalSupFeatCmd();
        break;
    case HCI_OPCODE_LE_RAND:
        if (RAND_COUNT < 3u) {
            ++RAND_COUNT;
            HciLeRandCmd();
        } else {
            uint32_t event = 0u;
            void (*callback)(void *) = reset_callback();
            HCI_CB[HCI_RESETTING] = 0u;
            if (callback != (void (*)(void *))0) callback(&event);
        }
        break;
    case HCI_OPCODE_LE_READ_SUPPORTED_STATES:
        copy_bytes(CORE + CORE_LE_STATES, parameters, 8u);
        HciLeReadWhiteListSizeCmd();
        break;
    case HCI_OPCODE_LE_READ_MAX_DATA_LEN:
        if (extended != (void (*)(const uint8_t *, uint16_t))0) {
            extended(parameters, opcode);
        } else {
            CORE[CORE_MAX_TX_OCTETS] = 0u;
            CORE[CORE_MAX_TX_OCTETS + 1u] = 0u;
            CORE[CORE_MAX_TX_TIME_LOW] = 0u;
            CORE[CORE_MAX_TX_TIME_HIGH] = 0u;
            HciLeRandCmd();
        }
        break;
    case HCI_OPCODE_LE_READ_RESOLVING_LIST_SIZE:
        CORE[CORE_RESOLVING_LIST_SIZE] = parameters[0];
        hciCoreReadMaxDataLen();
        break;
    case HCI_OPCODE_LE_WRITE_DEFAULT_DATA_LEN:
        HciLeWriteDefDataLen(get16(parameters), get16(parameters + 2u));
        break;
    case HCI_OPCODE_VS_RF_POWER:
        HciSetEventMaskCmd(EVENT_MASK);
        break;
    case HCI_OPCODE_VS_NVDS_UPDATE:
        HciVscSetRfPowerLevelEx(6u);
        break;
    case HCI_OPCODE_READ_LOCAL_VERSION:
    case HCI_OPCODE_LE_READ_MAX_ADV_DATA_LEN:
    case HCI_OPCODE_LE_READ_NUM_ADV_SETS:
    case HCI_OPCODE_LE_READ_PERIODIC_ADV_LIST_SIZE:
        if (extended != (void (*)(const uint8_t *, uint16_t))0) extended(parameters, opcode);
        break;
    default:
        break;
    }
}

uint8_t hciCoreVsCmdCmplRcvd(uint16_t opcode, uint8_t *message, uint8_t length)
{
    (void)opcode; (void)message; (void)length; return 0u;
}

uint8_t hciCoreVsEvtRcvd(uint8_t *message, uint8_t length)
{
    (void)message; (void)length; return 0u;
}

uint8_t hciCoreHwErrorRcvd(uint8_t *message)
{
    (void)message; return 0u;
}

void HciVsInit(uint8_t parameter) { (void)parameter; }

#if defined(OPEN_CFW_HCI_VS_TEST)
void open_cfw_hci_vs_reset_for_test(void)
{
    uint16_t index;
    for (index = 0u; index < sizeof(open_cfw_core); ++index) open_cfw_core[index] = 0u;
    for (index = 0u; index < sizeof(open_cfw_hci_cb); ++index) open_cfw_hci_cb[index] = 0u;
    open_cfw_feature_config = 0u; open_cfw_rand_count = 0u;
    open_cfw_reset_callback = (void (*)(void *))0;
    open_cfw_extended_callback = (void (*)(const uint8_t *, uint16_t))0;
}
uint8_t *open_cfw_hci_vs_core_for_test(void) { return CORE; }
uint8_t *open_cfw_hci_vs_hci_cb_for_test(void) { return HCI_CB; }
void open_cfw_hci_vs_set_features_for_test(uint64_t configured, uint64_t controller)
{
    open_cfw_feature_config = configured;
    *(uint64_t *)(void *)(CORE + CORE_FEATURES) = controller;
}
void open_cfw_hci_vs_set_callbacks_for_test(
    void (*reset)(void *), void (*extended)(const uint8_t *, uint16_t))
{
    open_cfw_reset_callback = reset; open_cfw_extended_callback = extended;
}
#endif
