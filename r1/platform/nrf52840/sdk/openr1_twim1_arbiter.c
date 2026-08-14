#include "openr1_twim1_arbiter.h"

#include "FreeRTOS.h"
#include "cmsis_os2.h"

/*
 * See openr1_twim1_arbiter.h for the ownership contract. All state is static;
 * the CMSIS mutex serializes ownership transitions and in-flight transfers so
 * a dock-context handoff can never interrupt a transfer on the bus.
 */

static const nrfx_twim_t arbiter_twim = NRFX_TWIM_INSTANCE(1);
static osMutexId_t arbiter_mutex;
static StaticSemaphore_t arbiter_mutex_control_block;
static openr1_twim1_client bus_owner;

static bool valid_client(openr1_twim1_client client) {
    return client == OPENR1_TWIM1_CLIENT_MOTION ||
           client == OPENR1_TWIM1_CLIENT_NFC;
}

static bool lock_arbiter(void) {
    return arbiter_mutex != NULL &&
           osMutexAcquire(arbiter_mutex, osWaitForever) == osOK;
}

static void unlock_arbiter(void) {
    if (arbiter_mutex != NULL) {
        (void)osMutexRelease(arbiter_mutex);
    }
}

static nrfx_err_t bus_start(const nrfx_twim_config_t *configuration) {
    const nrfx_err_t error = nrfx_twim_init(
        &arbiter_twim, configuration, NULL, NULL);
    if (error == NRFX_SUCCESS) {
        nrfx_twim_enable(&arbiter_twim);
    }
    return error;
}

static void bus_stop(void) {
    nrfx_twim_disable(&arbiter_twim);
    nrfx_twim_uninit(&arbiter_twim);
}

ret_code_t openr1_twim1_arbiter_initialize(void) {
    if (arbiter_mutex != NULL) {
        return NRF_ERROR_INVALID_STATE;
    }
    static const osMutexAttr_t attributes = {
        .name = "openr1_twim1",
        .cb_mem = &arbiter_mutex_control_block,
        .cb_size = sizeof arbiter_mutex_control_block,
    };
    arbiter_mutex = osMutexNew(&attributes);
    if (arbiter_mutex == NULL) {
        return NRF_ERROR_NO_MEM;
    }
    bus_owner = OPENR1_TWIM1_CLIENT_NONE;
    return NRF_SUCCESS;
}

nrfx_err_t openr1_twim1_acquire(
    openr1_twim1_client client, const nrfx_twim_config_t *configuration) {
    if (!valid_client(client) || configuration == NULL) {
        return NRFX_ERROR_INVALID_PARAM;
    }
    if (!lock_arbiter()) {
        return NRFX_ERROR_INVALID_STATE;
    }
    nrfx_err_t error = NRFX_SUCCESS;
    if (bus_owner == client) {
        /* Idempotent re-acquire by the current owner. */
    } else if (bus_owner == OPENR1_TWIM1_CLIENT_NONE) {
        error = bus_start(configuration);
        if (error == NRFX_SUCCESS) {
            bus_owner = client;
        }
    } else if (client == OPENR1_TWIM1_CLIENT_NFC) {
        /* Documented handoff: the dock context preempts the worn context. */
        bus_stop();
        bus_owner = OPENR1_TWIM1_CLIENT_NONE;
        error = bus_start(configuration);
        if (error == NRFX_SUCCESS) {
            bus_owner = client;
        }
    } else {
        /* The worn context never preempts the dock context. */
        error = NRFX_ERROR_BUSY;
    }
    unlock_arbiter();
    return error;
}

nrfx_err_t openr1_twim1_release(openr1_twim1_client client) {
    if (!valid_client(client)) {
        return NRFX_ERROR_INVALID_PARAM;
    }
    if (!lock_arbiter()) {
        return NRFX_ERROR_INVALID_STATE;
    }
    nrfx_err_t error = NRFX_SUCCESS;
    if (bus_owner != client) {
        error = NRFX_ERROR_INVALID_STATE;
    } else {
        bus_stop();
        bus_owner = OPENR1_TWIM1_CLIENT_NONE;
    }
    unlock_arbiter();
    return error;
}

nrfx_err_t openr1_twim1_tx(openr1_twim1_client client, uint8_t address,
                           const uint8_t *data, size_t length, bool no_stop) {
    if (!valid_client(client) || (length != 0u && data == NULL)) {
        return NRFX_ERROR_INVALID_PARAM;
    }
    if (!lock_arbiter()) {
        return NRFX_ERROR_INVALID_STATE;
    }
    nrfx_err_t error = NRFX_SUCCESS;
    if (bus_owner != client) {
        error = NRFX_ERROR_BUSY;
    } else {
        error = nrfx_twim_tx(&arbiter_twim, address, data, length, no_stop);
    }
    unlock_arbiter();
    return error;
}

nrfx_err_t openr1_twim1_rx(openr1_twim1_client client, uint8_t address,
                           uint8_t *data, size_t length) {
    if (!valid_client(client) || (length != 0u && data == NULL)) {
        return NRFX_ERROR_INVALID_PARAM;
    }
    if (!lock_arbiter()) {
        return NRFX_ERROR_INVALID_STATE;
    }
    nrfx_err_t error = NRFX_SUCCESS;
    if (bus_owner != client) {
        error = NRFX_ERROR_BUSY;
    } else {
        error = nrfx_twim_rx(&arbiter_twim, address, data, length);
    }
    unlock_arbiter();
    return error;
}
