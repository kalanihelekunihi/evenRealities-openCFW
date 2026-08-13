#ifndef R1_BOOTLOADER_MODEL_H
#define R1_BOOTLOADER_MODEL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define R1_FLASH_PAGE_SIZE 4096u
#define R1_BOOTLOADER_START 0x000f8000u
#define R1_MBR_PARAMETER_END 0x000ff000u
#define R1_INIT_COMMAND_MAX_SIZE 512u
#define R1_DATA_OBJECT_MAX_SIZE 4096u
#define R1_PUBLIC_KEY_SIZE 64u
#define R1_SIGNATURE_SIZE 64u
#define R1_SHA256_SIZE 32u
#define R1_ADV_NAME_SIZE 20u

typedef enum {
    R1_RESULT_SUCCESS = 1,
    R1_RESULT_INVALID_PARAMETER = 2,
    R1_RESULT_INVALID_OBJECT = 5,
    R1_RESULT_OPERATION_FAILED = 10,
    R1_RESULT_SIGNATURE_MISSING = 0x13,
    R1_RESULT_UNSUPPORTED_SIGNATURE = 0x16,
    R1_RESULT_VERIFICATION_FAILED = 0x17,
    R1_RESULT_INSUFFICIENT_RESOURCES = 0x04
} r1_result_t;

typedef enum {
    R1_IMAGE_NONE = 0x00,
    R1_IMAGE_APPLICATION = 0x01,
    R1_IMAGE_SOFTDEVICE = 0xa5,
    R1_IMAGE_BOOTLOADER = 0xaa,
    R1_IMAGE_SOFTDEVICE_BOOTLOADER = 0xac
} r1_image_type_t;

typedef enum {
    R1_BOOT_ACTION_START_APPLICATION,
    R1_BOOT_ACTION_ENTER_DFU,
    R1_BOOT_ACTION_ACTIVATE_APPLICATION,
    R1_BOOT_ACTION_ACTIVATE_SOFTDEVICE,
    R1_BOOT_ACTION_ACTIVATE_BOOTLOADER,
    R1_BOOT_ACTION_ACTIVATE_SOFTDEVICE_BOOTLOADER
} r1_boot_action_t;

typedef struct {
    uint32_t bank_code;
    uint32_t image_size;
    uint32_t image_crc;
} r1_bank_t;

typedef struct {
    uint32_t command_size;
    uint32_t command_offset;
    uint32_t data_object_size;
    uint32_t firmware_image_offset;
} r1_progress_t;

typedef struct {
    uint32_t crc;
    uint32_t settings_version;
    r1_bank_t bank_0;
    r1_bank_t bank_1;
    uint32_t write_offset;
    r1_progress_t progress;
    uint8_t init_command[R1_INIT_COMMAND_MAX_SIZE];
    uint8_t boot_validation_softdevice;
    uint8_t boot_validation_application;
    uint8_t boot_validation_bootloader;
    uint8_t boot_validation_bytes[R1_SHA256_SIZE];
    uint32_t boot_validation_crc;
    uint8_t advertising_name[R1_ADV_NAME_SIZE];
    uint32_t advertising_name_length;
} r1_settings_t;

typedef bool (*r1_sha256_fn)(
    void *context,
    const uint8_t *data,
    size_t length,
    uint8_t digest[R1_SHA256_SIZE]
);

typedef bool (*r1_ecdsa_verify_fn)(
    void *context,
    const uint8_t digest[R1_SHA256_SIZE],
    const uint8_t signature[R1_SIGNATURE_SIZE],
    const uint8_t public_key[R1_PUBLIC_KEY_SIZE]
);

typedef struct {
    uint32_t expected_hardware_version;
    uint32_t current_firmware_version;
    uint32_t installed_softdevice_id;
    bool allow_signed_debug_policy;
} r1_validation_policy_t;

typedef struct {
    uint32_t hardware_version;
    uint32_t firmware_version;
    uint32_t required_softdevice_id;
    r1_image_type_t image_type;
    uint32_t image_size;
    bool is_debug;
    uint32_t signature_type;
    const uint8_t *signature;
    size_t signature_length;
    const uint8_t *signed_bytes;
    size_t signed_bytes_length;
} r1_init_command_t;

typedef struct {
    bool init_authenticated;
    uint32_t total_image_size;
    uint32_t firmware_offset;
    uint32_t object_start;
    uint32_t object_size;
    uint32_t object_written;
} r1_data_state_t;

typedef struct {
    uint32_t start;
    uint32_t length;
} r1_acl_range_t;

typedef struct {
    uint8_t opcode;
    uint8_t object_type;
    uint32_t size;
    uint16_t receipt_interval;
} r1_dfu_request_t;

uint32_t r1_crc32_compute(const uint8_t *data, size_t length, uint32_t previous_crc);

void r1_settings_reconcile(
    const r1_settings_t *primary,
    bool primary_crc_valid,
    const r1_settings_t *backup,
    bool backup_crc_valid,
    r1_settings_t *out
);

r1_result_t r1_validate_init_command(
    const r1_init_command_t *command,
    const r1_validation_policy_t *policy,
    const uint8_t public_key[R1_PUBLIC_KEY_SIZE],
    r1_sha256_fn sha256,
    r1_ecdsa_verify_fn verify,
    void *crypto_context
);

r1_result_t r1_data_object_create(r1_data_state_t *state, uint32_t object_size);
r1_result_t r1_data_object_write(r1_data_state_t *state, size_t fragment_size);
r1_result_t r1_data_object_execute(r1_data_state_t *state);

r1_result_t r1_postvalidate_image(
    const uint8_t *image,
    size_t image_length,
    const uint8_t expected_digest[R1_SHA256_SIZE],
    r1_sha256_fn sha256,
    void *crypto_context
);

r1_boot_action_t r1_choose_boot_action(
    bool force_dfu,
    bool application_valid,
    r1_image_type_t pending_image
);

size_t r1_application_handoff_acl(
    uint32_t application_start,
    uint32_t application_size,
    r1_acl_range_t ranges[2]
);

r1_result_t r1_parse_dfu_request(
    const uint8_t *packet,
    size_t packet_length,
    r1_dfu_request_t *request
);

bool r1_decode_bounded_varint(
    const uint8_t *buffer,
    size_t length,
    uint64_t *value,
    size_t *consumed
);

r1_result_t r1_copy_advertising_name(
    const r1_settings_t *settings,
    uint8_t output[R1_ADV_NAME_SIZE],
    size_t *output_length
);

#endif
