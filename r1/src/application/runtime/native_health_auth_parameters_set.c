/* Stock 0x8ea0c: assemble cached identity and pKey, decrypt the SDK token,
 * and dispatch its four fields through the source-owned GoMore primitives. */
#include "native_health_authorize.h"
#include "native_gomore_runtime_configuration.h"
#include "../../vendor/gomore_primitives/gomore_primitives.h"
#include "../crypto/stock_two_pass.h"
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

extern void r1_native_device_id_read_boundary(void *);
extern void r1_native_srand(uint32_t);
extern uint32_t r1_native_rand(void);
extern const uint8_t r1_native_ctype_window[257];

/* Two adjacent, non-executable key records at stock 0xbced8 and 0xbcef8. */
static const uint8_t auth_keys[2][32] = {
    {0xe5,0x21,0xc0,0x99,0x49,0x52,0xc8,0x3f,0xb8,0x47,0x7a,0x80,0x9e,0x9c,0x54,0x0e,
     0xfb,0xee,0xb8,0x0c,0x13,0xb8,0x4b,0xb7,0x7b,0x30,0xfb,0xcf,0x6e,0x34,0xe8,0x13},
    {0x9e,0x8f,0x3f,0xa5,0x70,0x25,0x62,0xa0,0xaf,0xf0,0x83,0x7f,0x9b,0x94,0xcd,0xea,
     0xfa,0x85,0x7d,0xd0,0xef,0xc4,0x34,0x6e,0x25,0x02,0x96,0xcc,0x59,0xce,0x69,0x40},
};

static int32_t random_value(void) { return (int32_t)r1_native_rand(); }
static bool decrypt(void *context, const uint8_t *input, size_t length,
                    const uint8_t key[32], uint8_t *output,
                    size_t capacity, size_t *written)
{
    (void)context;
    if (length > capacity || length > INT32_MAX) return false;
    int32_t output_length = 0;
    if (r1_stock_two_pass_callback(input, (int32_t)length, key,
                                   output, &output_length) != 0 ||
        output_length < 0 || (size_t)output_length > capacity) return false;
    *written = (size_t)output_length;
    return true;
}

static bool equals_token(const uint8_t *text, size_t length, const char *token)
{
    size_t index = 0;
    while (token[index] != 0) ++index;
    if (length != index) return false;
    for (size_t position = 0; position < length; ++position)
        if (text[position] != (uint8_t)token[position]) return false;
    return true;
}

static bool message_matches(void *context, const uint8_t *message,
                            size_t length)
{
    (void)context;
    size_t token_length = 0;
    while (token_length < length && message[token_length] != ',')
        ++token_length;
    return equals_token(message, token_length, "1839052049009318") ||
           equals_token(message, token_length, "1839052049073388");
}

static int32_t parse_identifier(void *context, char *field,
                                const gomore_primitives_auth_parameters *parameters,
                                gomore_primitives_sdk_auth_status *status,
                                uint32_t scratch[4])
{
    (void)context; (void)parameters;
    return gomore_primitives_validate_identifier_status(
        (const uint8_t *)field, r1_native_ctype_window + 1,
        (uint8_t *)status, sizeof(*status), (uint8_t *)scratch, 16,
        r1_native_srand, random_value);
}
static int32_t parse_key(void *context, char *field,
                         const gomore_primitives_auth_parameters *parameters,
                         gomore_primitives_sdk_auth_status *status,
                         uint32_t scratch[4])
{
    (void)context;
    size_t length = 0; while (field[length]) ++length;
    return gomore_primitives_validate_key_and_update_status(
        (const uint8_t *)field, length, parameters, sizeof(*parameters),
        status, sizeof(*status), scratch, 16, r1_native_srand, random_value);
}
static int32_t parse_timestamp(void *context, char *field,
                               const gomore_primitives_auth_parameters *parameters,
                               gomore_primitives_sdk_auth_status *status,
                               uint32_t scratch[4])
{
    (void)context;
    return gomore_primitives_decimal_config_update(
        (const uint8_t *)field, parameters, sizeof(*parameters),
        status, sizeof(*status), scratch, 16,
        gomore_primitives_return_zero() != 0,
        r1_native_srand, random_value);
}
static int32_t parse_final(void *context, char *field,
                           const gomore_primitives_auth_parameters *parameters,
                           gomore_primitives_sdk_auth_status *status,
                           uint32_t scratch[4])
{
    (void)context; (void)parameters;
    return gomore_primitives_sdk_auth_final_field_parse(
        (const uint8_t *)field, (uint8_t *)status, sizeof(*status),
        (uint8_t *)scratch, 16, r1_native_srand, random_value);
}
static int32_t validate_identifier(void *context, char *field,
                                   const gomore_primitives_auth_parameters *parameters,
                                   gomore_primitives_sdk_auth_status *status)
{
    (void)context;
    size_t length = 0; while (field[length]) ++length;
    return gomore_primitives_validate_record_bytes(
        (const uint8_t *)field, length, parameters, sizeof(*parameters),
        status, sizeof(*status));
}
static int32_t validate_key(void *context, char *field,
                            const gomore_primitives_auth_parameters *parameters,
                            gomore_primitives_sdk_auth_status *status)
{
    (void)context;
    size_t length = 0; while (field[length]) ++length;
    return gomore_primitives_seed_and_test_text_class(
        (const uint8_t *)field, length, r1_native_ctype_window + 1,
        parameters, sizeof(*parameters), status, sizeof(*status),
        r1_native_srand);
}
static int32_t validate_timestamp(void *context, char *field,
                                  const gomore_primitives_auth_parameters *parameters,
                                  gomore_primitives_sdk_auth_status *status)
{
    (void)context; (void)parameters;
    size_t length = 0; while (field[length]) ++length;
    return gomore_primitives_validate_su_signature(
        (const uint8_t *)field, length + 1, status, sizeof(*status));
}

uint32_t r1_health_auth_parameters_set(const struct r1_health_auth_parameters *request)
{
    if (request == NULL) return (uint32_t)-1005;
    uint8_t key[68] = {0};
    uint8_t uuid[25] = {0};
    r1_native_device_id_read_boundary(uuid);
    size_t length = 0;
    while (length < 24 && uuid[length] != 0) ++length;
    (void)r1_health_authorization_key_read(key, 64, 0, 0);
    const gomore_primitives_auth_parameters parameters = {
        .key = key, .device_uuid = uuid,
        .device_uuid_length = (uint8_t)length,
        .timestamp = request->timestamp,
    };
    const gomore_primitives_sdk_auth_configuration configuration = {
        .decrypt_keys = {auth_keys[0], auth_keys[1]},
        .decrypt = decrypt,
        .message_matches = message_matches,
        .parse_fields = {parse_identifier, parse_key, parse_timestamp, parse_final},
        .validate_fields = {validate_identifier, validate_key, validate_timestamp},
    };
    gomore_primitives_sdk_auth_status status;
    int32_t result = -1002;
    if (!gomore_primitives_sdk_auth_parse(
            &parameters, &configuration, &status, &result)) return (uint32_t)result;
    volatile uint8_t *destination = (volatile uint8_t *)&r1_gomore_runtime_configuration;
    const uint8_t *source = (const uint8_t *)&status;
    for (size_t index = 0; index < sizeof(status); ++index)
        destination[index] = source[index];
    return (uint32_t)result;
}
