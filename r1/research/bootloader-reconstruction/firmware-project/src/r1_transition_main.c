/*
 * One-use BLE-to-source transition bootloader for an owner-authorized R1.
 *
 * The currently installed owner bootloader installs this image through normal
 * Nordic Secure DFU. This bootloader then accepts one exact owner-signed
 * application package containing the complete 0x00000..<0x27000 source boot
 * partition. On the following reset it verifies the staged length and CRC,
 * copies pages 1..38 first, copies page zero last, verifies the complete image,
 * and resets into source MCUboot. Until that exact payload exists it remains a
 * conventional owner-keyed Nordic BLE DFU bootloader.
 */

#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "app_error.h"
#include "app_error_weak.h"
#include "boards.h"
#include "crc32.h"
#include "nrf_bootloader.h"
#include "nrf_bootloader_app_start.h"
#include "nrf_bootloader_dfu_timers.h"
#include "nrf_bootloader_info.h"
#include "nrf_delay.h"
#include "nrf_dfu.h"
#include "nrf_dfu_settings.h"
#include "nrf_log.h"
#include "nrf_log_ctrl.h"
#include "nrf_log_default_backends.h"
#include "nrf_mbr.h"
#include "nrf_nvmc.h"

#ifndef R1_TRANSITION_IMAGE_BYTES
#error R1_TRANSITION_IMAGE_BYTES must be supplied by the audited packager
#endif
#ifndef R1_TRANSITION_IMAGE_CRC32
#error R1_TRANSITION_IMAGE_CRC32 must be supplied by the audited packager
#endif

#define R1_TRANSITION_PAGE_BYTES 0x1000u
#define R1_TRANSITION_SOURCE_LIMIT 0x000f8000u

static void reset_now(void) {
    __DSB();
    NVIC_SystemReset();
    for (;;) {
    }
}

static bool staged_source_image(uint32_t *source_address) {
    /* Read the two settings pages without initializing flash or rewriting
     * either page. Normal nrf_bootloader_init() owns that mutation later. */
    nrf_dfu_settings_reinit();
    if (s_dfu_settings.bank_1.bank_code != NRF_DFU_BANK_VALID_APP ||
        s_dfu_settings.bank_1.image_size != R1_TRANSITION_IMAGE_BYTES ||
        s_dfu_settings.bank_1.image_crc != R1_TRANSITION_IMAGE_CRC32) {
        return false;
    }
    const uint32_t source = s_dfu_settings.progress.update_start_address;
    if ((source & (R1_TRANSITION_PAGE_BYTES - 1u)) != 0u ||
        source < R1_TRANSITION_IMAGE_BYTES ||
        source > R1_TRANSITION_SOURCE_LIMIT - R1_TRANSITION_IMAGE_BYTES ||
        crc32_compute((const uint8_t *)source,
                      R1_TRANSITION_IMAGE_BYTES, NULL) !=
            R1_TRANSITION_IMAGE_CRC32) {
        return false;
    }
    *source_address = source;
    return true;
}

static bool copy_page(uint32_t destination, uint32_t source) {
    nrf_nvmc_page_erase(destination);
    nrf_nvmc_write_words(
        destination, (const uint32_t *)source,
        R1_TRANSITION_PAGE_BYTES / sizeof(uint32_t));
    return memcmp((const void *)destination, (const void *)source,
                  R1_TRANSITION_PAGE_BYTES) == 0;
}

static void install_source_boot_partition(uint32_t source) {
    for (uint32_t destination = R1_TRANSITION_PAGE_BYTES;
         destination < R1_TRANSITION_IMAGE_BYTES;
        destination += R1_TRANSITION_PAGE_BYTES) {
        if (!copy_page(destination, source + destination)) {
            reset_now();
        }
    }
    if (crc32_compute((const uint8_t *)R1_TRANSITION_PAGE_BYTES,
                      R1_TRANSITION_IMAGE_BYTES - R1_TRANSITION_PAGE_BYTES,
                      NULL) !=
        crc32_compute((const uint8_t *)(source + R1_TRANSITION_PAGE_BYTES),
                      R1_TRANSITION_IMAGE_BYTES - R1_TRANSITION_PAGE_BYTES,
                      NULL)) {
        reset_now();
    }

    /* Page zero is the only nonrecoverable BLE transition. Write it last. */
    if (!copy_page(0u, source)) {
        reset_now();
    }
    if (crc32_compute((const uint8_t *)0u, R1_TRANSITION_IMAGE_BYTES, NULL) ==
        R1_TRANSITION_IMAGE_CRC32) {
        reset_now();
    }
    reset_now();
}

static void on_error(void) {
    NRF_LOG_FINAL_FLUSH();
#if NRF_MODULE_ENABLED(NRF_LOG_BACKEND_RTT)
    nrf_delay_ms(100);
#endif
    reset_now();
}

void app_error_handler(uint32_t error_code, uint32_t line_num,
                       const uint8_t *file_name) {
    (void)error_code;
    NRF_LOG_ERROR("%s:%d", file_name, line_num);
    on_error();
}

void app_error_fault_handler(uint32_t id, uint32_t pc, uint32_t info) {
    NRF_LOG_ERROR("fault id=0x%08x pc=0x%08x info=0x%08x", id, pc, info);
    on_error();
}

void app_error_handler_bare(uint32_t error_code) {
    NRF_LOG_ERROR("error=0x%08x", error_code);
    on_error();
}

static void dfu_observer(nrf_dfu_evt_type_t event) {
    switch (event) {
        case NRF_DFU_EVT_DFU_FAILED:
        case NRF_DFU_EVT_DFU_ABORTED:
        case NRF_DFU_EVT_DFU_INITIALIZED:
            bsp_board_init(BSP_INIT_LEDS);
            break;
        default:
            break;
    }
}

int main(void) {
    /* Must precede settings access and flash protection, matching Nordic's
     * proven secure-bootloader entry sequence. */
    nrf_bootloader_mbr_addrs_populate();

    uint32_t source = 0u;
    if (staged_source_image(&source)) {
        install_source_boot_partition(source);
    }

    /* Stay in DFU until the exact transition payload has been received. */
    NRF_POWER->GPREGRET = BOOTLOADER_DFU_START;

    APP_ERROR_CHECK(nrf_bootloader_flash_protect(0u, MBR_SIZE));
    APP_ERROR_CHECK(nrf_bootloader_flash_protect(
        BOOTLOADER_START_ADDR, BOOTLOADER_SIZE));

    (void)NRF_LOG_INIT(nrf_bootloader_dfu_timer_counter_get);
    NRF_LOG_DEFAULT_BACKENDS_INIT();
    APP_ERROR_CHECK(nrf_bootloader_init(dfu_observer));
    APP_ERROR_CHECK_BOOL(false);
}
