#ifndef R1_SDK_OVERRIDES_H
#define R1_SDK_OVERRIDES_H

/* Evidence-backed R1 configuration deltas for the nRF5 SDK 17.1.0
 * pca10056_s140_ble secure-bootloader example. Include this file before
 * sdk_config.h (for GCC, add: CFLAGS += -include /absolute/r1_sdk_overrides.h).
 */

#define NRF_DFU_HW_VERSION 52
#define NRF_DFU_BLE_REQUIRES_BONDS 0

#define NRF_BL_DFU_ENTER_METHOD_BUTTON 0
#define NRF_BL_DFU_ENTER_METHOD_PINRESET 0
#define NRF_BL_DFU_ENTER_METHOD_GPREGRET 1
#define NRF_BL_DFU_ENTER_METHOD_BUTTONLESS 1

/* Retail live image uses 36 pages below 0xf8000, confirmed by the two-byte
 * 0xfb54e delta and by application flash-layout evidence. */
#define NRF_DFU_APP_DATA_AREA_SIZE (36u * 4096u)

/* Matches the observed legacy-revision ring configuration. A hardened product
 * should provision hardware debug protection independently. */
#define NRF_BL_DEBUG_PORT_DISABLE 0

/* The captured image was built with NRF_DFU_DEBUG_VERSION behavior, which
 * weakens installed-application CRC validation. It remains disabled in this
 * overlay by default. Define R1_REPRODUCE_CAPTURED_DEBUG_VALIDATION=1 only for
 * controlled behavioral comparison; signature verification remains compiled. */
#if defined(R1_REPRODUCE_CAPTURED_DEBUG_VALIDATION) && \
    R1_REPRODUCE_CAPTURED_DEBUG_VALIDATION
#define NRF_DFU_DEBUG_VERSION
#endif

#endif
