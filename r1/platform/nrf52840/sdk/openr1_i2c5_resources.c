#include "openr1_i2c5_resources.h"

#include <stdint.h>

#include "FreeRTOS.h"
#include "cmsis_os2.h"
#include "nrf_gpio.h"

#include "openr1_nfc.h"

#define OPENR1_NFC_BOARD_ENABLE_PIN NRF_GPIO_PIN_MAP(1, 10)
#define OPENR1_NFC_BOARD_SETTLE_TICKS UINT32_C(10)

static osMutexId_t i2c5_mutex;
static StaticSemaphore_t i2c5_mutex_control_block;
static bool nfc_board_enabled;

static void configure_nfc_board_enable(void) {
    nrf_gpio_cfg(
        OPENR1_NFC_BOARD_ENABLE_PIN,
        NRF_GPIO_PIN_DIR_OUTPUT,
        NRF_GPIO_PIN_INPUT_DISCONNECT,
        NRF_GPIO_PIN_PULLUP,
        NRF_GPIO_PIN_H0H1,
        NRF_GPIO_PIN_NOSENSE);
    nrf_gpio_pin_clear(OPENR1_NFC_BOARD_ENABLE_PIN);
    nfc_board_enabled = false;
}

static bool acquire_nfc_board_enable(void *context) {
    (void)context;
    if (i2c5_mutex == NULL || nfc_board_enabled) {
        return false;
    }
    nrf_gpio_pin_clear(OPENR1_NFC_BOARD_ENABLE_PIN);
    (void)osDelay(OPENR1_NFC_BOARD_SETTLE_TICKS);
    nrf_gpio_pin_set(OPENR1_NFC_BOARD_ENABLE_PIN);
    (void)osDelay(OPENR1_NFC_BOARD_SETTLE_TICKS);
    nfc_board_enabled = true;
    return true;
}

static void release_nfc_board_enable(void *context) {
    (void)context;
    nrf_gpio_pin_clear(OPENR1_NFC_BOARD_ENABLE_PIN);
    nfc_board_enabled = false;
}

static bool acquire_nfc_i2c5(void *context) {
    (void)context;
    return openr1_i2c5_try_acquire();
}

static void release_nfc_i2c5(void *context) {
    (void)context;
    openr1_i2c5_release();
}

static const openr1_nfc_resource_ops nfc_resources = {
    acquire_nfc_board_enable,
    release_nfc_board_enable,
    acquire_nfc_i2c5,
    release_nfc_i2c5,
};

ret_code_t openr1_i2c5_resources_initialize(void) {
    if (i2c5_mutex != NULL) {
        return NRF_ERROR_INVALID_STATE;
    }
    static const osMutexAttr_t attributes = {
        .name = "openr1_i2c5",
        .cb_mem = &i2c5_mutex_control_block,
        .cb_size = sizeof i2c5_mutex_control_block,
    };
    i2c5_mutex = osMutexNew(&attributes);
    if (i2c5_mutex == NULL) {
        return NRF_ERROR_NO_MEM;
    }
    configure_nfc_board_enable();
    const ret_code_t error = openr1_nfc_bind_resources(
        &nfc_resources, NULL);
    if (error != NRF_SUCCESS) {
        return error;
    }
    return NRF_SUCCESS;
}

bool openr1_i2c5_try_acquire(void) {
    return i2c5_mutex != NULL &&
           osMutexAcquire(i2c5_mutex, 0u) == osOK;
}

void openr1_i2c5_release(void) {
    if (i2c5_mutex != NULL) {
        (void)osMutexRelease(i2c5_mutex);
    }
}
