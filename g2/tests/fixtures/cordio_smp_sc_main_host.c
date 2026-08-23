#include <stdarg.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

struct open_cfw_smp_sc_control_block;
struct open_cfw_smp_sc_ccb;
struct open_cfw_smp_sc_config;

extern struct open_cfw_smp_sc_control_block open_cfw_test_smp_sc_control;
static struct open_cfw_smp_sc_ccb *open_cfw_test_smp_sc_records(void);
static struct open_cfw_smp_sc_config *open_cfw_test_smp_sc_config(void);

#define OPEN_CFW_SMP_SC_CONTROL_BLOCK open_cfw_test_smp_sc_control
#define OPEN_CFW_SMP_SC_RECORDS (open_cfw_test_smp_sc_records())
#define OPEN_CFW_SMP_SC_CONFIG (*open_cfw_test_smp_sc_config())

#include "../../components/apollo_main/core_overlay/cordio_smp_sc_main.c"
#include "cordio_smp_sc_main_host.h"

struct open_cfw_smp_sc_control_block open_cfw_test_smp_sc_control;
static struct open_cfw_smp_sc_ccb test_records[3];
static struct open_cfw_smp_sc_config test_config;
static unsigned allocation_calls;
static unsigned free_calls;
static unsigned fail_allocation_at;
static unsigned state_calls;
static struct open_cfw_smp_sc_header last_state_message;
static unsigned cmac_calls;
static uint8_t cmac_result;
static uint8_t cmac_text[65];
static uint16_t cmac_length;
static unsigned idle_calls;
static unsigned timer_calls;
static unsigned send_calls;
static uint8_t sent_packet[80];
static uint16_t allocated_packet_length;
static unsigned db_failure_calls;
static unsigned initiator_state_calls;
static unsigned responder_state_calls;
static unsigned trace_calls;
static char trace_lines[8][64];

static struct open_cfw_smp_sc_ccb *open_cfw_test_smp_sc_records(void)
{
    return test_records;
}

static struct open_cfw_smp_sc_config *open_cfw_test_smp_sc_config(void)
{
    return &test_config;
}

static void reset_fixture(void)
{
    memset(&open_cfw_test_smp_sc_control, 0, sizeof(open_cfw_test_smp_sc_control));
    memset(test_records, 0, sizeof(test_records));
    memset(&test_config, 0, sizeof(test_config));
    allocation_calls = 0U;
    free_calls = 0U;
    fail_allocation_at = 0U;
    state_calls = 0U;
    memset(&last_state_message, 0, sizeof(last_state_message));
    cmac_calls = 0U;
    cmac_result = 1U;
    memset(cmac_text, 0, sizeof(cmac_text));
    cmac_length = 0U;
    idle_calls = 0U;
    timer_calls = 0U;
    send_calls = 0U;
    memset(sent_packet, 0, sizeof(sent_packet));
    allocated_packet_length = 0U;
    db_failure_calls = 0U;
    initiator_state_calls = 0U;
    responder_state_calls = 0U;
    trace_calls = 0U;
    memset(trace_lines, 0, sizeof(trace_lines));
}

void *open_cfw_retained_cordio_wsf_buffer_alloc(uint16_t size)
{
    allocation_calls++;
    if (allocation_calls == fail_allocation_at) {
        return NULL;
    }
    return calloc(1U, size);
}

void open_cfw_retained_cordio_wsf_buffer_free(void *buffer)
{
    free_calls++;
    free(buffer);
}

uint8_t open_cfw_retained_cordio_sec_cmac(
    const uint8_t *key, uint8_t *text, uint16_t text_length,
    uint8_t handler_id, uint16_t parameter, uint8_t event)
{
    (void)key;
    (void)handler_id;
    (void)parameter;
    (void)event;
    cmac_calls++;
    cmac_length = text_length;
    memcpy(cmac_text, text, text_length);
    if (cmac_result != 0U) {
        free(text);
    }
    return cmac_result;
}

void open_cfw_retained_cordio_dm_conn_set_idle(
    uint8_t connection_id, uint16_t idle_mask, uint8_t idle)
{
    (void)connection_id;
    (void)idle_mask;
    (void)idle;
    idle_calls++;
}

void open_cfw_retained_cordio_smp_start_response_timer(
    struct open_cfw_smp_sc_main_ccb *ccb)
{
    (void)ccb;
    timer_calls++;
}

uint8_t *open_cfw_cordio_smp_main_message_allocate(uint16_t length)
{
    allocated_packet_length = length;
    return calloc(1U, length);
}

void open_cfw_retained_cordio_wstr_reverse_copy(
    uint8_t *destination, const uint8_t *source, uint16_t length)
{
    uint16_t index;
    for (index = 0U; index < length; index++) {
        destination[index] = source[length - index - 1U];
    }
}

void open_cfw_cordio_smp_main_send_packet(
    struct open_cfw_smp_sc_main_ccb *ccb, uint8_t *packet)
{
    uint16_t length = packet[8] == 12U ? 73U : 25U;
    (void)ccb;
    memcpy(sent_packet, packet, length);
    send_calls++;
    free(packet);
}

void open_cfw_retained_cordio_smp_state_machine_execute(
    struct open_cfw_smp_sc_main_ccb *ccb, void *message)
{
    (void)ccb;
    state_calls++;
    last_state_message = *(struct open_cfw_smp_sc_header *)message;
}

void open_cfw_retained_cordio_calc128_copy(
    uint8_t destination[16], const uint8_t source[16])
{
    memcpy(destination, source, 16U);
}

struct open_cfw_smp_sc_main_ccb *
open_cfw_cordio_smp_main_ccb_by_connection_id(uint8_t connection_id)
{
    if (connection_id == 0U || connection_id > 3U) {
        return NULL;
    }
    return &open_cfw_test_smp_sc_control.connections[connection_id - 1U];
}

void open_cfw_cordio_smp_db_pairing_failed(uint8_t connection_id)
{
    (void)connection_id;
    db_failure_calls++;
}

uint8_t *open_cfw_retained_cordio_smpi_state_string(uint8_t state)
{
    static uint8_t value[] = "initiator";
    (void)state;
    initiator_state_calls++;
    return value;
}

uint8_t *open_cfw_retained_cordio_smpr_state_string(uint8_t state)
{
    static uint8_t value[] = "responder";
    (void)state;
    responder_state_calls++;
    return value;
}

uint8_t open_cfw_retained_cordio_smp_sc_process_pairing(
    struct open_cfw_smp_sc_main_ccb *ccb, uint8_t *oob, uint8_t *display)
{
    (void)ccb;
    (void)oob;
    (void)display;
    return 1U;
}

void open_cfw_retained_cordio_smp_sc_process_authentication(
    struct open_cfw_smp_sc_main_ccb *ccb, uint8_t oob, uint8_t display)
{
    (void)ccb;
    (void)oob;
    (void)display;
}

void open_cfw_retained_cordio_wsf_trace(const char *format, ...)
{
    va_list arguments;
    va_start(arguments, format);
    va_end(arguments);
    if (trace_calls < 8U) {
        strncpy(trace_lines[trace_calls], format, 63U);
    }
    trace_calls++;
}

void open_cfw_iar_memcpy_void(
    void *destination, const void *source, uint32_t size)
{
    memcpy(destination, source, size);
}

int open_cfw_test_smp_sc_init_and_scratch(void)
{
    struct open_cfw_smp_sc_main_ccb *ccb;
    reset_fixture();
    open_cfw_test_smp_sc_control.handler_id = 9U;
    open_cfw_cordio_smp_sc_init();
    ccb = &open_cfw_test_smp_sc_control.connections[1];
    if (ccb->secure_connections != &test_records[1] ||
        open_cfw_test_smp_sc_control.lesc_supported != 1U ||
        open_cfw_test_smp_sc_control.process_pairing == NULL ||
        open_cfw_test_smp_sc_control.process_authentication == NULL) return 1;
    if (open_cfw_cordio_smp_sc_allocate_scratch_buffers(ccb) != 1U ||
        allocation_calls != 5U || ccb->secure_connections->scratch == NULL ||
        ccb->secure_connections->peer_public_key == NULL ||
        ccb->secure_connections->ltk == NULL ||
        ccb->secure_connections->local_public_key == NULL ||
        ccb->secure_connections->private_key == NULL) return 2;
    if (open_cfw_cordio_smp_sc_allocate_scratch_buffers(ccb) != 1U ||
        allocation_calls != 5U) return 3;
    open_cfw_cordio_smp_sc_free_scratch_buffers(ccb);
    return free_calls == 5U && ccb->secure_connections->scratch == NULL &&
        ccb->secure_connections->peer_public_key == NULL &&
        ccb->secure_connections->ltk == NULL &&
        ccb->secure_connections->local_public_key == NULL &&
        ccb->secure_connections->private_key == NULL ? 0 : 4;
}

int open_cfw_test_smp_sc_failure_paths(void)
{
    struct open_cfw_smp_sc_main_ccb *ccb;
    struct open_cfw_smp_sc_header message = {0};
    uint8_t key[16] = {0};
    uint8_t *text;
    reset_fixture();
    open_cfw_cordio_smp_sc_init();
    ccb = &open_cfw_test_smp_sc_control.connections[0];
    ccb->connection_id = 1U;
    fail_allocation_at = 1U;
    if (open_cfw_cordio_smp_sc_allocate(8U, ccb, &message) != NULL ||
        state_calls != 1U || message.event != 3U || message.status != 8U) return 1;
    fail_allocation_at = 0U;
    text = malloc(4U);
    cmac_result = 0U;
    open_cfw_cordio_smp_sc_cmac(key, text, 4U, ccb, &message);
    return state_calls == 2U && free_calls == 1U &&
        last_state_message.event == 3U && last_state_message.status == 8U ? 0 : 2;
}

int open_cfw_test_smp_sc_f4(void)
{
    struct open_cfw_smp_sc_main_ccb *ccb;
    struct open_cfw_smp_sc_header message = {0};
    uint8_t u[32];
    uint8_t v[32];
    uint8_t x[16] = {0};
    uint8_t index;
    reset_fixture();
    open_cfw_cordio_smp_sc_init();
    ccb = &open_cfw_test_smp_sc_control.connections[0];
    for (index = 0U; index < 32U; index++) {
        u[index] = index;
        v[index] = (uint8_t)(0x80U + index);
    }
    open_cfw_cordio_smp_sc_calculate_f4(ccb, &message, u, v, 0x5AU, x);
    return cmac_calls == 1U && cmac_length == 65U &&
        memcmp(cmac_text, u, 32U) == 0 && memcmp(cmac_text + 32U, v, 32U) == 0 &&
        cmac_text[64] == 0x5AU ? 0 : 1;
}

int open_cfw_test_smp_sc_packets(void)
{
    struct open_cfw_smp_sc_main_ccb *ccb;
    struct open_cfw_smp_sc_header message = {0};
    struct open_cfw_smp_sc_public_key local_key;
    uint8_t value[16];
    uint8_t index;
    reset_fixture();
    open_cfw_cordio_smp_sc_init();
    ccb = &open_cfw_test_smp_sc_control.connections[0];
    ccb->secure_connections->local_public_key = &local_key;
    for (index = 0U; index < 32U; index++) {
        local_key.x[index] = index;
        local_key.y[index] = (uint8_t)(0x40U + index);
    }
    open_cfw_cordio_smp_sc_send_public_key(ccb, &message);
    if (allocated_packet_length != 73U || sent_packet[8] != 12U ||
        sent_packet[9] != 31U || sent_packet[40] != 0U ||
        sent_packet[41] != 0x5FU || sent_packet[72] != 0x40U) return 1;
    for (index = 0U; index < 16U; index++) value[index] = index;
    open_cfw_cordio_smp_sc_send_dh_key_check(ccb, &message, value);
    if (sent_packet[8] != 13U || sent_packet[9] != 15U || sent_packet[24] != 0U) return 2;
    open_cfw_cordio_smp_sc_send_random(ccb, &message, value);
    if (sent_packet[8] != 4U) return 3;
    open_cfw_cordio_smp_sc_send_pairing_confirm(ccb, &message, value);
    return sent_packet[8] == 3U && send_calls == 4U && idle_calls == 4U &&
        timer_calls == 4U ? 0 : 4;
}

int open_cfw_test_smp_sc_passkey_and_attempts(void)
{
    struct open_cfw_smp_sc_main_ccb *ccb;
    struct open_cfw_smp_sc_scratch scratch = {0};
    struct open_cfw_smp_sc_header header = {0};
    reset_fixture();
    open_cfw_cordio_smp_sc_init();
    ccb = &open_cfw_test_smp_sc_control.connections[1];
    ccb->connection_id = 2U;
    ccb->secure_connections->scratch = &scratch;
    ccb->secure_connections->passkey_position = 0U;
    scratch.ra[15] = 1U;
    if (open_cfw_cordio_smp_sc_get_passkey_bit(ccb) != 0x81U) return 1;
    scratch.ra[15] = 0U;
    if (open_cfw_cordio_smp_sc_get_passkey_bit(ccb) != 0x80U) return 2;
    test_config.maximum_attempts = 2U;
    open_cfw_cordio_smp_sc_cancel_with_reattempt(2U, &header, 4U);
    if (header.event != 3U || header.param != 2U || header.status != 4U) return 3;
    open_cfw_cordio_smp_sc_fail_with_reattempt(ccb);
    return ccb->attempts == 2U && last_state_message.event == 13U &&
        last_state_message.status == 4U && db_failure_calls == 2U ? 0 : 4;
}

int open_cfw_test_smp_sc_diagnostics(void)
{
    uint8_t bytes[18];
    uint8_t index;
    reset_fixture();
    if (strcmp((char *)open_cfw_cordio_smp_sc_event_string(31U), "INT_CLEANUP") != 0 ||
        strcmp((char *)open_cfw_cordio_smp_sc_event_string(30U), "Unknown") != 0 ||
        strcmp((char *)open_cfw_cordio_smp_sc_event_string(99U), "Unknown") != 0) return 1;
    open_cfw_test_smp_sc_control.connections[0].initiator = 1U;
    (void)open_cfw_cordio_smp_sc_state_string(3U);
    open_cfw_test_smp_sc_control.connections[0].initiator = 0U;
    (void)open_cfw_cordio_smp_sc_state_string(4U);
    for (index = 0U; index < 18U; index++) bytes[index] = index;
    open_cfw_cordio_smp_sc_log_byte_array("prefix", bytes, 18U);
    return initiator_state_calls == 1U && responder_state_calls == 1U &&
        trace_calls == 3U &&
        strcmp(trace_lines[1], "[00010203 04050607 08090a0b 0c0d0e0f]") == 0 &&
        strcmp(trace_lines[2], "[1011]") == 0 ? 0 : 2;
}
