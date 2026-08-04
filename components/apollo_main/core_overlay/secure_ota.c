/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 secure-OTA addition routine adapted from AmbiqSuite SDK
 * 5.1.0 and matched to stock 0x00475230...0x00475285.
 */

typedef __UINTPTR_TYPE__ open_cfw_secure_ota_uintptr;

#define OPEN_CFW_SECURE_OTA_MRAM_BASE 0x00400000U
#define OPEN_CFW_SECURE_OTA_MAX_IMAGES 8U
#define OPEN_CFW_SECURE_OTA_PENDING 3U
#define OPEN_CFW_SECURE_OTA_VALID 1U
#define OPEN_CFW_SECURE_OTA_STATUS_SUCCESS 0U
#define OPEN_CFW_SECURE_OTA_STATUS_OUT_OF_RANGE 5U
#define OPEN_CFW_SECURE_OTA_STATUS_INVALID_ARGUMENT 6U

#define OPEN_CFW_SECURE_OTA_STATE_DEFAULT_ADDRESS 0x20073F54U
#define OPEN_CFW_SECURE_OTA_POINTER_REGISTER 0x40020264U
#define OPEN_CFW_SECURE_OTA_PROGRAM_WORDS_ENTRY 0x004D09D9U

typedef struct {
    unsigned int mram_size;
    unsigned int descriptor_address;
    unsigned int image_count;
} open_cfw_secure_ota_state;

#ifndef OPEN_CFW_SECURE_OTA_STATE_ADDRESS
#define OPEN_CFW_SECURE_OTA_STATE_ADDRESS \
    OPEN_CFW_SECURE_OTA_STATE_DEFAULT_ADDRESS
#endif

#ifndef OPEN_CFW_SECURE_OTA_READ
#define OPEN_CFW_SECURE_OTA_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_SECURE_OTA_WRITE
#define OPEN_CFW_SECURE_OTA_WRITE(address, value) \
    (*(volatile unsigned int *)(address) = (value))
#endif

#ifndef OPEN_CFW_SECURE_OTA_PROGRAM_WORDS
typedef unsigned int (*open_cfw_secure_ota_program_words_function)(
    unsigned int,
    unsigned int *,
    unsigned int *,
    unsigned int
);
#define OPEN_CFW_SECURE_OTA_PROGRAM_WORDS( \
    key, source, destination, count \
) \
    (((open_cfw_secure_ota_program_words_function) \
        OPEN_CFW_SECURE_OTA_PROGRAM_WORDS_ENTRY)( \
            (key), (source), (destination), (count) \
        ))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite am_hal_ota_add. The
 * image_magic byte is part of the public ABI but is intentionally unused by
 * both the SDK and reviewed stock body.
 */
__attribute__((used, noinline))
unsigned int open_cfw_secure_ota_add(
    unsigned int program_key,
    unsigned char image_magic,
    unsigned int *image
)
{
    volatile open_cfw_secure_ota_state *state =
        (volatile open_cfw_secure_ota_state *)
            (open_cfw_secure_ota_uintptr)
                OPEN_CFW_SECURE_OTA_STATE_ADDRESS;
    unsigned int image_address =
        (unsigned int)(open_cfw_secure_ota_uintptr)image;
    unsigned int image_index;
    unsigned int status;

    (void)image_magic;

    if (
        image_address >
            OPEN_CFW_SECURE_OTA_MRAM_BASE + state->mram_size ||
        image_address < OPEN_CFW_SECURE_OTA_MRAM_BASE
    ) {
        return OPEN_CFW_SECURE_OTA_STATUS_INVALID_ARGUMENT;
    }
    if (state->image_count == OPEN_CFW_SECURE_OTA_MAX_IMAGES) {
        return OPEN_CFW_SECURE_OTA_STATUS_OUT_OF_RANGE;
    }

    image_address |= OPEN_CFW_SECURE_OTA_PENDING;
    image_index = state->image_count;
    state->image_count = image_index + 1U;
    status = OPEN_CFW_SECURE_OTA_PROGRAM_WORDS(
        program_key,
        &image_address,
        (unsigned int *)(open_cfw_secure_ota_uintptr)(
            state->descriptor_address + image_index * 4U
        ),
        1U
    );
    if (status == OPEN_CFW_SECURE_OTA_STATUS_SUCCESS) {
        OPEN_CFW_SECURE_OTA_WRITE(
            OPEN_CFW_SECURE_OTA_POINTER_REGISTER,
            OPEN_CFW_SECURE_OTA_READ(
                OPEN_CFW_SECURE_OTA_POINTER_REGISTER
            ) | OPEN_CFW_SECURE_OTA_VALID
        );
    }
    return status;
}
