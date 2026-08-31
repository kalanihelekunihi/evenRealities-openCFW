/* SPDX-License-Identifier: MIT */
/*************************************************************************************************/
/* Clean-room G2 Apollo HCI driver state, queue, scheduler, and vendor-command implementation. */
/*************************************************************************************************/

#include "runtime_cordio_hci_driver.h"

#include <stddef.h>

#define OPEN_CFW_HCI_DRIVER_QUEUE_FULL_ERROR 0x09000000u
#define OPEN_CFW_HCI_DRIVER_PACKET_TOO_LARGE_ERROR 0x09000001u
#define OPEN_CFW_HCI_DRIVER_RX_TOO_LARGE_ERROR 0x09000002u
#define OPEN_CFW_HCI_DRIVER_TRANSACTION_LIMIT_ERROR 0x09000006u
#define OPEN_CFW_HCI_DRIVER_RECORD_COUNT 8u
#define OPEN_CFW_HCI_DRIVER_RECORD_BYTES 260u
#define OPEN_CFW_HCI_DRIVER_DATA_BYTES 256u
#define OPEN_CFW_HCI_DRIVER_TRANSFER_EVENT 1u
#define OPEN_CFW_HCI_DRIVER_HEARTBEAT_EVENT 2u
#define OPEN_CFW_HCI_DRIVER_HEARTBEAT_MS 10000u
#define OPEN_CFW_HCI_DRIVER_MAX_TRANSACTIONS 1000u
#define OPEN_CFW_HCI_DRIVER_MAX_READS 4u

typedef struct {
    volatile uint32_t write_index;
    volatile uint32_t read_index;
    volatile uint32_t length;
    uint32_t capacity;
    uint32_t item_size;
    uint8_t *data;
} open_cfw_hci_driver_queue_t;

typedef struct {
    uint32_t length;
    uint8_t data[OPEN_CFW_HCI_DRIVER_DATA_BYTES];
} open_cfw_hci_driver_record_t;

typedef struct {
    uint16_t parameter;
    uint8_t event;
    uint8_t status;
} open_cfw_hci_driver_message_t;

extern void WsfSetEvent(uint8_t handler_id, uint8_t event);
extern void WsfTimerStartMs(void *timer, uint32_t milliseconds);
extern void WsfTimerStop(void *timer);
extern void HciReadBufSizeCmd(void);
extern uint16_t hciTrSerialRxIncoming(const uint8_t *data, uint16_t length);
extern void DmDevReset(void);
extern void HciVendorSpecificCmd(uint16_t opcode, uint8_t length, const uint8_t *data);
extern void open_cfw_hci_driver_queue_init(open_cfw_hci_driver_queue_t *queue,
                                           void *data, uint32_t item_size,
                                           uint32_t array_size);
extern void open_cfw_hci_driver_queue_add(open_cfw_hci_driver_queue_t *queue,
                                          uint32_t items, uint32_t count);
extern void open_cfw_hci_driver_queue_remove(open_cfw_hci_driver_queue_t *queue,
                                             uint32_t items, uint32_t count);

/* These providers are the explicit physical BLEIF boundary.  Their C ABI is
 * complete.  Hardware qualification is blocked by unavailable physical evidence; future
 * production substitution requires authorized G2 hardware plus a controller
 * fixture or authenticated golden capture. */
extern uint32_t open_cfw_hci_driver_hal_boot(bool cold_boot, uint8_t address[6]);
extern void open_cfw_hci_driver_hal_shutdown(void);
extern bool open_cfw_hci_driver_hal_irq_pending(void);
extern uint32_t open_cfw_hci_driver_hal_read(uint8_t *data, uint32_t capacity,
                                             uint32_t *length);
extern uint32_t open_cfw_hci_driver_hal_write(const uint8_t *data, uint32_t length);
extern void open_cfw_hci_driver_hal_constant_transmission(uint8_t channel);
extern void open_cfw_hci_driver_hal_carrier_wave(uint8_t channel);
extern void open_cfw_hci_driver_hal_sleep(bool enable);

#if defined(OPEN_CFW_HCI_DRIVER_PRODUCTION)
#define OPEN_CFW_HCI_DRIVER_PTR(type, address) ((type *)(uintptr_t)(address))
#define OPEN_CFW_HCI_DRIVER_ERROR_HANDLER \
    (*OPEN_CFW_HCI_DRIVER_PTR(open_cfw_hci_driver_error_handler_t, 0x20074644u))
#define OPEN_CFW_HCI_DRIVER_ERROR_STATUS \
    (*OPEN_CFW_HCI_DRIVER_PTR(uint32_t, 0x20074648u))
#define OPEN_CFW_HCI_DRIVER_READ_LENGTH \
    (*OPEN_CFW_HCI_DRIVER_PTR(uint32_t, 0x20074638u))
#define OPEN_CFW_HCI_DRIVER_READ_OFFSET \
    (*OPEN_CFW_HCI_DRIVER_PTR(uint32_t, 0x2007463Cu))
#define OPEN_CFW_HCI_DRIVER_INTERRUPTS \
    (*OPEN_CFW_HCI_DRIVER_PTR(uint32_t, 0x20074640u))
#define OPEN_CFW_HCI_DRIVER_HANDLER_ID \
    (*OPEN_CFW_HCI_DRIVER_PTR(uint8_t, 0x20074FCBu))
#define OPEN_CFW_HCI_DRIVER_MAC OPEN_CFW_HCI_DRIVER_PTR(uint8_t, 0x20074148u)
#define OPEN_CFW_HCI_DRIVER_NVDS OPEN_CFW_HCI_DRIVER_PTR(uint8_t, 0x20074150u)
#define OPEN_CFW_HCI_DRIVER_READ_BUFFER OPEN_CFW_HCI_DRIVER_PTR(uint8_t, 0x20000DACu)
#define OPEN_CFW_HCI_DRIVER_HEARTBEAT OPEN_CFW_HCI_DRIVER_PTR(uint8_t, 0x20073E64u)
#define OPEN_CFW_HCI_DRIVER_WAKE_TIMER OPEN_CFW_HCI_DRIVER_PTR(uint8_t, 0x20073E74u)
#define OPEN_CFW_HCI_DRIVER_QUEUE \
    OPEN_CFW_HCI_DRIVER_PTR(open_cfw_hci_driver_queue_t, 0x20073BA8u)
#define OPEN_CFW_HCI_DRIVER_RECORDS \
    OPEN_CFW_HCI_DRIVER_PTR(open_cfw_hci_driver_record_t, 0x20065A10u)
#else
static open_cfw_hci_driver_error_handler_t open_cfw_hci_driver_error_handler;
static uint32_t open_cfw_hci_driver_error_status;
static uint32_t open_cfw_hci_driver_read_length;
static uint32_t open_cfw_hci_driver_read_offset;
static uint32_t open_cfw_hci_driver_interrupts;
static uint8_t open_cfw_hci_driver_handler_id;
static uint8_t open_cfw_hci_driver_mac[6];
static uint8_t open_cfw_hci_driver_nvds[8];
static uint8_t open_cfw_hci_driver_read_buffer[OPEN_CFW_HCI_DRIVER_DATA_BYTES];
static uint8_t open_cfw_hci_driver_heartbeat[16];
static uint8_t open_cfw_hci_driver_wake_timer[16];
static open_cfw_hci_driver_queue_t open_cfw_hci_driver_queue;
static open_cfw_hci_driver_record_t
    open_cfw_hci_driver_records[OPEN_CFW_HCI_DRIVER_RECORD_COUNT];
#define OPEN_CFW_HCI_DRIVER_ERROR_HANDLER open_cfw_hci_driver_error_handler
#define OPEN_CFW_HCI_DRIVER_ERROR_STATUS open_cfw_hci_driver_error_status
#define OPEN_CFW_HCI_DRIVER_READ_LENGTH open_cfw_hci_driver_read_length
#define OPEN_CFW_HCI_DRIVER_READ_OFFSET open_cfw_hci_driver_read_offset
#define OPEN_CFW_HCI_DRIVER_INTERRUPTS open_cfw_hci_driver_interrupts
#define OPEN_CFW_HCI_DRIVER_HANDLER_ID open_cfw_hci_driver_handler_id
#define OPEN_CFW_HCI_DRIVER_MAC open_cfw_hci_driver_mac
#define OPEN_CFW_HCI_DRIVER_NVDS open_cfw_hci_driver_nvds
#define OPEN_CFW_HCI_DRIVER_READ_BUFFER open_cfw_hci_driver_read_buffer
#define OPEN_CFW_HCI_DRIVER_HEARTBEAT open_cfw_hci_driver_heartbeat
#define OPEN_CFW_HCI_DRIVER_WAKE_TIMER open_cfw_hci_driver_wake_timer
#define OPEN_CFW_HCI_DRIVER_QUEUE (&open_cfw_hci_driver_queue)
#define OPEN_CFW_HCI_DRIVER_RECORDS open_cfw_hci_driver_records
#endif

void error_check(uint32_t status)
{
    if (status != 0u) {
        OPEN_CFW_HCI_DRIVER_ERROR_STATUS = status;
        if (OPEN_CFW_HCI_DRIVER_ERROR_HANDLER !=
            (open_cfw_hci_driver_error_handler_t)0) {
            OPEN_CFW_HCI_DRIVER_ERROR_HANDLER(status);
        }
    }
}

void HciDrvErrorHandlerSet(open_cfw_hci_driver_error_handler_t handler)
{
    OPEN_CFW_HCI_DRIVER_ERROR_HANDLER = handler;
}

void HciDrvEmptyWriteQueue(void)
{
    open_cfw_hci_driver_queue_init(
        OPEN_CFW_HCI_DRIVER_QUEUE, OPEN_CFW_HCI_DRIVER_RECORDS,
        OPEN_CFW_HCI_DRIVER_RECORD_BYTES,
        OPEN_CFW_HCI_DRIVER_RECORD_COUNT * OPEN_CFW_HCI_DRIVER_RECORD_BYTES);
}

uint32_t HciDrvRadioBoot(bool cold_boot)
{
    uint32_t status;
    OPEN_CFW_HCI_DRIVER_READ_LENGTH = 0u;
    OPEN_CFW_HCI_DRIVER_READ_OFFSET = 0u;
    OPEN_CFW_HCI_DRIVER_INTERRUPTS = 0u;
    HciDrvEmptyWriteQueue();
    status = open_cfw_hci_driver_hal_boot(cold_boot, OPEN_CFW_HCI_DRIVER_MAC);
    error_check(status);
    return status;
}

void HciDrvRadioShutdown(void)
{
    WsfTimerStop(OPEN_CFW_HCI_DRIVER_HEARTBEAT);
    open_cfw_hci_driver_hal_shutdown();
    OPEN_CFW_HCI_DRIVER_READ_LENGTH = 0u;
    OPEN_CFW_HCI_DRIVER_READ_OFFSET = 0u;
}

void HciDrvShutdown(void)
{
    HciDrvRadioShutdown();
}

uint16_t hciDrvWrite(uint8_t type, uint16_t length, uint8_t *data)
{
    open_cfw_hci_driver_record_t *record;
    uint16_t index;

    if (OPEN_CFW_HCI_DRIVER_QUEUE->length == OPEN_CFW_HCI_DRIVER_QUEUE->capacity) {
        error_check(OPEN_CFW_HCI_DRIVER_QUEUE_FULL_ERROR);
        return length;
    }
    if (length >= 0x103u || (length != 0u && data == (uint8_t *)0)) {
        error_check(OPEN_CFW_HCI_DRIVER_PACKET_TOO_LARGE_ERROR);
        return length;
    }
    record = (open_cfw_hci_driver_record_t *)(void *)(
        OPEN_CFW_HCI_DRIVER_QUEUE->data + OPEN_CFW_HCI_DRIVER_QUEUE->write_index);
    record->length = (uint32_t)length + 1u;
    record->data[0] = type;
    for (index = 0u; index < length; ++index) {
        record->data[(uint16_t)(index + 1u)] = data[index];
    }
    open_cfw_hci_driver_queue_add(OPEN_CFW_HCI_DRIVER_QUEUE, 0u, 1u);
    WsfSetEvent(OPEN_CFW_HCI_DRIVER_HANDLER_ID, OPEN_CFW_HCI_DRIVER_TRANSFER_EVENT);
    return length;
}

void HciDrvHandlerInit(uint8_t handler_id)
{
    OPEN_CFW_HCI_DRIVER_HANDLER_ID = handler_id;
    OPEN_CFW_HCI_DRIVER_HEARTBEAT[12] = handler_id;
    OPEN_CFW_HCI_DRIVER_HEARTBEAT[10] = OPEN_CFW_HCI_DRIVER_HEARTBEAT_EVENT;
    OPEN_CFW_HCI_DRIVER_WAKE_TIMER[12] = handler_id;
    OPEN_CFW_HCI_DRIVER_WAKE_TIMER[10] = 3u;
}

void HciDrvIntService(void)
{
    ++OPEN_CFW_HCI_DRIVER_INTERRUPTS;
    WsfSetEvent(OPEN_CFW_HCI_DRIVER_HANDLER_ID, OPEN_CFW_HCI_DRIVER_TRANSFER_EVENT);
}

static bool open_cfw_hci_driver_drain_saved_receive(void)
{
    uint16_t consumed;
    uint32_t remaining;
    if (OPEN_CFW_HCI_DRIVER_READ_OFFSET >= OPEN_CFW_HCI_DRIVER_READ_LENGTH) {
        OPEN_CFW_HCI_DRIVER_READ_LENGTH = 0u;
        OPEN_CFW_HCI_DRIVER_READ_OFFSET = 0u;
        return true;
    }
    remaining = OPEN_CFW_HCI_DRIVER_READ_LENGTH - OPEN_CFW_HCI_DRIVER_READ_OFFSET;
    consumed = hciTrSerialRxIncoming(
        OPEN_CFW_HCI_DRIVER_READ_BUFFER + OPEN_CFW_HCI_DRIVER_READ_OFFSET,
        (uint16_t)remaining);
    OPEN_CFW_HCI_DRIVER_READ_OFFSET += consumed;
    if (OPEN_CFW_HCI_DRIVER_READ_OFFSET != OPEN_CFW_HCI_DRIVER_READ_LENGTH) {
        WsfSetEvent(OPEN_CFW_HCI_DRIVER_HANDLER_ID, OPEN_CFW_HCI_DRIVER_TRANSFER_EVENT);
        return false;
    }
    OPEN_CFW_HCI_DRIVER_READ_LENGTH = 0u;
    OPEN_CFW_HCI_DRIVER_READ_OFFSET = 0u;
    return true;
}

static void open_cfw_hci_driver_recover(uint32_t status)
{
    error_check(status);
    HciDrvRadioShutdown();
    (void)HciDrvRadioBoot(false);
    HciDrvEmptyWriteQueue();
    DmDevReset();
}

void HciDrvHandler(uint8_t event_mask, void *message)
{
    const open_cfw_hci_driver_message_t *header =
        (const open_cfw_hci_driver_message_t *)message;
    uint32_t transactions = 0u;
    uint32_t reads = 0u;
    (void)event_mask;

    if (header != (const open_cfw_hci_driver_message_t *)0 &&
        header->event == OPEN_CFW_HCI_DRIVER_HEARTBEAT_EVENT) {
        HciReadBufSizeCmd();
        WsfTimerStartMs(OPEN_CFW_HCI_DRIVER_HEARTBEAT,
                        OPEN_CFW_HCI_DRIVER_HEARTBEAT_MS);
        return;
    }
    if (!open_cfw_hci_driver_drain_saved_receive()) {
        return;
    }
    while (transactions < OPEN_CFW_HCI_DRIVER_MAX_TRANSACTIONS) {
        uint32_t status;
        ++transactions;
        if (open_cfw_hci_driver_hal_irq_pending()) {
            OPEN_CFW_HCI_DRIVER_READ_LENGTH = 0u;
            status = open_cfw_hci_driver_hal_read(
                OPEN_CFW_HCI_DRIVER_READ_BUFFER,
                OPEN_CFW_HCI_DRIVER_DATA_BYTES,
                &OPEN_CFW_HCI_DRIVER_READ_LENGTH);
            if (OPEN_CFW_HCI_DRIVER_READ_LENGTH > OPEN_CFW_HCI_DRIVER_DATA_BYTES) {
                open_cfw_hci_driver_recover(OPEN_CFW_HCI_DRIVER_RX_TOO_LARGE_ERROR);
                return;
            }
            if (status != 0u) {
                open_cfw_hci_driver_recover(status);
                return;
            }
            WsfTimerStop(OPEN_CFW_HCI_DRIVER_HEARTBEAT);
            WsfTimerStartMs(OPEN_CFW_HCI_DRIVER_HEARTBEAT,
                            OPEN_CFW_HCI_DRIVER_HEARTBEAT_MS);
            if (!open_cfw_hci_driver_drain_saved_receive()) {
                return;
            }
            if (++reads >= OPEN_CFW_HCI_DRIVER_MAX_READS) {
                WsfSetEvent(OPEN_CFW_HCI_DRIVER_HANDLER_ID,
                            OPEN_CFW_HCI_DRIVER_TRANSFER_EVENT);
                return;
            }
            continue;
        }
        if (OPEN_CFW_HCI_DRIVER_QUEUE->length != 0u) {
            open_cfw_hci_driver_record_t *record =
                (open_cfw_hci_driver_record_t *)(void *)(
                    OPEN_CFW_HCI_DRIVER_QUEUE->data +
                    OPEN_CFW_HCI_DRIVER_QUEUE->read_index);
            status = open_cfw_hci_driver_hal_write(record->data, record->length);
            if (status != 0u) {
                WsfSetEvent(OPEN_CFW_HCI_DRIVER_HANDLER_ID,
                            OPEN_CFW_HCI_DRIVER_TRANSFER_EVENT);
                return;
            }
            WsfTimerStop(OPEN_CFW_HCI_DRIVER_HEARTBEAT);
            WsfTimerStartMs(OPEN_CFW_HCI_DRIVER_HEARTBEAT,
                            OPEN_CFW_HCI_DRIVER_HEARTBEAT_MS);
            open_cfw_hci_driver_queue_remove(OPEN_CFW_HCI_DRIVER_QUEUE, 0u, 1u);
            reads = 0u;
            continue;
        }
        return;
    }
    open_cfw_hci_driver_recover(OPEN_CFW_HCI_DRIVER_TRANSACTION_LIMIT_ERROR);
}

void HciVscUpdateNvdsParam(void)
{
    static const uint8_t parameters[8] = {0xFFu, 0x7Cu, 0x01u, 0x0Fu,
                                           0xB8u, 0x19u, 0x00u, 0x00u};
    uint8_t index;
    for (index = 0u; index < 8u; ++index) {
        OPEN_CFW_HCI_DRIVER_NVDS[index] = parameters[index];
    }
    HciVendorSpecificCmd(0xFFF2u, 8u, OPEN_CFW_HCI_DRIVER_NVDS);
}

bool HciVscSetRfPowerLevelEx(int8_t power_dbm)
{
    uint8_t payload;
    if (power_dbm < -27 || power_dbm > 6) {
        return false;
    }
    payload = (uint8_t)power_dbm;
    HciVendorSpecificCmd(0xFCC4u, 1u, &payload);
    return true;
}

void HciVscConstantTransmission(uint8_t channel)
{
    open_cfw_hci_driver_hal_constant_transmission(channel);
}

bool HciVscSetCustom_BDAddr(uint8_t *address)
{
    uint8_t index;
    uint8_t any = 0u;
    if (address == (uint8_t *)0) {
        return false;
    }
    for (index = 0u; index < 6u; ++index) {
        any |= address[index];
    }
    if (any == 0u) {
        return false;
    }
    for (index = 0u; index < 6u; ++index) {
        OPEN_CFW_HCI_DRIVER_MAC[index] = address[index];
    }
    return true;
}

void HciVscUpdateBDAddress(void)
{
    HciVendorSpecificCmd(0xFC43u, 6u, OPEN_CFW_HCI_DRIVER_MAC);
}

void HciVscCarrierWaveMode(uint8_t channel)
{
    open_cfw_hci_driver_hal_carrier_wave(channel);
}

void HciDrvBleSleepSet(bool enable)
{
    open_cfw_hci_driver_hal_sleep(enable);
}

#if defined(OPEN_CFW_HCI_DRIVER_TEST)
void open_cfw_hci_driver_reset_for_test(void)
{
    uint8_t index;
    OPEN_CFW_HCI_DRIVER_ERROR_HANDLER = (open_cfw_hci_driver_error_handler_t)0;
    OPEN_CFW_HCI_DRIVER_ERROR_STATUS = 0u;
    OPEN_CFW_HCI_DRIVER_READ_LENGTH = 0u;
    OPEN_CFW_HCI_DRIVER_READ_OFFSET = 0u;
    OPEN_CFW_HCI_DRIVER_INTERRUPTS = 0u;
    OPEN_CFW_HCI_DRIVER_HANDLER_ID = 0u;
    for (index = 0u; index < 6u; ++index) OPEN_CFW_HCI_DRIVER_MAC[index] = 0u;
    for (index = 0u; index < 8u; ++index) OPEN_CFW_HCI_DRIVER_NVDS[index] = 0u;
    HciDrvEmptyWriteQueue();
}

uint32_t open_cfw_hci_driver_error_for_test(void)
{
    return OPEN_CFW_HCI_DRIVER_ERROR_STATUS;
}

uint8_t *open_cfw_hci_driver_mac_for_test(void)
{
    return OPEN_CFW_HCI_DRIVER_MAC;
}

uint8_t *open_cfw_hci_driver_nvds_for_test(void)
{
    return OPEN_CFW_HCI_DRIVER_NVDS;
}

uint32_t open_cfw_hci_driver_interrupts_for_test(void)
{
    return OPEN_CFW_HCI_DRIVER_INTERRUPTS;
}
#endif
