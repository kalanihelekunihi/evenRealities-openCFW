#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static unsigned char open_cfw_test_sc_control_storage[512];
static unsigned char open_cfw_test_sc_config_storage[32];
#define OPEN_CFW_SMP_SC_ACT_CONTROL_BLOCK \
    (*(struct open_cfw_smp_sc_act_control_block *)open_cfw_test_sc_control_storage)
#define OPEN_CFW_SMP_SC_ACT_CONFIG \
    (*(struct open_cfw_smp_sc_act_config *)open_cfw_test_sc_config_storage)
#include "../../components/apollo_main/core_overlay/cordio_smp_sc_act.c"

static uint8_t local_address[6], local_rpa[6], peer_address[6], peer_rpa[6];
static uint8_t packet[96], allocation[128], last_text[128], ecc_key_bytes[96];
static struct open_cfw_smp_sc_act_public_key local_key, peer_key;
static struct open_cfw_smp_sc_act_scratch scratch;
static struct open_cfw_smp_sc_act_ltk ltk;
static uint8_t private_key[32];
static uint8_t local_type, peer_type, allocation_ok, shared_secret_ok;
static uint8_t state_event, state_status, callback_event, callback_byte;
static uint8_t cmac_key[16], cmac_length, ecc_handler, ecc_event;
static uint16_t ecc_parameter;
static unsigned state_calls, callback_calls, cleanup_calls, free_calls;
static unsigned fail_calls, send_calls, timer_calls, cmac_calls, ecc_calls;

static void reset_fixture(void)
{
    memset(open_cfw_test_sc_control_storage, 0,
        sizeof(open_cfw_test_sc_control_storage));
    memset(open_cfw_test_sc_config_storage, 0,
        sizeof(open_cfw_test_sc_config_storage));
    memset(local_rpa, 0, sizeof(local_rpa));
    memset(peer_rpa, 0, sizeof(peer_rpa));
    memset(packet, 0, sizeof(packet));
    memset(allocation, 0, sizeof(allocation));
    memset(last_text, 0, sizeof(last_text));
    memset(&local_key, 0, sizeof(local_key));
    memset(&peer_key, 0, sizeof(peer_key));
    memset(&scratch, 0, sizeof(scratch));
    memset(&ltk, 0, sizeof(ltk));
    memset(private_key, 0, sizeof(private_key));
    for (unsigned i = 0; i < 6; i++) {
        local_address[i] = (uint8_t)(0x10U + i);
        peer_address[i] = (uint8_t)(0x20U + i);
    }
    for (unsigned i = 0; i < sizeof(ecc_key_bytes); i++)
        ecc_key_bytes[i] = (uint8_t)i;
    local_type = 0U; peer_type = 1U; allocation_ok = 1U;
    shared_secret_ok = 1U; state_event = state_status = callback_event = 0U;
    callback_byte = cmac_length = ecc_handler = ecc_event = 0U;
    ecc_parameter = 0U;
    state_calls = callback_calls = cleanup_calls = free_calls = 0U;
    fail_calls = send_calls = timer_calls = cmac_calls = ecc_calls = 0U;
    OPEN_CFW_SMP_SC_ACT_CONTROL_BLOCK.handler_id = 9U;
    OPEN_CFW_SMP_SC_ACT_CONTROL_BLOCK.lesc_supported = 1U;
    OPEN_CFW_SMP_SC_ACT_CONFIG.minimum_key_length = 7U;
}

static void attach_sc(struct open_cfw_smp_sc_act_ccb *ccb,
    struct open_cfw_smp_sc_act_sc_ccb *sc)
{
    memset(ccb, 0, sizeof(*ccb)); memset(sc, 0, sizeof(*sc));
    ccb->secure_connections = sc; ccb->connection_id = 2U;
    sc->local_public_key = &local_key; sc->peer_public_key = &peer_key;
    sc->scratch = &scratch; sc->ltk = &ltk; sc->private_key = private_key;
}

uint8_t *open_cfw_retained_cordio_dm_conn_local_address(uint8_t id)
{ (void)id; return local_address; }
uint8_t *open_cfw_retained_cordio_dm_conn_local_rpa(uint8_t id)
{ (void)id; return local_rpa; }
uint8_t open_cfw_retained_cordio_dm_conn_local_address_type(uint8_t id)
{ (void)id; return local_type; }
uint8_t *open_cfw_retained_cordio_dm_conn_peer_address(uint8_t id)
{ (void)id; return peer_address; }
uint8_t *open_cfw_retained_cordio_dm_conn_peer_rpa(uint8_t id)
{ (void)id; return peer_rpa; }
uint8_t open_cfw_retained_cordio_dm_conn_peer_address_type(uint8_t id)
{ (void)id; return peer_type; }
void open_cfw_retained_cordio_wstr_reverse_copy(
    uint8_t *destination, const uint8_t *source, uint16_t length)
{ for (uint16_t i = 0; i < length; i++) destination[i] = source[length - i - 1U]; }
void open_cfw_iar_memcpy_void(void *destination, const void *source, uint32_t size)
{ memcpy(destination, source, size); }
void *open_cfw_runtime_memory_zero(void *destination, uint32_t size)
{ return memset(destination, 0, size); }
void *open_cfw_cordio_dm_sec_get_ecc_key(void) { return ecc_key_bytes; }
void open_cfw_cordio_dm_sec_smp_callback_execute(void *message)
{
    const struct open_cfw_smp_sc_act_header *header = message;
    callback_calls++; callback_event = header->event;
    callback_byte = ((const uint8_t *)message)[4];
}
void open_cfw_retained_cordio_smp_state_machine_execute(
    struct open_cfw_smp_sc_act_ccb *ccb, void *message)
{
    const struct open_cfw_smp_sc_act_header *header = message;
    (void)ccb; state_calls++; state_event = header->event; state_status = header->status;
}
uint8_t open_cfw_cordio_smp_sc_allocate_scratch_buffers(
    struct open_cfw_smp_sc_act_ccb *ccb)
{ (void)ccb; return allocation_ok; }
void open_cfw_cordio_smp_sc_free_scratch_buffers(
    struct open_cfw_smp_sc_act_ccb *ccb)
{ (void)ccb; free_calls++; }
uint8_t *open_cfw_cordio_smp_sc_allocate(
    uint8_t size, struct open_cfw_smp_sc_act_ccb *ccb,
    struct open_cfw_smp_sc_act_header *message)
{ (void)ccb; (void)message; memset(allocation, 0, sizeof(allocation)); return allocation_ok && size <= sizeof(allocation) ? allocation : NULL; }
uint8_t *open_cfw_cordio_smp_sc_cat(
    uint8_t *destination, const uint8_t *source, uint8_t length)
{ memcpy(destination, source, length); return destination + length; }
uint8_t *open_cfw_cordio_smp_sc_cat128(uint8_t *destination, uint8_t *source)
{ memcpy(destination, source, 16); return destination + 16; }
void open_cfw_cordio_smp_sc_cmac(
    const uint8_t *key, uint8_t *text, uint8_t text_length,
    struct open_cfw_smp_sc_act_ccb *ccb,
    struct open_cfw_smp_sc_act_header *message)
{
    (void)ccb; (void)message; cmac_calls++; cmac_length = text_length;
    memcpy(cmac_key, key, 16); memcpy(last_text, text, text_length);
}
void open_cfw_cordio_smp_sc_calculate_f4(
    struct open_cfw_smp_sc_act_ccb *ccb,
    struct open_cfw_smp_sc_act_header *message, uint8_t *u, uint8_t *v,
    uint8_t z, uint8_t *x)
{ (void)ccb; (void)message; cmac_calls++; last_text[0] = u[0]; last_text[1] = v[0]; last_text[2] = z; last_text[3] = x[0]; }
void open_cfw_cordio_smp_sc_cancel_with_reattempt(
    uint8_t id, struct open_cfw_smp_sc_act_header *header, uint8_t status)
{ header->param = id; header->event = 3U; header->status = status; }
void open_cfw_cordio_smp_act_cleanup(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{ (void)ccb; (void)msg; cleanup_calls++; }
void open_cfw_cordio_smp_act_pairing_failed(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{ (void)ccb; (void)msg; fail_calls++; }
void open_cfw_cordio_smp_act_send_pairing_failed(
    struct open_cfw_smp_sc_act_ccb *ccb, uint8_t reason)
{ (void)ccb; (void)reason; send_calls++; }
void open_cfw_cordio_smp_act_start_response_timer(
    struct open_cfw_smp_sc_act_ccb *ccb)
{ (void)ccb; timer_calls++; }
uint8_t *open_cfw_cordio_smp_main_message_allocate(uint16_t length)
{ return allocation_ok && length <= sizeof(packet) ? packet : NULL; }
void open_cfw_cordio_smp_main_send_packet(
    struct open_cfw_smp_sc_act_ccb *ccb, uint8_t *value)
{ (void)ccb; if (value == packet) send_calls++; }
void open_cfw_retained_cordio_calc128_copy(
    uint8_t destination[16], const uint8_t source[16])
{ memcpy(destination, source, 16); }
uint8_t open_cfw_retained_cordio_sec_ecc_gen_shared_secret(
    const struct open_cfw_smp_sc_act_ecc_key *key, uint8_t handler,
    uint16_t parameter, uint8_t event)
{
    ecc_calls++; ecc_handler = handler; ecc_parameter = parameter; ecc_event = event;
    memcpy(last_text, key, sizeof(*key)); return shared_secret_ok;
}

int open_cfw_test_smp_sc_act_address_contract(void)
{
    struct open_cfw_smp_sc_act_ccb ccb; struct open_cfw_smp_sc_act_sc_ccb sc;
    uint8_t output[14]; reset_fixture(); attach_sc(&ccb, &sc); ccb.initiator = 1U;
    local_rpa[0] = 0xa1U; local_rpa[5] = 0xa6U;
    uint8_t *cursor = open_cfw_cordio_smp_sc_act_cat_initiator_address(&ccb, output);
    cursor = open_cfw_cordio_smp_sc_act_cat_responder_address(&ccb, cursor);
    return !((cursor - output) == 14 && output[0] == 1U && output[1] == 0xa6U &&
        output[6] == 0xa1U && output[7] == peer_type && output[8] == 0x25U &&
        output[13] == 0x20U);
}

int open_cfw_test_smp_sc_act_pairing_hybrid_contract(void)
{
    struct open_cfw_smp_sc_act_ccb ccb; struct open_cfw_smp_sc_act_sc_ccb sc;
    uint8_t oob, display; reset_fixture(); attach_sc(&ccb, &sc); ccb.initiator = 1U;
    ccb.pair_request[1] = ccb.pair_response[1] = 3U;
    ccb.pair_request[3] = ccb.pair_response[3] = 0x0cU;
    ccb.pair_request[4] = ccb.pair_response[4] = 16U;
    if (open_cfw_cordio_smp_sc_act_process_pairing(&ccb, &oob, &display) != 1U)
        return 1;
    return !(sc.lesc_enabled == 1U && sc.authentication_type == 1U &&
        (ccb.authentication & 4U) != 0U && state_event == 17U && state_status == 0U &&
        local_key.x[0] == 0U && local_key.y[0] == 32U && private_key[0] == 64U);
}

int open_cfw_test_smp_sc_act_pairing_failure_contract(void)
{
    struct open_cfw_smp_sc_act_ccb ccb; struct open_cfw_smp_sc_act_sc_ccb sc;
    uint8_t oob, display; reset_fixture(); attach_sc(&ccb, &sc);
    ccb.pair_request[3] = ccb.pair_response[3] = 8U;
    ccb.pair_request[4] = ccb.pair_response[4] = 16U;
    OPEN_CFW_SMP_SC_ACT_CONTROL_BLOCK.lesc_supported = 0U;
    if (open_cfw_cordio_smp_sc_act_process_pairing(&ccb, &oob, &display) != 0U ||
        state_event != 3U || state_status != 3U) return 1;
    reset_fixture(); attach_sc(&ccb, &sc); ccb.pair_request[4] = 6U;
    ccb.pair_response[4] = 16U;
    return !(open_cfw_cordio_smp_sc_act_process_pairing(&ccb, &oob, &display) == 0U &&
        state_event == 3U && state_status == 6U);
}

int open_cfw_test_smp_sc_act_auth_and_selection_contract(void)
{
    struct open_cfw_smp_sc_act_ccb ccb; struct open_cfw_smp_sc_act_sc_ccb sc;
    union open_cfw_smp_sc_act_message message;
    reset_fixture(); attach_sc(&ccb, &sc); memset(&message, 0, sizeof(message));
    sc.lesc_enabled = 1U; sc.authentication_type = 2U;
    open_cfw_cordio_smp_sc_act_authentication_request(&ccb, 1U, 1U);
    if (callback_event != 46U || callback_byte != 1U) return 1;
    for (unsigned i = 0; i < 64; i++) packet[8U + 1U + i] = (uint8_t)(i + 1U);
    message.data.packet = packet; sc.authentication_type = 4U;
    open_cfw_cordio_smp_sc_act_authentication_select(&ccb, &message);
    return !(state_event == 19U && peer_key.x[0] == 32U && peer_key.x[31] == 1U &&
        peer_key.y[0] == 64U && peer_key.y[31] == 33U);
}

int open_cfw_test_smp_sc_act_passkey_cleanup_contract(void)
{
    struct open_cfw_smp_sc_act_ccb ccb; struct open_cfw_smp_sc_act_sc_ccb sc;
    union open_cfw_smp_sc_act_message message;
    reset_fixture(); attach_sc(&ccb, &sc); memset(&message, 0, sizeof(message));
    sc.display = 1U; sc.keypress_notify = 1U;
    open_cfw_cordio_smp_sc_act_passkey_setup(&ccb, &message);
    if (ccb.next_command != 3U || callback_event != 46U || callback_byte != 0U)
        return 1;
    message.keypress.keypress = 4U;
    open_cfw_cordio_smp_sc_act_passkey_send(&ccb, &message);
    if (timer_calls != 1U || send_calls != 1U || packet[8] != 14U || packet[9] != 4U)
        return 1;
    open_cfw_cordio_smp_sc_act_pairing_cancel(&ccb, &message);
    return !(send_calls == 2U && cleanup_calls == 1U && free_calls == 1U && fail_calls == 1U);
}

int open_cfw_test_smp_sc_act_crypto_contract(void)
{
    struct open_cfw_smp_sc_act_ccb ccb; struct open_cfw_smp_sc_act_sc_ccb sc;
    union open_cfw_smp_sc_act_message message; uint8_t cipher[16];
    reset_fixture(); attach_sc(&ccb, &sc); memset(&message, 0, sizeof(message));
    for (unsigned i = 0; i < 32; i++) { local_key.x[i] = (uint8_t)(0x40U+i); peer_key.x[i] = (uint8_t)(0x80U+i); private_key[i] = (uint8_t)(0xc0U+i); }
    for (unsigned i = 0; i < 16; i++) { scratch.initiator_random[i] = (uint8_t)i; scratch.responder_random[i] = (uint8_t)(0x10U+i); scratch.rb[i] = (uint8_t)(0x20U+i); cipher[i] = (uint8_t)(0x30U+i); }
    ccb.initiator = 1U;
    open_cfw_cordio_smp_sc_act_jwnc_calculate_g2(&ccb, &message);
    if (cmac_length != 80U || last_text[0] != 0x40U || last_text[32] != 0x80U || last_text[64] != 0x10U || cmac_key[0] != 0U) return 1;
    message.aes.ciphertext = cipher;
    open_cfw_cordio_smp_sc_act_calculate_f6_ea(&ccb, &message);
    if (cmac_length != 65U || last_text[0] != 0U || last_text[16] != 0x10U || last_text[32] != 0x20U || ltk.temporary_ltk[0] != 0x3fU) return 1;
    open_cfw_cordio_smp_sc_act_calculate_shared_secret(&ccb, &message);
    return !(ecc_calls == 1U && ecc_handler == 9U && ecc_parameter == 2U && ecc_event == 25U && last_text[0] == 0x80U && last_text[64] == 0xc0U);
}
