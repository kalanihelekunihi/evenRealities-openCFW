/* Host behavior fixture for the clean-room charging-case protocol. */
#include <stdint.h>
#include <string.h>

#include "../../components/shared/case/runtime_case_uart_update.c"

static unsigned write_calls;
static unsigned write_success_at;

static int test_writer(uint8_t channel, uint8_t command, uint8_t length,
                       uint8_t *payload, void *context)
{
    (void)length;
    (void)payload;
    (void)context;
    ++write_calls;
    return channel == 0x5AU && command == 0x13U &&
           write_calls == write_success_at;
}

uint32_t open_cfw_test_case_frame_scenario(void)
{
    uint8_t bytes[16] = {0x11U, 0x22U, 0x5AU, 0xA5U, 0xFFU, 4U,
                         0x13U, 1U, 2U, 3U, 0U};
    open_cfw_case_frame frame;
    uint32_t result = 0U;
    bytes[10] = open_cfw_case_frame_checksum(4U, &bytes[6]);
    result |= open_cfw_case_frame_find_validate(bytes, 11U, &frame) == 0 ? 1U : 0U;
    result |= frame.header_offset == 2U && frame.command == 0x13U &&
              frame.length == 4U ? 2U : 0U;
    bytes[10] ^= 1U;
    result |= open_cfw_case_frame_find_validate(bytes, 11U, &frame) ==
              OPEN_CFW_CASE_FRAME_BAD_CHECKSUM ? 4U : 0U;
    result |= open_cfw_case_frame_find_validate(bytes, 9U, &frame) ==
              OPEN_CFW_CASE_FRAME_TRUNCATED ? 8U : 0U;
    memset(bytes, 0, sizeof(bytes));
    result |= open_cfw_case_frame_find_validate(bytes, sizeof(bytes), &frame) ==
              OPEN_CFW_CASE_FRAME_NO_HEADER ? 16U : 0U;
    return result;
}

uint32_t open_cfw_test_case_checksum_scenario(void)
{
    static const uint8_t image[] = {1U, 2U, 3U, 4U, 0xFFU, 0U, 0U, 1U};
    uint32_t result = 0U;
    result |= open_cfw_case_image_be32_sum(image, sizeof(image)) ==
              0x00020305U ? 1U : 0U;
    result |= open_cfw_case_image_be32_sum(image, sizeof(image) - 1U) == 0U ? 2U : 0U;
    return result;
}

uint32_t open_cfw_test_case_offer_chunk_scenario(void)
{
    uint8_t payload[32] = {0};
    open_cfw_case_frame frame = {0x58U, 32U, payload, 0U, 0U};
    open_cfw_case_ota_offer offer;
    uint32_t result = 0U;
    payload[0] = 0x58U;
    payload[3] = 0x20U;
    payload[9] = 2U;
    payload[10] = 58U;
    payload[12] = 0x01U; payload[13] = 0x02U; payload[14] = 0x03U; payload[15] = 0x04U;
    payload[16] = 0xA1U; payload[17] = 0xB2U; payload[18] = 0xC3U; payload[19] = 0xD4U;
    result |= open_cfw_case_parse_ota_offer(&frame, &offer) == 1 ? 1U : 0U;
    result |= offer.image_length == 0x01020304U &&
              offer.image_checksum == 0xA1B2C3D4U ? 2U : 0U;
    payload[10] = 57U;
    result |= open_cfw_case_parse_ota_offer(&frame, &offer) == 0 ? 4U : 0U;

    memset(payload, 0, sizeof(payload));
    frame.command = 0x5AU;
    frame.length = 13U;
    payload[0] = 0x5AU;
    payload[3] = 9U;
    payload[4] = 1U; payload[5] = 2U; payload[6] = 3U; payload[7] = 4U;
    payload[8] = 5U; payload[9] = 6U; payload[10] = 7U; payload[11] = 8U;
    payload[12] = 36U;
    result |= open_cfw_case_validate_chunk(&frame) == 1 ? 8U : 0U;
    payload[12] ^= 1U;
    result |= open_cfw_case_validate_chunk(&frame) == 0 ? 16U : 0U;
    return result;
}

uint32_t open_cfw_test_case_retry_scenario(void)
{
    uint8_t payload[3] = {1U, 2U, 3U};
    uint32_t result = 0U;
    write_calls = 0U;
    write_success_at = 3U;
    result |= open_cfw_case_channel_send_retry(0x13U, 3U, payload, 1,
                                               test_writer, 0) == 1 ? 1U : 0U;
    result |= write_calls == 3U ? 2U : 0U;
    write_calls = 0U;
    write_success_at = 0U;
    result |= open_cfw_case_channel_send_retry(0x13U, 3U, payload, 1,
                                               test_writer, 0) == 0 ? 4U : 0U;
    result |= write_calls == 9U ? 8U : 0U;
    result |= payload[0] == 0xFFU && payload[1] == 0xFFU &&
              payload[2] == 0xFFU ? 16U : 0U;
    return result;
}

typedef struct ota_fixture {
    uint32_t calls;
    uint32_t erase_failures;
    uint32_t serial_pair;
    uint32_t verify_length;
    uint32_t verify_checksum;
    uint8_t informed;
    uint8_t swapped;
} ota_fixture;

static int ready(void *p) { ((ota_fixture *)p)->calls |= 1U; return 1; }
static int bank(void *p, uint8_t *value) { ((ota_fixture *)p)->calls |= 2U; *value = 1U; return 1; }
static int erase(void *p, uint8_t value) {
    ota_fixture *f = p; f->calls |= 4U;
    if (value != 2U) return 0;
    if (f->erase_failures != 0U) { --f->erase_failures; return 0; }
    return 1;
}
static int serial(void *p, uint8_t from, uint8_t to) {
    ota_fixture *f = p; f->calls |= 8U; f->serial_pair = ((uint32_t)from << 8) | to; return 1;
}
static int receive(void *p, uint8_t bank_value, uint32_t length) {
    ota_fixture *f = p; f->calls |= 16U; return bank_value == 2U && length == 0x1000U;
}
static int verify(void *p, uint8_t bank_value, uint32_t length, uint32_t checksum) {
    ota_fixture *f = p; f->calls |= 32U; f->verify_length = length; f->verify_checksum = checksum;
    return bank_value == 2U;
}
static int inform(void *p, uint8_t result) { ota_fixture *f = p; f->calls |= 64U; f->informed = result; return 1; }
static int swap(void *p, uint8_t target) { ota_fixture *f = p; f->calls |= 128U; f->swapped = target; return 1; }

uint32_t open_cfw_test_case_ota_scenario(void)
{
    open_cfw_case_ota_offer offer = {2U, 2U, 58U, 0x1000U, 0x12345678U};
    open_cfw_case_ota_context ota;
    ota_fixture f = {0};
    open_cfw_case_ota_port port = {ready, bank, erase, serial, receive,
                                   verify, inform, swap, &f};
    uint32_t result = 0U;
    unsigned guard;
    f.erase_failures = 2U;
    open_cfw_case_ota_begin(&ota, &offer);
    for (guard = 0U; guard < 16U && ota.state != OPEN_CFW_CASE_OTA_DONE &&
         ota.state != OPEN_CFW_CASE_OTA_FAILED; ++guard) {
        open_cfw_case_ota_advance(&ota, &port);
    }
    result |= ota.state == OPEN_CFW_CASE_OTA_DONE ? 1U : 0U;
    result |= f.calls == 0xFFU ? 2U : 0U;
    result |= f.serial_pair == 0x0102U ? 4U : 0U;
    result |= f.verify_length == 0x1000U &&
              f.verify_checksum == 0x12345678U ? 8U : 0U;
    result |= f.informed == 0U && f.swapped == 2U ? 16U : 0U;
    return result;
}
