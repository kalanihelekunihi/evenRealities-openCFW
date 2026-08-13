#include "r1_bootloader_model.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    bool hash_ok;
    bool signature_ok;
    uint8_t digest[R1_SHA256_SIZE];
} fake_crypto_t;

static bool fake_sha256(
    void *context,
    const uint8_t *data,
    size_t length,
    uint8_t digest[R1_SHA256_SIZE])
{
    fake_crypto_t *crypto = context;
    (void)data;
    (void)length;
    memcpy(digest, crypto->digest, R1_SHA256_SIZE);
    return crypto->hash_ok;
}

static bool fake_verify(
    void *context,
    const uint8_t digest[R1_SHA256_SIZE],
    const uint8_t signature[R1_SIGNATURE_SIZE],
    const uint8_t public_key[R1_PUBLIC_KEY_SIZE])
{
    fake_crypto_t *crypto = context;
    (void)digest;
    (void)signature;
    (void)public_key;
    return crypto->signature_ok;
}

static void test_crc(void)
{
    static const uint8_t sample[] = "123456789";
    assert(r1_crc32_compute(sample, sizeof(sample) - 1, 0) == 0xcbf43926u);
}

static void test_settings_reconcile(void)
{
    r1_settings_t primary = {0};
    r1_settings_t backup = {0};
    r1_settings_t result;

    primary.settings_version = 2;
    primary.bank_0.bank_code = R1_IMAGE_BOOTLOADER;
    primary.advertising_name_length = 3;
    memcpy(primary.advertising_name, "NEW", 3);
    backup.settings_version = 2;
    backup.bank_0.bank_code = R1_IMAGE_APPLICATION;

    r1_settings_reconcile(&primary, true, &backup, true, &result);
    assert(result.bank_0.bank_code == R1_IMAGE_APPLICATION);
    assert(result.advertising_name_length == 3);
    assert(memcmp(result.advertising_name, "NEW", 3) == 0);

    r1_settings_reconcile(&primary, true, &backup, false, &result);
    assert(result.bank_0.bank_code == R1_IMAGE_BOOTLOADER);
}

static void test_signature_and_policy(void)
{
    uint8_t key[R1_PUBLIC_KEY_SIZE] = {0};
    uint8_t signature[R1_SIGNATURE_SIZE] = {0};
    uint8_t signed_bytes[] = {1, 2, 3};
    fake_crypto_t crypto = {.hash_ok = true, .signature_ok = true, .digest = {0}};
    r1_validation_policy_t policy = {
        .expected_hardware_version = 52,
        .current_firmware_version = 10,
        .installed_softdevice_id = 0x100,
        .allow_signed_debug_policy = true
    };
    r1_init_command_t command = {
        .hardware_version = 52,
        .firmware_version = 11,
        .required_softdevice_id = 0x100,
        .image_type = R1_IMAGE_APPLICATION,
        .image_size = 4096,
        .signature_type = 1,
        .signature = signature,
        .signature_length = sizeof(signature),
        .signed_bytes = signed_bytes,
        .signed_bytes_length = sizeof(signed_bytes)
    };

    assert(r1_validate_init_command(
        &command, &policy, key, fake_sha256, fake_verify, &crypto
    ) == R1_RESULT_SUCCESS);
    crypto.signature_ok = false;
    assert(r1_validate_init_command(
        &command, &policy, key, fake_sha256, fake_verify, &crypto
    ) == R1_RESULT_VERIFICATION_FAILED);
    crypto.signature_ok = true;
    command.signature_length = 63;
    assert(r1_validate_init_command(
        &command, &policy, key, fake_sha256, fake_verify, &crypto
    ) == R1_RESULT_UNSUPPORTED_SIGNATURE);
}

static void test_data_bounds(void)
{
    r1_data_state_t state = {
        .init_authenticated = true,
        .total_image_size = 5000,
        .firmware_offset = 0
    };

    assert(r1_data_object_create(&state, 4096) == R1_RESULT_SUCCESS);
    assert(r1_data_object_write(&state, 2048) == R1_RESULT_SUCCESS);
    assert(r1_data_object_write(&state, 2049) == R1_RESULT_INSUFFICIENT_RESOURCES);
    assert(r1_data_object_write(&state, 2048) == R1_RESULT_SUCCESS);
    assert(r1_data_object_execute(&state) == R1_RESULT_SUCCESS);
    assert(r1_data_object_create(&state, 905) == R1_RESULT_INSUFFICIENT_RESOURCES);
    assert(r1_data_object_create(&state, 904) == R1_RESULT_SUCCESS);
}

static void test_postvalidation(void)
{
    uint8_t image[] = {4, 5, 6};
    fake_crypto_t crypto = {.hash_ok = true, .signature_ok = true, .digest = {7}};
    uint8_t expected[R1_SHA256_SIZE] = {7};

    assert(r1_postvalidate_image(
        image, sizeof(image), expected, fake_sha256, &crypto
    ) == R1_RESULT_SUCCESS);
    expected[31] = 1;
    assert(r1_postvalidate_image(
        image, sizeof(image), expected, fake_sha256, &crypto
    ) == R1_RESULT_VERIFICATION_FAILED);
}

static void test_transport_and_varint(void)
{
    r1_dfu_request_t request;
    uint8_t short_create[] = {1, 2, 0, 0, 0};
    uint8_t create[] = {1, 2, 0x00, 0x10, 0x00, 0x00};
    uint8_t unterminated[] = {0x80};
    uint8_t encoded[] = {0xac, 0x02};
    uint64_t value = 0;
    size_t consumed = 0;

    assert(r1_parse_dfu_request(NULL, 0, &request) == R1_RESULT_INVALID_PARAMETER);
    assert(r1_parse_dfu_request(
        short_create, sizeof(short_create), &request
    ) == R1_RESULT_INVALID_PARAMETER);
    assert(r1_parse_dfu_request(create, sizeof(create), &request) == R1_RESULT_SUCCESS);
    assert(request.object_type == 2 && request.size == 4096);
    assert(!r1_decode_bounded_varint(
        unterminated, sizeof(unterminated), &value, &consumed
    ));
    assert(r1_decode_bounded_varint(encoded, sizeof(encoded), &value, &consumed));
    assert(value == 300 && consumed == 2);
}

static void test_boot_and_acl(void)
{
    r1_acl_range_t ranges[2];

    assert(r1_choose_boot_action(false, true, R1_IMAGE_NONE) ==
           R1_BOOT_ACTION_START_APPLICATION);
    assert(r1_choose_boot_action(false, true, R1_IMAGE_BOOTLOADER) ==
           R1_BOOT_ACTION_ACTIVATE_BOOTLOADER);
    assert(r1_application_handoff_acl(0x27000, 0x9de08, ranges) == 2);
    assert(ranges[0].start == 0xf8000 && ranges[0].length == 0x7000);
    assert(ranges[1].start == 0 && ranges[1].length == 0xc5000);
}

static void test_advertising_name_bound(void)
{
    r1_settings_t settings = {0};
    uint8_t output[R1_ADV_NAME_SIZE];
    size_t length = 0;

    settings.advertising_name_length = 20;
    assert(r1_copy_advertising_name(&settings, output, &length) == R1_RESULT_SUCCESS);
    settings.advertising_name_length = 21;
    assert(r1_copy_advertising_name(&settings, output, &length) ==
           R1_RESULT_INVALID_PARAMETER);
}

int main(void)
{
    test_crc();
    test_settings_reconcile();
    test_signature_and_policy();
    test_data_bounds();
    test_postvalidation();
    test_transport_and_varint();
    test_boot_and_acl();
    test_advertising_name_bound();
    puts("r1 bootloader functional model: all tests passed");
    return 0;
}
