#include "r1_bootloader_model.h"

#include <string.h>

#define R1_SETTINGS_VERSION 2u
#define R1_SIGNATURE_TYPE_ECDSA_P256_SHA256 1u

static uint32_t read_le32(const uint8_t *value)
{
    return (uint32_t)value[0] |
           ((uint32_t)value[1] << 8) |
           ((uint32_t)value[2] << 16) |
           ((uint32_t)value[3] << 24);
}

static uint16_t read_le16(const uint8_t *value)
{
    return (uint16_t)((uint16_t)value[0] | ((uint16_t)value[1] << 8));
}

static bool constant_time_equal(const uint8_t *left, const uint8_t *right, size_t length)
{
    uint8_t difference = 0;
    size_t index;

    for (index = 0; index < length; ++index) {
        difference |= (uint8_t)(left[index] ^ right[index]);
    }
    return difference == 0;
}

uint32_t r1_crc32_compute(const uint8_t *data, size_t length, uint32_t previous_crc)
{
    uint32_t crc = ~previous_crc;
    size_t index;
    unsigned bit;

    if (data == NULL && length != 0) {
        return previous_crc;
    }
    for (index = 0; index < length; ++index) {
        crc ^= data[index];
        for (bit = 0; bit < 8; ++bit) {
            uint32_t mask = (uint32_t)-(int32_t)(crc & 1u);
            crc = (crc >> 1) ^ (0xedb88320u & mask);
        }
    }
    return ~crc;
}

static void copy_backup_protected_fields(
    r1_settings_t *destination,
    const r1_settings_t *backup)
{
    destination->bank_0 = backup->bank_0;
    destination->bank_1 = backup->bank_1;
    destination->write_offset = backup->write_offset;
    destination->progress = backup->progress;
    memcpy(
        destination->init_command,
        backup->init_command,
        sizeof(destination->init_command)
    );
    destination->boot_validation_softdevice = backup->boot_validation_softdevice;
    destination->boot_validation_application = backup->boot_validation_application;
    destination->boot_validation_bootloader = backup->boot_validation_bootloader;
    memcpy(
        destination->boot_validation_bytes,
        backup->boot_validation_bytes,
        sizeof(destination->boot_validation_bytes)
    );
    destination->boot_validation_crc = backup->boot_validation_crc;
}

void r1_settings_reconcile(
    const r1_settings_t *primary,
    bool primary_crc_valid,
    const r1_settings_t *backup,
    bool backup_crc_valid,
    r1_settings_t *out)
{
    if (out == NULL) {
        return;
    }
    memset(out, 0, sizeof(*out));

    if (primary_crc_valid && primary != NULL) {
        *out = *primary;
        if (backup_crc_valid && backup != NULL) {
            copy_backup_protected_fields(out, backup);
        }
    }
    else if (backup_crc_valid && backup != NULL) {
        *out = *backup;
    }
    else {
        out->settings_version = R1_SETTINGS_VERSION;
    }

    if (out->settings_version == 0) {
        out->settings_version = R1_SETTINGS_VERSION;
    }
}

r1_result_t r1_validate_init_command(
    const r1_init_command_t *command,
    const r1_validation_policy_t *policy,
    const uint8_t public_key[R1_PUBLIC_KEY_SIZE],
    r1_sha256_fn sha256,
    r1_ecdsa_verify_fn verify,
    void *crypto_context)
{
    uint8_t digest[R1_SHA256_SIZE];

    if (command == NULL || policy == NULL || public_key == NULL ||
        sha256 == NULL || verify == NULL) {
        return R1_RESULT_INVALID_PARAMETER;
    }
    if (command->signature == NULL || command->signature_length == 0) {
        return R1_RESULT_SIGNATURE_MISSING;
    }
    if (command->signature_type != R1_SIGNATURE_TYPE_ECDSA_P256_SHA256 ||
        command->signature_length != R1_SIGNATURE_SIZE) {
        return R1_RESULT_UNSUPPORTED_SIGNATURE;
    }
    if (command->signed_bytes == NULL || command->signed_bytes_length == 0 ||
        !sha256(
            crypto_context,
            command->signed_bytes,
            command->signed_bytes_length,
            digest
        ) ||
        !verify(crypto_context, digest, command->signature, public_key)) {
        return R1_RESULT_VERIFICATION_FAILED;
    }

    /* The recovered bootloader applies debug policy only after authentication. */
    if (!(command->is_debug && policy->allow_signed_debug_policy)) {
        if (command->hardware_version != policy->expected_hardware_version ||
            command->required_softdevice_id != policy->installed_softdevice_id ||
            command->firmware_version < policy->current_firmware_version) {
            return R1_RESULT_VERIFICATION_FAILED;
        }
    }
    if (command->image_size == 0 || command->image_type == R1_IMAGE_NONE) {
        return R1_RESULT_INVALID_OBJECT;
    }
    return R1_RESULT_SUCCESS;
}

r1_result_t r1_data_object_create(r1_data_state_t *state, uint32_t object_size)
{
    uint32_t remaining;

    if (state == NULL || !state->init_authenticated) {
        return R1_RESULT_INVALID_OBJECT;
    }
    if (object_size == 0 || object_size > R1_DATA_OBJECT_MAX_SIZE ||
        state->firmware_offset > state->total_image_size) {
        return R1_RESULT_INVALID_PARAMETER;
    }
    remaining = state->total_image_size - state->firmware_offset;
    if (object_size > remaining) {
        return R1_RESULT_INSUFFICIENT_RESOURCES;
    }
    state->object_start = state->firmware_offset;
    state->object_size = object_size;
    state->object_written = 0;
    return R1_RESULT_SUCCESS;
}

r1_result_t r1_data_object_write(r1_data_state_t *state, size_t fragment_size)
{
    uint32_t remaining;

    if (state == NULL || !state->init_authenticated || fragment_size == 0 ||
        fragment_size > UINT32_MAX) {
        return R1_RESULT_INVALID_PARAMETER;
    }
    if (state->object_written > state->object_size) {
        return R1_RESULT_INVALID_OBJECT;
    }
    remaining = state->object_size - state->object_written;
    if (fragment_size > remaining ||
        fragment_size > state->total_image_size - state->firmware_offset) {
        return R1_RESULT_INSUFFICIENT_RESOURCES;
    }
    state->object_written += (uint32_t)fragment_size;
    state->firmware_offset += (uint32_t)fragment_size;
    return R1_RESULT_SUCCESS;
}

r1_result_t r1_data_object_execute(r1_data_state_t *state)
{
    if (state == NULL || state->object_size == 0 ||
        state->object_written != state->object_size) {
        return R1_RESULT_INVALID_OBJECT;
    }
    state->object_start = state->firmware_offset;
    state->object_size = 0;
    state->object_written = 0;
    return R1_RESULT_SUCCESS;
}

r1_result_t r1_postvalidate_image(
    const uint8_t *image,
    size_t image_length,
    const uint8_t expected_digest[R1_SHA256_SIZE],
    r1_sha256_fn sha256,
    void *crypto_context)
{
    uint8_t actual[R1_SHA256_SIZE];

    if (image == NULL || image_length == 0 || expected_digest == NULL || sha256 == NULL) {
        return R1_RESULT_INVALID_PARAMETER;
    }
    if (!sha256(crypto_context, image, image_length, actual) ||
        !constant_time_equal(actual, expected_digest, sizeof(actual))) {
        return R1_RESULT_VERIFICATION_FAILED;
    }
    return R1_RESULT_SUCCESS;
}

r1_boot_action_t r1_choose_boot_action(
    bool force_dfu,
    bool application_valid,
    r1_image_type_t pending_image)
{
    if (pending_image == R1_IMAGE_APPLICATION) {
        return R1_BOOT_ACTION_ACTIVATE_APPLICATION;
    }
    if (pending_image == R1_IMAGE_SOFTDEVICE) {
        return R1_BOOT_ACTION_ACTIVATE_SOFTDEVICE;
    }
    if (pending_image == R1_IMAGE_BOOTLOADER) {
        return R1_BOOT_ACTION_ACTIVATE_BOOTLOADER;
    }
    if (pending_image == R1_IMAGE_SOFTDEVICE_BOOTLOADER) {
        return R1_BOOT_ACTION_ACTIVATE_SOFTDEVICE_BOOTLOADER;
    }
    if (force_dfu || !application_valid) {
        return R1_BOOT_ACTION_ENTER_DFU;
    }
    return R1_BOOT_ACTION_START_APPLICATION;
}

size_t r1_application_handoff_acl(
    uint32_t application_start,
    uint32_t application_size,
    r1_acl_range_t ranges[2])
{
    uint64_t application_end;
    uint64_t aligned_end;

    if (ranges == NULL || application_start == 0 || application_size == 0) {
        return 0;
    }
    application_end = (uint64_t)application_start + application_size;
    aligned_end = (application_end + R1_FLASH_PAGE_SIZE - 1u) &
                  ~(uint64_t)(R1_FLASH_PAGE_SIZE - 1u);
    if (aligned_end > R1_BOOTLOADER_START) {
        return 0;
    }
    ranges[0].start = R1_BOOTLOADER_START;
    ranges[0].length = R1_MBR_PARAMETER_END - R1_BOOTLOADER_START;
    ranges[1].start = 0;
    ranges[1].length = (uint32_t)aligned_end;
    return 2;
}

r1_result_t r1_parse_dfu_request(
    const uint8_t *packet,
    size_t packet_length,
    r1_dfu_request_t *request)
{
    uint8_t opcode;

    if (packet == NULL || request == NULL || packet_length < 1) {
        return R1_RESULT_INVALID_PARAMETER;
    }
    memset(request, 0, sizeof(*request));
    opcode = packet[0];
    request->opcode = opcode;

    switch (opcode) {
    case 0x01: /* OBJECT CREATE: opcode, type, uint32 size */
        if (packet_length < 6) return R1_RESULT_INVALID_PARAMETER;
        request->object_type = packet[1];
        request->size = read_le32(packet + 2);
        break;
    case 0x02: /* RECEIPT NOTIFICATION SET */
        if (packet_length < 3) return R1_RESULT_INVALID_PARAMETER;
        request->receipt_interval = read_le16(packet + 1);
        break;
    case 0x06: /* OBJECT SELECT */
        if (packet_length < 2) return R1_RESULT_INVALID_PARAMETER;
        request->object_type = packet[1];
        break;
    case 0x03: /* CRC GET */
    case 0x04: /* OBJECT EXECUTE */
    case 0x0c: /* ABORT */
        break;
    default:
        return R1_RESULT_INVALID_PARAMETER;
    }
    return R1_RESULT_SUCCESS;
}

bool r1_decode_bounded_varint(
    const uint8_t *buffer,
    size_t length,
    uint64_t *value,
    size_t *consumed)
{
    uint64_t result = 0;
    unsigned shift = 0;
    size_t index;

    if (buffer == NULL || value == NULL || consumed == NULL) {
        return false;
    }
    for (index = 0; index < length && index < 10; ++index) {
        uint8_t byte = buffer[index];
        if (shift == 63 && (byte & 0xfeu) != 0) {
            return false;
        }
        result |= (uint64_t)(byte & 0x7fu) << shift;
        if ((byte & 0x80u) == 0) {
            *value = result;
            *consumed = index + 1;
            return true;
        }
        shift += 7;
    }
    return false;
}

r1_result_t r1_copy_advertising_name(
    const r1_settings_t *settings,
    uint8_t output[R1_ADV_NAME_SIZE],
    size_t *output_length)
{
    if (settings == NULL || output == NULL || output_length == NULL ||
        settings->advertising_name_length > R1_ADV_NAME_SIZE) {
        return R1_RESULT_INVALID_PARAMETER;
    }
    memcpy(output, settings->advertising_name, settings->advertising_name_length);
    *output_length = settings->advertising_name_length;
    return R1_RESULT_SUCCESS;
}
