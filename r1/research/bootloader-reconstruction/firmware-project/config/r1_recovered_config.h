#ifndef R1_RECOVERED_CONFIG_H
#define R1_RECOVERED_CONFIG_H

/*
 * Product-specific values recovered from the retail R1 bootloader and the
 * firmware security audit. This header is force-included before Nordic's
 * unmodified sdk_config.h, whose settings use #ifndef guards.
 */

#define NRF_DFU_HW_VERSION 52
#define NRF_DFU_BLE_REQUIRES_BONDS 0

#define NRF_BL_DFU_ENTER_METHOD_BUTTON 0
#define NRF_BL_DFU_ENTER_METHOD_PINRESET 0
#define NRF_BL_DFU_ENTER_METHOD_GPREGRET 1
#define NRF_BL_DFU_ENTER_METHOD_BUTTONLESS 1

/* 36 flash pages below 0x000f8000 are retained for application data. */
#define NRF_DFU_APP_DATA_AREA_SIZE (36u * 4096u)

/* These remain explicit so a vendor config update cannot weaken DFU policy. */
#define NRF_DFU_REQUIRE_SIGNED_APP_UPDATE 1
#define NRF_DFU_SINGLE_BANK_APP_UPDATES 0
#define NRF_BL_APP_SIGNATURE_CHECK_REQUIRED 0

/* Matches the observed legacy-ring configuration. */
#define NRF_BL_DEBUG_PORT_DISABLE 0

/*
 * The captured image has Nordic's debug-validation behavior. It does not
 * remove ECDSA package verification, but it accepts an installed-app CRC
 * mismatch and relaxes version handling for signed debug init packets.
 * The hardened profile omits this define while preserving valid-input DFU.
 */
#if defined(R1_BUILD_PROFILE_CAPTURED) && R1_BUILD_PROFILE_CAPTURED
#define NRF_DFU_DEBUG_VERSION
#endif

#endif

