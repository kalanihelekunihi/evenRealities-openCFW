/***************************************************************************//**
* \file cy_capsense_structure.h
* \version 6.10.0
*
* \brief
* This file provides the top-level declarations of the CAPSENSE&trade; data
* structure. Also, the file declares the functions for data access.
*
********************************************************************************
* \copyright
* Copyright 2018-2025, Cypress Semiconductor Corporation (an Infineon company)
* or an affiliate of Cypress Semiconductor Corporation. All rights reserved.
* You may use this file only in accordance with the license, terms, conditions,
* disclaimers, and limitations in the end user license agreement accompanying
* the software package with which this file was provided.
*******************************************************************************/


#if !defined(CY_CAPSENSE_STRUCTURE_H)
#define CY_CAPSENSE_STRUCTURE_H

#include "cy_syslib.h"
#include "cy_device_headers.h"
#include "cycfg_capsense_defines.h"
#include "cy_capsense_lib.h"
#include "cy_capsense_gesture_lib.h"
#include "cy_capsense_common.h"
#if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
    #include "cy_csd.h"
#elif (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
    #include "cy_msclp.h"
#else /* (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) */
    #include "cy_msc.h"
#endif

#if (defined(CY_IP_MXCSDV2) || defined(CY_IP_M0S8CSDV2) || defined(CY_IP_M0S8MSCV3) || defined(CY_IP_M0S8MSCV3LP))

#if defined(__cplusplus)
extern "C" {
#endif


/*******************************************************************************
* CAPSENSE&trade; Enumerated Types
*******************************************************************************/

/******************************************************************************/
/** \addtogroup group_capsense_enums *//** \{ */
/******************************************************************************/

/** Defines MW Tuner module states */
typedef enum
{
    CY_CAPSENSE_TU_FSM_RUNNING          = 0x00u,                /**< Running state is a state when CAPSENSE&trade; middleware is not
                                                                   * blocked by the CAPSENSE&trade; Tuner tool and application program continuously scans */
    CY_CAPSENSE_TU_FSM_SUSPENDED        = 0x01u,                /**< Scanning is suspended */
    CY_CAPSENSE_TU_FSM_ONE_SCAN         = 0x03u,                /**< Scanning is suspended after one scan cycle */
} cy_en_capsense_tuner_state_t;

/** Defines the Tuner command codes */
typedef enum
{
    CY_CAPSENSE_TU_CMD_NONE_E                    = 0u,          /**< No command */
    CY_CAPSENSE_TU_CMD_SUSPEND_E                 = 1u,          /**< Suspend command */
    CY_CAPSENSE_TU_CMD_RESUME_E                  = 2u,          /**< Resume command switches state from suspend to running */
    CY_CAPSENSE_TU_CMD_RESTART_E                 = 3u,          /**< Restart command requests to perform CAPSENSE&trade; re-initialization and switches state to running */
    CY_CAPSENSE_TU_CMD_RUN_SNR_TEST_E            = 4u,          /**< Reserved */
    CY_CAPSENSE_TU_CMD_PING_E                    = 5u,          /**< Ping command to check whether application program calls Cy_CapSense_RunTuner() */
    CY_CAPSENSE_TU_CMD_ONE_SCAN_E                = 6u,          /**< Execute one scan cycle and then switch to suspend state */
    CY_CAPSENSE_TU_CMD_WRITE_E                   = 7u,          /**< Writes specified data with offset into cy_capsense_tuner */
    CY_CAPSENSE_TU_CMD_COMM_DIS_E                = 8u,          /**< Disables the communication mode (used in the fifth-generation low power CAPSENSE&trade; only):
                                                                 * * Low power sensors rawcounts does not copied to communication structure
                                                                 * * Communication of CapSense data structure to Tuner does not happen (in case of UART or protocol-agnostic method) */
    CY_CAPSENSE_TU_CMD_COMM_EN_E                 = 9u,                   /**< Enables the communication mode (used in the fifth-generation low power CAPSENSE&trade; only):
                                                                 * * Low power sensors rawcounts are copied to communication structure
                                                                 * * Data is transferred to Tuner (in case of UART or protocol-agnostic method) */
    CY_CAPSENSE_TU_CMD_RESTART_ONLY_E            = 10u,         /**< Restart command requests to perform CAPSENSE&trade; re-initialization and keeps state unchanged */
    CY_CAPSENSE_TU_CMD_SET_DUTY_CYCLE_AND_SCAN_E = 11u,         /**< Sets duty cycle and executes one scan (used only when foam-rejection is enabled for LLW) */
    CY_CAPSENSE_TU_CMD_LAST_E                    = 12u,         /**< The last command */
} cy_en_capsense_tuner_cmd_t;

/** Defines widget types */
typedef enum
{
    CY_CAPSENSE_WD_BUTTON_E             = 0x01u,                /**< Button widget */
    CY_CAPSENSE_WD_LINEAR_SLIDER_E      = 0x02u,                /**< Linear Slider widget */
    CY_CAPSENSE_WD_RADIAL_SLIDER_E      = 0x03u,                /**< Radial Slider widget */
    CY_CAPSENSE_WD_MATRIX_BUTTON_E      = 0x04u,                /**< Matrix Buttons widget */
    CY_CAPSENSE_WD_TOUCHPAD_E           = 0x05u,                /**< Touchpad widget */
    CY_CAPSENSE_WD_PROXIMITY_E          = 0x06u,                /**< Proximity widget */
    CY_CAPSENSE_WD_LOW_POWER_E          = 0x07u,                /**< Low Power widget, used in the fifth-generation low power CAPSENSE&trade; only */
    CY_CAPSENSE_WD_LIQUID_LEVEL_E       = 0x08u,                /**< Liquid level widget, used in the fifth-generation low power CAPSENSE&trade; only */
    CY_CAPSENSE_WD_LIQUID_DETECTION_E   = 0x09u,                /**< Liquid detection widget, used in the fifth-generation low power CAPSENSE&trade; only */
} cy_en_capsense_widget_type_t;

/** Defines CAPSENSE&trade; return statuses types */
typedef enum
{
    CY_CAPSENSE_SUCCESS_E               = 0x00u,                /**< The success return status */
    CY_CAPSENSE_BAD_PARAM_E             = 0x01u,                /**< One or more invalid input parameters  */
    CY_CAPSENSE_HW_LOCKED_E             = 0x02u,                /**< The sensing HW block is captured by another middleware */
    CY_CAPSENSE_HW_BUSY_E               = 0x03u,                /**< The sensing HW block is busy by previous operation */
    CY_CAPSENSE_TIMEOUT_E               = 0x04u,                /**< The sensing HW block operation was not finished correctly */
} cy_en_capsense_return_status_t;

/** Defines types of electrode */
typedef enum
{
    CY_CAPSENSE_ELTD_TYPE_SELF_E        = 0x01u,                /**< Electrode used as a sensor in CSD sensing method */
    CY_CAPSENSE_ELTD_TYPE_MUT_TX_E      = 0x02u,                /**< Electrode used as a TX in CSX sensing method */
    CY_CAPSENSE_ELTD_TYPE_MUT_RX_E      = 0x03u,                /**< Electrode used as a RX in CSX sensing method */
} cy_en_capsense_eltd_t;


/** Defines connections of sensing capacitors */
typedef enum
{
    CY_CAPSENSE_CMODPAD_E               = 0x01u,                /**< External capacitor is connected to dedicated CMOD pad */
    CY_CAPSENSE_CTANKPAD_E              = 0x02u,                /**< External capacitor is connected to dedicated CSH pad */
    CY_CAPSENSE_CSHIELDPAD_E            = 0x03u,                /**< External capacitor is connected to dedicated SHIELD pad */
    CY_CAPSENSE_VREFEXTPAD_E            = 0x04u,                /**< External capacitor is connected to dedicated VREF pad */
} cy_en_capsense_cap_connection_t;


/** Defines CAPSENSE&trade; middleware execution events
  * when the CAPSENSE&trade; callback can be executed. */
typedef enum
{
    CY_CAPSENSE_START_SAMPLE_E          = 0x01u,                /**< Start Sample Callback. The callback will be executed before each sensor
                                                                   *scan triggering */
    CY_CAPSENSE_END_OF_SCAN_E           = 0x02u,                /**< End Of Scan Callback. The callback will be executed when sensor scan
                                                                   * is finished and there is no other sensors in the queue to be scanned. */
} cy_en_capsense_callback_event_t;


/** Defines HW configurations types for BIST operations */
typedef enum
{
    CY_CAPSENSE_BIST_HW_UNDEFINED_E     = 0x00u,                /**< Initialization or releasing of the CAPSENSE&trade; HW block */
    CY_CAPSENSE_BIST_HW_SHORT_E         = 0x01u,                /**< Short tests */
    CY_CAPSENSE_BIST_HW_ELTD_CAP_E      = 0x02u,                /**< Sensor and shield electrodes capacitance measurements with disabled shield */
    CY_CAPSENSE_BIST_HW_EXTERNAL_CAP_E  = 0x03u,                /**< External capacitors capacitance measurements */
    CY_CAPSENSE_BIST_HW_VDDA_E          = 0x04u,                /**< VDDA measurement */
    CY_CAPSENSE_BIST_HW_ELTD_CAP_SH_E   = 0x05u,                /**< Sensor electrodes capacitance measurements with configured shield */
} cy_en_capsense_bist_hw_config_t;


/** Defines BIST IO Configuration */
typedef enum
{
    CY_CAPSENSE_BIST_IO_UNDEFINED_E        = 0x00u,             /**< The undefined state. Pins are disconnected from AMuxBus */
    CY_CAPSENSE_BIST_IO_STRONG_E           = 0x01u,             /**< The drive mode is set to Strong in off - Low.
                                                                   * The HSIOM is set to GPIO */
    CY_CAPSENSE_BIST_IO_HIGHZA_E           = 0x02u,             /**< The drive mode is set to High-Z.
                                                                   * The HSIOM is set to GPIO */
    CY_CAPSENSE_BIST_IO_SENSE_E            = 0x03u,             /**< The drive mode is set to High-Z/Strong in off (depending on the device platform).
                                                                   * The HSIOM is set to CSD sense connection. */
    CY_CAPSENSE_BIST_IO_SHIELD_E           = 0x04u,             /**< The drive mode is set to High-Z/Strong in off (depending on the device platform).
                                                                   * The HSIOM is set to CSD shield connection. */
    CY_CAPSENSE_BIST_IO_STRONG_HIGH_E      = 0x05u,             /**< The drive mode is set to Strong in off - High.
                                                                   * The HSIOM is set to GPIO */
    CY_CAPSENSE_BIST_IO_VDDA2_E            = 0x06u,             /**< The drive mode is set to High-Z/Strong in off.
                                                                   * The HSIOM is set to VDDA/2 */
} cy_en_capsense_bist_io_state_t;


/** Defines BIST result statuses */
typedef enum
{
    CY_CAPSENSE_BIST_SUCCESS_E             = 0x00u,             /**< The success test status */
    CY_CAPSENSE_BIST_BAD_PARAM_E           = 0x01u,             /**< The bad input parameters test status */
    CY_CAPSENSE_BIST_HW_BUSY_E             = 0x02u,             /**< The CAPSENSE&trade; HW block is busy by previous operation */
    CY_CAPSENSE_BIST_LOW_LIMIT_E           = 0x03u,             /**< The status for a low limit reached during the test */
    CY_CAPSENSE_BIST_HIGH_LIMIT_E          = 0x04u,             /**< The status for a high limit reached during the test */
    CY_CAPSENSE_BIST_ERROR_E               = 0x05u,             /**< The status for an error occurred during the test.
                                                                     The test is not completed */
    CY_CAPSENSE_BIST_FEATURE_DISABLED_E    = 0x06u,             /**< The BIST feature is disabled. */
    CY_CAPSENSE_BIST_TIMEOUT_E             = 0x07u,             /**< The status for a timeout occurred during the test */
    CY_CAPSENSE_BIST_BAD_CONFIG_E          = 0x08u,             /**< The bad configuration parameters test status */
    CY_CAPSENSE_BIST_FAIL_E                = 0x0Fu,             /**< The failed test status */
} cy_en_capsense_bist_status_t;

#if ((CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
/** Defines IDs of the external capacitors */
typedef enum
{
    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        CY_CAPSENSE_BIST_CMOD01_ID_E         = 0x00u,                /**< ID for the MSC0 Cmod1 external capacitor \note This value is available for the fifth-generation low power CAPSENSE&trade;.*/
        CY_CAPSENSE_BIST_CMOD02_ID_E         = 0x01u,                /**< ID for the MSC0 Cmod2 external capacitor \note This value is available for the fifth-generation low power CAPSENSE&trade;.*/
    #endif
    #if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
        CY_CAPSENSE_BIST_CMOD_ID_E           = 0x00u,                /**< ID for Cmod external capacitor \note This value is available only for the fourth-generation CAPSENSE&trade;.*/
        CY_CAPSENSE_BIST_CINTA_ID_E          = 0x01u,                /**< ID for CintA external capacitor \note This value is available only for the fourth-generation CAPSENSE&trade;.*/
        CY_CAPSENSE_BIST_CINTB_ID_E          = 0x02u,                /**< ID for CintB external capacitor \note This value is available only for the fourth-generation CAPSENSE&trade;.*/
        CY_CAPSENSE_BIST_CSH_ID_E            = 0x03u,                /**< ID for Csh external capacitor \note This value is available only for the fourth-generation CAPSENSE&trade;.*/
    #endif
} cy_en_capsense_bist_external_cap_id_t;
#endif

/** Defines the raw count accumulation mode for MSC HW block */
typedef enum
{
    CY_CAPSENSE_MSC_RAW_SATURATE_E         = 0x00u,             /**< In this scenario, RAW_COUNT is clamped at 0xFFFF and RESULT_FIFO_RD.OVERFLOW is set. */
    CY_CAPSENSE_MSC_RAW_OVERFLOW_E         = 0x01u,             /**< In this scenario, RAW_COUNT rolls over and RESULT_FIFO_RD.OVERFLOW is set. This mode allows more sensitive tuning if measuring baseline capacitance */
} cy_en_capsense_msc_raw_mode_t;

/** \} */


/*******************************************************************************
* CAPSENSE&trade; Data Structures
*******************************************************************************/

/******************************************************************************/
/** \addtogroup group_capsense_structures *//** \{ */
/******************************************************************************/

/** Unified return status of CAPSENSE&trade; operation:
 * * CY_CAPSENSE_STATUS_SUCCESS
 * * CY_CAPSENSE_STATUS_BAD_PARAM
 * * CY_CAPSENSE_STATUS_BAD_DATA
 * * CY_CAPSENSE_STATUS_TIMEOUT
 * * CY_CAPSENSE_STATUS_INVALID_STATE
 * * CY_CAPSENSE_STATUS_BAD_CONFIG
 * * CY_CAPSENSE_STATUS_CONFIG_OVERFLOW
 * * CY_CAPSENSE_STATUS_HW_BUSY
 */
typedef uint32_t cy_capsense_status_t;

/** Unified return state of CAPSENSE&trade; Middleware:
 *
 * * CY_CAPSENSE_MW_STATE_BIST_MASK               - The BIST is in progress.
 *                                                  The next scan frame cannot be started.
 * * CY_CAPSENSE_MW_STATE_CALIBRATION_MASK        - The auto-calibration is in progress.
 *                                                  The next scan frame cannot be started.
 * * CY_CAPSENSE_MW_STATE_SMARTSENSE_MASK         - The smart sensing algorithm is
 *                                                  in progress.
 *                                                  The next scan frame cannot be started.
 * * CY_CAPSENSE_MW_STATE_INITIALIZATION_MASK     - Middleware initialization is
 *                                                  in progress and a next scan frame
 *                                                  can be initiated.
 * * CY_CAPSENSE_MW_STATE_SCAN_SLOT_MASK[x]       - The set [x] number of the result
 *                                                  means that the previously initiated
 *                                                  scan for the [x] slot is completed
 *                                                  or in progress. In CS-DMA mode, this
 *                                                  field is set only for the first
 *                                                  scanned slot.
 */
typedef uint32_t cy_capsense_mw_state_t;

/** Sensor context structure */
typedef struct
{
    uint16_t raw;                                               /**< Sensor raw count */
    uint16_t bsln;                                              /**< Sensor baseline */
    uint16_t diff;                                              /**< Sensor difference count */
    uint8_t status;                                             /**< Sensor status, contains masks:
                                                                   * * bit[0] - Regular Sensor Touched (CY_CAPSENSE_SNS_TOUCH_STATUS_MASK) or Proximity Sensor is active (CY_CAPSENSE_SNS_PROX_STATUS_MASK)
                                                                   * * bit[1] - Proximity Sensor Touched  (CY_CAPSENSE_SNS_TOUCH_PROX_STATUS_MASK)
                                                                   * * bit[2] - Overflow during scanning (CY_CAPSENSE_SNS_OVERFLOW_MASK) */
    uint8_t negBslnRstCnt;                                      /**< Negative baseline reset counter */
    #if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
        uint8_t idacComp;                                       /**< Compensation IDAC of CSD or IDAC in CSX
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
    #endif
    uint8_t bslnExt;                                            /**< Sensor baseline fractional */
    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN || CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        uint8_t cdacComp;                                       /**< Compensation CDAC
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN || CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */
} cy_stc_capsense_sensor_context_t;

/** CSX Touchpad touch tracking history */
typedef struct
{
    uint32_t velocity;                                          /**< The square of the "speed" (maximum distance change per refresh interval) threshold
                                                                   * distinguishing a fast finger movement from separate finger touches
                                                                   * (in [pixels/refresh interval]).
                                                                   * Squared speeds exceeding this value indicate separate finger touches.
                                                                   * Squared speeds below this value indicate fast single finger movement. */
    cy_stc_capsense_position_t oldPeak[CY_CAPSENSE_CSX_TOUCHPAD_MAX_PEAKS];
                                                                /**< Touch Positions */
    uint8_t oldPeakNumber;                                      /**< Number of detected peaks */
    uint8_t oldActiveIdsMask;                                   /**< Mask of used IDs */
} cy_stc_capsense_csx_touch_history_t;

/** Internal CSX Touchpad buffer structure for CSX for Touchpads' processing */
typedef struct
{
    int32_t distanceMap[CY_CAPSENSE_CSX_TOUCHPAD_MAX_PEAKS * CY_CAPSENSE_CSX_TOUCHPAD_MAX_PEAKS];
                                                                /**< Buffer for distance map data */
    int32_t colMap[CY_CAPSENSE_CSX_TOUCHPAD_MAX_PEAKS];         /**< Buffer for column map data */
    int32_t rowMap[CY_CAPSENSE_CSX_TOUCHPAD_MAX_PEAKS];         /**< Buffer for row map data */
    int32_t minsMap[CY_CAPSENSE_CSX_TOUCHPAD_MAX_PEAKS];        /**< Buffer for minimums map data */
    cy_stc_capsense_position_t newPeak[CY_CAPSENSE_CSX_TOUCHPAD_MAX_PEAKS];
                                                                /**< Touch Positions */
    int8_t fingerPosIndexMap[CY_CAPSENSE_CSX_TOUCHPAD_MAX_PEAKS + 3u];
                                                                /**< Buffer for index map data */
    int8_t linksMap[CY_CAPSENSE_CSX_TOUCHPAD_MAX_PEAKS];        /**< Buffer for linked map data */
    int8_t visitedMap[CY_CAPSENSE_CSX_TOUCHPAD_MAX_PEAKS];      /**< Buffer for visited map data */
    int8_t markIndicesMap[CY_CAPSENSE_CSX_TOUCHPAD_MAX_PEAKS];  /**< Buffer for mark map data */
    uint8_t newPeakNumber;                                      /**< Number of detected peaks */
    uint8_t newActiveIdsMask;                                   /**< Mask of used IDs */
} cy_stc_capsense_csx_touch_buffer_t;

/** Widget context structure */
typedef struct
{
    uint16_t fingerCap;                                         /**< Touch sensitivity used when full auto-tuning mode is enabled:
                                                                   * * For CSD widgets is a finger capacitance introduced at touch
                                                                   * * For ISX widgets is a coil inductance change at touch */
    uint16_t sigPFC;                                            /**< The 75% of signal per the user-defined touch sensitivity parameter */
    #if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
        uint16_t resolution;                                    /**< Provides scan resolution for the CSD Widgets.
                                                                 * Provides number of sub-conversions for the CSX Widgets
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    #endif
    uint16_t maxRawCount;                                       /**< Calculated maximum raw count of widget */
    uint16_t maxRawCountRow;                                    /**< Calculated row maximum raw count of widget */
    uint16_t fingerTh;                                          /**< Widget Finger Threshold */
    uint16_t proxTh;                                            /**< Widget Proximity Threshold or Foam Correction Coefficient for Liquid level widget */
    uint16_t lowBslnRst;                                        /**< The widget low baseline reset count. Specifies the number
                                                                   * of samples the sensor signal must be below the Negative
                                                                   * Noise Threshold \ref nNoiseTh to trigger a baseline reset */
    uint16_t snsClk;                                            /**< Sense Clock Divider. For the Matrix Buttons and Touchpad widgets
                                                                   * specifies the column sense clock divider */
    uint16_t rowSnsClk;                                         /**< Row Sense Clock Divider for the Matrix Buttons and Touchpad widgets */
    uint16_t gestureDetected;                                   /**< Mask of detected gestures */
    uint16_t gestureDirection;                                  /**< Mask of directions of detected gestures */
    int16_t xDelta;                                             /**< The filtered by Ballistic Multiplier X-displacement */
    int16_t yDelta;                                             /**< The filtered by Ballistic Multiplier Y-displacement */
    uint16_t noiseTh;                                           /**< Widget Noise Threshold */
    uint16_t nNoiseTh;                                          /**< Widget Negative Noise Threshold */
    uint16_t hysteresis;                                        /**< Widget Hysteresis for the signal crossing finger threshold */
    uint8_t onDebounce;                                         /**< Widget Debounce for the signal above the finger threshold 1 to 255.
                                                                   * * 1 - touch reported immediately as soon as detected
                                                                   * * 2 - touch reported on the second consecutive detection
                                                                   * * 3 - touch reported on the third consecutive detection */
    uint8_t snsClkSource;                                       /**< Widget clock source.
                                                                   * For fourth-generation CAPSENSE&trade;:
                                                                   * * bit[7] - Indicates auto mode of clock source selection
                                                                   * * bit[0:6] - Clock source:
                                                                   *   * 0 - Direct (CY_CAPSENSE_CLK_SOURCE_DIRECT)
                                                                   *   * 1 - SSC6 (CY_CAPSENSE_CLK_SOURCE_SSC6)
                                                                   *   * 2 - SSC7 (CY_CAPSENSE_CLK_SOURCE_SSC7)
                                                                   *   * 3 - SSC9 (CY_CAPSENSE_CLK_SOURCE_SSC9)
                                                                   *   * 4 - SSC10 (CY_CAPSENSE_CLK_SOURCE_SSC10)
                                                                   *   * 5 - PRS8 (CY_CAPSENSE_CLK_SOURCE_PRS8)
                                                                   *   * 6 - PRS12 (CY_CAPSENSE_CLK_SOURCE_PRS12)
                                                                   *
                                                                   * For fifth-generation and fifth-generation low power CAPSENSE&trade;:
                                                                   * bit[3] - Indicates auto mode of PRS clock source
                                                                   * bit[2] - Indicates auto mode of SSC clock source
                                                                   * * bit[0:1] - Clock source:
                                                                   *   * 0 - Direct (CY_CAPSENSE_CLK_SOURCE_DIRECT)
                                                                   *   * 1 - SSC (CY_CAPSENSE_CLK_SOURCE_SSC)
                                                                   *   * 2 - PRS (CY_CAPSENSE_CLK_SOURCE_PRS)
                                                                   */
    #if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
        uint8_t idacMod[CY_CAPSENSE_MAX_SUPPORTED_FREQ_NUM];         /**< Sets the current of the modulation IDAC for the CSD widgets.
                                                                * For the CSD Touchpad and Matrix Button widgets sets the current of the
                                                                * modulation IDAC for the column sensors. Not used for the CSX widgets.
                                                                * \note This field is available only for the fourth-generation CAPSENSE&trade;.*/
        uint8_t idacGainIndex;                                  /**< Index of IDAC gain in table \ref cy_stc_capsense_idac_gain_table_t
                                                                * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                *  */
        uint8_t rowIdacMod[CY_CAPSENSE_MAX_SUPPORTED_FREQ_NUM];      /**< Sets the current of the modulation IDAC for the row sensors
                                                                * for the CSD Touchpad and Matrix Button widgets. Not used for the CSX widgets.
                                                                * \note This field is available only for the fourth-generation CAPSENSE&trade;.*/
    #endif
    uint8_t bslnCoeff;                                          /**< Baseline IIR filter coefficient. Lower value leads to higher filtering. */
    uint8_t status;                                             /**< Contains masks:
                                                                   * * bit[0] - Widget Active (CY_CAPSENSE_WD_ACTIVE_MASK)
                                                                   * * bit[1] - Widget Enable (CY_CAPSENSE_WD_ENABLE_MASK)
                                                                   * * bit[2] - Widget Working (CY_CAPSENSE_WD_WORKING_MASK)
                                                                   * * bit[3] - Widget maximum raw count calculation enabled (CY_CAPSENSE_WD_MAXCOUNT_CALC_MASK)
                                                                   * * bit[4] - Widget row maximum raw count calculation enable (CY_CAPSENSE_WD_MAXCOUNT_ROW_CALC_MASK) */
    cy_stc_capsense_touch_t wdTouch;                            /**< Widget touch structure used for Matrix Buttons, Sliders, and Touchpads */

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
        uint16_t numSubConversions;                             /**< Number of sub-conversions in a scan
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint8_t cdacRef;                                        /**< Sets the capacitance of the reference CDAC
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint8_t rowCdacRef;                                     /**< Sets the capacitance of the row reference CDAC for CSD
                                                                 * Touchpad and CSD Matrix buttons widgets
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */

        #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP) && \
             ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_FINE_EN) || \
              (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CDAC_FINE_EN) || \
              (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CDAC_FINE_EN)))
            uint8_t cdacFine;                                   /**< Sets the capacitance of the fine CDAC
                                                                 * \note This field is available for the fifth-generation low power CAPSENSE&trade;.
                                                                 */
            uint8_t rowCdacFine;                                /**< Sets the capacitance of the row fine CDAC for CSD
                                                                 * Touchpad and CSD Matrix buttons widgets
                                                                 * \note This field is available for the fifth-generation low power CAPSENSE&trade;.
                                                                 */
        #endif

        uint8_t cicRate;                                        /**< Sets decimation rate when CIC2 is enabled
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN)
            uint8_t cdacDitherEn;                                   /**< Enabled CDAC dithering
                                                                     * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                     */
        #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN */

        uint8_t cdacDitherValue;                                /**< CDAC dither scale value in bits
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint8_t coarseInitBypassEn;                             /**< Skip Cmod coarse initialization sensors scan within widget
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint16_t cdacCompDivider;                               /**< Number of time DAC switched in sense clock period
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint8_t lfsrBits;                                       /**< Defines the number of LSB bits to use by the LSFR unit to achieve
                                                                 *   the desired clock dithering variation.
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN || CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */
    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        uint8_t cicShift;                                       /**< Sets the right shift value applied to CIC2 accumulator to form rawcounts when CIC2 is enabled
                                                                 * \note This field is available for the fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint8_t rowCicShift;                                       /**< Sets the right shift value applied to CIC2 accumulator to form rawcounts when CIC2 is enabled
                                                                 * \note This field is available for the fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif

} cy_stc_capsense_widget_context_t;

/** Legacy mode pin configuration structure */
typedef struct
{
    GPIO_PRT_Type * pcPtr;                                      /**< Pointer to the base port register of the IO */
    uint8_t pinNumber;                                          /**< Position of the IO in the port */

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
        uint8_t padNumber;                                      /**< Control Mux pad number
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN)
        uint8_t chId;                                           /**< Channel Id the pin belongs to
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
    #endif

} cy_stc_capsense_pin_config_t;

/** Electrode objects configuration structure */
typedef struct
{
    const cy_stc_capsense_pin_config_t * ptrPin;                /**< Pointer to pin configuration structure */
    uint8_t type;                                               /**< Electrode type \ref cy_en_capsense_eltd_t */
    uint8_t numPins;                                            /**< Total number of pins in this sensor */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN)
        uint8_t chId;                                           /**< Channel Id the electrode belongs to
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
    #endif
} cy_stc_capsense_electrode_config_t;

/** Configuration structure of advanced touchpad */
typedef struct
{
    uint16_t penultimateTh;                                     /**< Defines a threshold for determining arrival at edges. This
                                                                   * value may have to be increased for small diamonds, so that the edge handling is
                                                                   * initiated sooner. If this number is too high, there is jumping at the edge with
                                                                   * a smaller finger. If this number is too low, there is jumping at the edge with a
                                                                   * larger finger. */
    uint16_t virtualSnsTh;                                      /**< Defines a virtual sensor signal. This value should be set
                                                                   * to the value of any sensor when a medium-sized finger is placed directly over
                                                                   * it. If this value is too high, a position is reported nearer the edge than ideal
                                                                   * position. If this value is too low, a position is reported nearer the middle of
                                                                   * touchpad. */
    uint8_t crossCouplingTh;                                    /**< Defines cross coupling threshold. It is subtracted from
                                                                   * sensor signals at centroid position calculation to improve the accuracy.
                                                                   * The threshold should be equal to a sensor signal when your finger is near the
                                                                   * sensor, but not touching the sensor. This can be determined by slowly dragging
                                                                   * your finger across the panel and finding the inflection point of the difference
                                                                   * counts at the base of the curve. The difference value at this point should be
                                                                   * the Cross-coupling threshold. */
    uint8_t reserved0;                                          /**< Reserved field */
    uint8_t reserved1;                                          /**< Reserved field */
    uint8_t reserved2;                                          /**< Reserved field */
} cy_stc_capsense_advanced_touchpad_config_t;


#if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
/** Multi-phase table for de-convolution structure
 * \note This structure is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
 */
typedef struct
{
    uint32_t vector;                                            /**< Vector / pattern */
    int16_t deconvCoef[32u];                                    /**< De-convolution coefficients */
} cy_stc_capsense_mp_table_t;
#endif


/** Widget configuration structure */
typedef struct
{
    cy_stc_capsense_widget_context_t * ptrWdContext;            /**< Pointer to context structure of this widget */
    cy_stc_capsense_sensor_context_t * ptrSnsContext;           /**< Pointer to the first object of sensor context structure that belongs to this widget */
    const cy_stc_capsense_electrode_config_t * ptrEltdConfig;   /**< Pointer to the first object of electrode configuration structure that belongs to this widget */
    uint32_t * ptrEltdCapacitance;                              /**< Pointer to the first object in the electrode capacitance array that belongs to this widget */

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
        uint32_t * ptrSnsCapacitance;                           /**< Pointer to the first object in the sensor capacitance array that belongs to this widget.
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif

    uint16_t * ptrBslnInv;                                      /**< Pointer to the first object in the sensor baseline inversion array that belongs to this widget */

    cy_stc_capsense_smartsense_csd_noise_envelope_t * ptrNoiseEnvelope;
                                                                /**< Pointer to the noise envelope filter used by smart sensing algorithm */
    uint16_t * ptrRawFilterHistory;                             /**< Pointer to the raw count filter history of the widget */
    uint8_t  * ptrRawFilterHistoryLow;                          /**< Pointer to the raw count filter history extended of the widget */
    uint32_t   iirCoeff;                                        /**< Raw count IIR filter coefficient. Smaller value leads to higher filtering */

    uint8_t * ptrDebounceArr;                                   /**< Pointer to the debounce array of the widget */

    const uint8_t * ptrDiplexTable;                             /**< Pointer to the diplex table used for Linear slider when Diplex option is enabled */
    uint32_t centroidConfig;                                    /**< Bit mask defining centroid configuration including centroid type, number of touches, 
                                                                   * diplexing, foam rejection, edge correction, etc. */
    uint16_t xResolution;                                       /**< Keeps maximum position value. For Touchpads X-axis maximum position */
    uint16_t yResolution;                                       /**< For Touchpads Y-Axis maximum position */
    uint16_t numSns;                                            /**< The total number of sensors:
                                                                   * For CSD widgets: WD_NUM_ROWS + WD_NUM_COLS.
                                                                   * For CSX widgets: WD_NUM_ROWS * WD_NUM_COLS.
                                                                   * For ISX widgets: (WD_NUM_ROWS + WD_NUM_COLS) / 2 */
    uint8_t numCols;                                            /**< For CSD Button and Proximity Widgets, the number of sensors.
                                                                   * For CSD Slider Widget, the number of segments.
                                                                   * For CSD Touchpad and Matrix Button, the number of the column sensors.
                                                                   * For CSX Button, Slider, Touchpad, and Matrix Button, the number of the Rx electrodes.
                                                                   * For ISX Button and Linear Slider, the number of the Rx electrodes. */
    uint8_t numRows;                                            /**< For CSD Touchpad and Matrix Buttons, the number of the row sensors.
                                                                   * For the CSX Button and Slider, the number of the Tx electrodes (constant 1u).
                                                                   * For CSX Touchpad and Matrix Button, the number of the Tx electrodes.
                                                                   * For ISX Button and Linear Slider, the number of the Lx electrodes. */
    cy_stc_capsense_touch_t * ptrPosFilterHistory;              /**< Pointer to the position filter history */
    cy_stc_capsense_csx_touch_history_t * ptrCsxTouchHistory;   /**< Pointer to the CSX touchpad history */
    cy_stc_capsense_csx_touch_buffer_t * ptrCsxTouchBuffer;     /**< Pointer to the single CSX buffer needed for CSX touchpad processing */
    uint16_t * ptrCsdTouchBuffer;                               /**< Pointer to the CSD buffer needed for advanced CSD touchpad processing */

    cy_stc_capsense_gesture_config_t * ptrGestureConfig;        /**< Pointer to Gesture configuration structure */
    cy_stc_capsense_gesture_context_t * ptrGestureContext;      /**< Pointer to Gesture context structure */

    cy_stc_capsense_ballistic_config_t ballisticConfig;         /**< The configuration data for position ballistic filter */
    cy_stc_capsense_ballistic_context_t * ptrBallisticContext;  /**< Pointer to Ballistic filter context structure */

    cy_stc_capsense_adaptive_filter_config_t aiirConfig;        /**< The configuration of position adaptive filter */
    cy_stc_capsense_advanced_touchpad_config_t advConfig;       /**< The configuration of CSD advanced touchpad */

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
        cy_stc_capsense_mp_table_t * ptrMpTable;                /**< Pointer to the multi-phase vector and de-convolution coefficients
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif

    uint32_t posFilterConfig;                                   /**< Position filters configuration */
    uint16_t rawFilterConfig;                                   /**< Raw count filters configuration */

    uint16_t alpOnThreshold;                                    /**< ALP Filter ON threshold */
    uint16_t alpOffThreshold;                                   /**< ALP Filter OFF threshold */
    uint16_t cmfThreshold;                                      /**< CMF threshold */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        uint16_t cdacConfig;                                    /**< Bit-mask for widget CDAC configuration:
                                                                 *  * bit[0..1]  - Reference CDAC mode (CY_CAPSENSE_CDAC_REF_MODE_MASK)
                                                                 *    * 0 (CY_CAPSENSE_CDAC_MODE_DISABLED)  - The reference CDAC is disabled
                                                                 *    * 1 (CY_CAPSENSE_CDAC_MODE_MANUAL)    - The value of reference CDAC set manually
                                                                 *    * 2 (CY_CAPSENSE_CDAC_MODE_AUTO)      - The value of reference CDAC set automatically
                                                                 *  * bit[2..3]  - Fine CDAC mode (CY_CAPSENSE_CDAC_FINE_MODE_MASK)
                                                                 *    * 0 (CY_CAPSENSE_CDAC_MODE_DISABLED)  - The fine CDAC is disabled
                                                                 *    * 1 (CY_CAPSENSE_CDAC_MODE_MANUAL)    - The value of fine CDAC set manually
                                                                 *    * 2 (CY_CAPSENSE_CDAC_MODE_AUTO)      - The value of fine CDAC set automatically
                                                                 *  * bit[4..5]  - Compensation CDAC mode (CY_CAPSENSE_CDAC_COMP_MODE_MASK)
                                                                 *    * 0 (CY_CAPSENSE_CDAC_MODE_DISABLED)  - The compensation CDAC is disabled
                                                                 *    * 1 (CY_CAPSENSE_CDAC_MODE_MANUAL)    - The value of compensation CDAC set manually
                                                                 *    * 2 (CY_CAPSENSE_CDAC_MODE_AUTO)      - The value of compensation CDAC set automatically
                                                                 *  * bit[6..7]  - Compensation CDAC divider mode (CY_CAPSENSE_CDAC_COMP_DIV_MODE_MASK)
                                                                 *    * 0 (CY_CAPSENSE_CDAC_MODE_MANUAL)    - The value of compensation CDAC divider set manually
                                                                 *    * 2 (CY_CAPSENSE_CDAC_MODE_AUTO)      - The value of compensation CDAC divider set automatically
                                                                 *  * bit[8..9]  - Sensitivity boost (CY_CAPSENSE_CDAC_BOOST_VAL_MASK)
                                                                 *    * 1 (CY_CAPSENSE_CDAC_BOOST_DISABLED) - Boost disabled
                                                                 *    * 2 (CY_CAPSENSE_CDAC_BOOST_2X)       - 2X Boost
                                                                 *    * 3 (CY_CAPSENSE_CDAC_BOOST_3X)       - 3X Boost
                                                                 *    * 4 (CY_CAPSENSE_CDAC_BOOST_4X)       - 4X Boost
                                                                 * \note This field is available for the fifth-generation low power CAPSENSE&trade;.
                                                                 */

        uint16_t foamCoefficient;                               /**< Foam rejection coefficient. This decides the scanning cycle for foam sensing mechanism.
                                                                 * \note This field is available for the fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
        uint16_t firstSlotId;                                   /**< The slot ID in the widget to start scan from
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint16_t numSlots;                                      /**< The number of slots in the widget
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif

    uint8_t senseMethod;                                        /**< Specifies the widget sensing method:
                                                                    * * 0 - UNDEFINED   (CY_CAPSENSE_UNDEFINED_GROUP)
                                                                    * * 1 - CSD         (CY_CAPSENSE_CSD_GROUP)
                                                                    * * 2 - CSX         (CY_CAPSENSE_CSX_GROUP)
                                                                    * * 3 - ISX         (CY_CAPSENSE_ISX_GROUP) */
    uint8_t wdType;                                             /**< Specifies the widget type */

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
        uint8_t numChopCycles;                                  /**< Defines number of chopping cycles. One cycle means the feature is disabled
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint8_t mpOrder;                                        /**< Multi-phase order
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
            uint8_t mpOrderRows;                                 /**< Multi-phase order for rows in CSD widgets
                                                                 * \note This field is available for the fifth-generation low power CAPSENSE&trade;.
                                                                 */
        #endif
        uint8_t lfsrDitherLimit;                                /**< Max dither in percentage. The input parameter for the LFSR range auto-selection algorithm
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade;and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint8_t snsClkSourceAutoSelMode;                        /**< Defines set of rules that are used by clock source auto-selection algorithm
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint8_t mfsConfig;                                      /**< Multi-frequency Scan (MFS) widget configuration
                                                                 **  Contains masks:
                                                                 * * bit[0:3] - Number of MFS Channels (CY_CAPSENSE_MFS_FREQ_CHANNELS_NUM_MASK).
                                                                 * * bit[4]   - MFS Configuration (CY_CAPSENSE_MFS_EN_MASK):
                                                                 *   * 0 - MFS Disabled.
                                                                 *   * 1 - MFS Enabled (Base or Frequency channel widget).
                                                                 * * bit[5:6]   - Widget attribute (CY_CAPSENSE_MFS_WIDGET_FREQ_ALL_CH_MASK):
                                                                 *   * 0 - Base widget
                                                                 *   * 1 - Frequency channel 1 widget (CY_CAPSENSE_MFS_WIDGET_FREQ_CH_1_MASK)
                                                                 *   * 2 - Frequency channel 2 widget (CY_CAPSENSE_MFS_WIDGET_FREQ_CH_2_MASK)
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint8_t cdacDitherScaleMode;                            /**< CDAC dither scale mode
                                                                 * * 0 (CY_CAPSENSE_CDAC_DITHERING_MODE_DISABLE) - CDAC dithering is disabled
                                                                 * * 1 (CY_CAPSENSE_CDAC_DITHERING_MODE_MANUAL)  - CDAC dither value set manually
                                                                 * * 2 (CY_CAPSENSE_CDAC_DITHERING_MODE_AUTO)    - CDAC dither value set automatically
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        uint8_t cicRateMode;                                    /**< CIC2 filter decimation rate mode
                                                                 * * 0 (CY_CAPSENSE_CIC_RATE_MODE_MANUAL)     - The cicRate value set by users
                                                                 * * 1 (CY_CAPSENSE_CIC_RATE_MODE_AUTO)       - The cicRate value configured by middleware
                                                                 * * 2 (CY_CAPSENSE_CIC_RATE_MODE_SMARTSENSE) - The cicRate value configured by SMARTSENSE&trade; algorithm
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint8_t iirCoeffHw;                                     /**< Raw count HW IIR filter coefficient. Smaller value leads to lower filtering.
                                                                 * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif

} cy_stc_capsense_widget_config_t;

#if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
/** Declares the IDAC gain table
 * \note This structure is available only for the fourth-generation CAPSENSE&trade;.
*/
typedef struct
{
    uint32_t gainReg;                                           /**< Register value of IDAC gain */
    uint32_t gainValue;                                         /**< Absolute gain value in pA */
} cy_stc_capsense_idac_gain_table_t;
#endif

#if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
/** Declares the scan order of widget and sensor
 * \note This structure is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
 */
typedef struct
{
    uint16_t wdId;                                              /**< Specifies the widget ID for the current scan slot */
    uint16_t snsId;                                             /**< Specifies the sensor ID for the current scan slot */
} cy_stc_capsense_scan_slot_t;
#endif

#if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
/** Declares MSC channel (HW block) configuration
 * \note This structure is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
 */
typedef struct
{
    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN)
        MSC_Type * ptrHwBase;                              /**< Pointer to the MSC HW block register
                                                            * \note This structure is available only for the fifth-generation CAPSENSE&trade;
                                                            */
        cy_stc_msc_context_t * ptrHwContext;               /**< Pointer to the MSC driver context
                                                            * \note This structure is available only for the fifth-generation CAPSENSE&trade;
                                                            */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        MSCLP_Type * ptrHwBase;                            /**< Pointer to the MSCLP HW block register
                                                            * \note This structure is available only for the fifth-generation low power CAPSENSE&trade;
                                                            */
        cy_stc_msclp_context_t * ptrHwContext;             /**< Pointer to the MSCLP driver context
                                                            * \note This structure is available only for the fifth-generation low power CAPSENSE&trade;
                                                            */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */

    GPIO_PRT_Type * portCmod1;                              /**< The pointer to the Cmod1 pin base port register */
    uint8_t pinCmod1;                                       /**< The Cmod1 pin position (bit number) in the port */

    GPIO_PRT_Type * portCmod2;                              /**< The pointer to the Cmod2 pin base port register */
    uint8_t pinCmod2;                                       /**< The Cmod2 pin position (bit number) in the port */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN)
        uint8_t dmaWrChIndex;                               /**< Specifies the DMA Write channel index
                                                             * \note This structure is available only for the fifth-generation CAPSENSE&trade;
                                                             */
        uint8_t dmaChainWrChIndex;                          /**< Specifies the DMA Chain Write channel index
                                                             * \note This structure is available only for the fifth-generation CAPSENSE&trade;
                                                             */
        uint8_t dmaRdChIndex;                               /**< Specifies the DMA Read channel index
                                                             * \note This structure is available only for the fifth-generation CAPSENSE&trade;
                                                             */
        uint8_t dmaChainRdChIndex;                          /**< Specifies the DMA Chain Read channel index
                                                             * \note This structure is available only for the fifth-generation CAPSENSE&trade;
                                                             */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN */

    const cy_stc_capsense_electrode_config_t * ptrShieldEltdConfig;   /**< Pointer to the first object of shield electrode configuration */

} cy_stc_capsense_channel_config_t;
#endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN || CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */


/** Common configuration structure */
typedef struct
{
    uint32_t cpuClkHz;                                          /**< CPU clock in Hz */
    uint32_t periClkHz;                                         /**< Peripheral clock in Hz */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
        cy_stc_capsense_idac_gain_table_t idacGainTable[CY_CAPSENSE_IDAC_GAIN_TABLE_SIZE];
                                                                /**< Table with the supported IDAC gains and corresponding register values
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        CSD_Type * ptrCsdBase;                                  /**< Pointer to the CSD HW block register
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        cy_stc_csd_context_t * ptrCsdContext;                   /**< Pointer to the CSD driver context
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        GPIO_PRT_Type * portCmod;                               /**< Pointer to the base port register of the Cmod pin
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        GPIO_PRT_Type * portCsh;                                /**< Pointer to the base port register of the Csh pin
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        GPIO_PRT_Type * portCintA;                              /**< Pointer to the base port register of the CintA pin
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        GPIO_PRT_Type * portCintB;                              /**< Pointer to the base port register of the CintB pin
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN */

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
        cy_stc_capsense_channel_config_t * ptrChConfig;         /**< The pointer to the CAPSENSE&trade; enabled channel (HW block) configuration
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif /* (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP) */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN)
        DMAC_Type * ptrDmacBase;                                /**< Pointer to the DMAC HW block base register
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
        const uint32_t * const * ptrDmaWrChSnsCfgAddr;          /**< Pointer to the array containing the addresses of sensor configurations
                                                                 * used as a source for the DMA Chain Write channel
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
        const uint16_t * const * ptrDmaRdChSnsCfgAddr;          /**< Pointer to the array containing the addresses of sensor configurations
                                                                 * used as a source for the DMA Chain Read channel
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
        const uint32_t ** ptrDmaWrChSnsCfgAddrLocal;            /**< Pointer to the array containing the addresses of sensor configurations
                                                                 * used as a source for the DMA Chain Write channel
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
        const uint16_t ** ptrDmaRdChSnsCfgAddrLocal;            /**< Pointer to the array containing the addresses of sensor configurations
                                                                 * used as a source for the DMA Chain Read channel
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
        uint16_t * ptrEmptyRawCount;                            /**< Pointer to the empty storage for raw count in case widget is disabled.
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN */

    uint16_t numPin;                                            /**< Total number of IOs. */
    uint16_t numSns;                                            /**< The total number of sensors. It is equal to the number of objects with raw count.
                                                                   * * For CSD widgets: WD_NUM_ROWS + WD_NUM_COLS
                                                                   * * For CSX widgets: WD_NUM_ROWS * WD_NUM_COLS */
    uint16_t proxTouchCoeff;                                    /**< Proximity touch coefficient in percentage used in smart sensing algorithm */
    uint16_t csdRConst;                                         /**< Sensor resistance in series used by smart sensing algorithm */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
        uint16_t vdda;                                          /**< VDDA in mV */
        uint16_t csdVref;                                       /**< Vref for CSD method
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN */

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
        uint16_t numEpiCycles;                                  /**< Number of clk_mod cycles to be run during EPILOGUE
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint16_t numCoarseInitChargeCycles;                     /**< Configure duration of Cmod initialization, phase 1
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint16_t numCoarseInitSettleCycles;                     /**< Configure duration of Cmod initialization, phase 2
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint16_t numSlots;                                      /**< Total number of slots
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif /* (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP) */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        uint16_t numProWaitKrefDelayPrs;                        /**< Number of Kref/4 ProDummy Wait Cycles if PRS is enabled
                                                                 * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint16_t numProWaitKrefDelay;                           /**< Number of Kref/4 ProDummy Wait Cycles if PRS is disabled
                                                                 * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint16_t numEpiKrefDelayPrs;                            /**< Number of Kref/4 cycles to be run during EPILOGUE if PRS is enabled
                                                                 * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint16_t numEpiKrefDelay;                               /**< Number of Kref/4 cycles to be run during EPILOGUE if PRS is disabled
                                                                 * \note This field is available only for the fifth-generation pow power CAPSENSE&trade;.
                                                                 */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */

    uint8_t numWd;                                              /**< Total number of widgets */
    uint8_t periDividerType;                                    /**< Peripheral clock type (8- or 16-bit type) */
    uint8_t periDividerIndex;                                   /**< Peripheral divider index */
    uint8_t analogWakeupDelay;                                  /**< Time needed to establish correct operation of CAPSENSE&trade; HW block block after power up or System Deep Sleep. */
    uint8_t swSensorAutoResetEn;                                /**< Sensor auto reset enabled */

    uint8_t csdInactiveSnsConnection;                           /**< Inactive sensor connection for CSD scan:
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_HIGHZ
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_SHIELD
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_GROUND */
    uint8_t csxInactiveSnsConnection;                           /**< Inactive sensor connection for CSX scan:
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_HIGHZ
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_GROUND
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_VDDA_BY_2
                                                                   *
                                                                   * CY_CAPSENSE_SNS_CONNECTION_VDDA_BY_2 is only available for fifth-generation
                                                                   * and fifth-generation low power CAPSENSE&trade;.
                                                                   */
    uint8_t isxInactiveSnsConnection;                           /**< Inactive sensor connection for ISX scan:
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_HIGHZ
                                                                   *
                                                                   * Applicable only for fifth-generation low power CAPSENSE&trade;.
                                                                   */
    uint8_t csdShieldNumPin;                                    /**< Number of shield IOs */

    uint8_t csxRawTarget;                                       /**< Raw count target in percentage for CSX calibration */
    uint8_t csxCalibrationError;                                /**< Acceptable calibration error */
    uint8_t csdRawTarget;                                       /**< Raw count target in percentage for CSD calibration */
    uint8_t csdCalibrationError;                                /**< Acceptable calibration error */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
        uint8_t ssIrefSource;                                   /**< Iref source
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  * */
        uint8_t ssVrefSource;                                   /**< Vref source
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t portCmodPadNum;                                 /**< Number of port of dedicated Cmod pad
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t pinCmodPad;                                     /**< Position of the dedicated Cmod pad in the port
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t portCshPadNum;                                  /**< Number of port of dedicated Csh pad
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t pinCshPad;                                      /**< Position of the dedicated Csh pad in the port
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t portShieldPadNum;                               /**< Number of port of dedicated Shield pad
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t pinShieldPad;                                   /**< Position of the dedicated Shield pad in the port
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t portVrefExtPadNum;                              /**< Number of port of dedicated VrefExt pad
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t pinVrefExtPad;                                  /**< Position of the dedicated VrefExt pad in the port
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t portCmodNum;                                    /**< Number of port of Cmod pin
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t pinCmod;                                        /**< Position of the Cmod pin in the port
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t portCshNum;                                     /**< Number of port of Csh pin
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t pinCsh;                                         /**< Position of the Csh pin in the port
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t pinCintA;                                       /**< Position of the CintA pin in the port
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t pinCintB;                                       /**< Position of the CintB pin in the port
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csdShieldDelay;                                 /**< Shield signal delay
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csdShieldSwRes;                                 /**< Shield switch resistance
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csdInitSwRes;                                   /**< Switch resistance at coarse initialization
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csdChargeTransfer;                              /**< IDAC sensing configuration
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csdIdacGainInitIndex;                           /**< IDAC gain index per \ref idacGainTable
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csdIdacMin;                                     /**< Min acceptable IDAC value in CSD calibration
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csdFineInitTime;                                /**< Number of dummy SnsClk periods at fine initialization
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csdMfsDividerOffsetF1;                          /**< Frequency divider offset for channel 1. This value is added to
                                                                  * base (channel 0) SnsClk divider to form channel 1 frequency
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csdMfsDividerOffsetF2;                          /**< Frequency divider offset for channel 2. This value is added to
                                                                  * base (channel 0) SnsClk divider to form channel 2 frequency
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csxFineInitTime;                                /**< Number of dummy TX periods at fine initialization
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csxInitSwRes;                                   /**< Switch resistance at fine initialization
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csxScanSwRes;                                   /**< Switch resistance at scanning
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csxInitShieldSwRes;                             /**< Switch resistance at fine initialization
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csxScanShieldSwRes;                             /**< Switch resistance at scanning
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csxMfsDividerOffsetF1;                          /**< Frequency divider offset for channel 1. This value is added to
                                                                  * base (channel 0) Tx divider to form channel 1 frequency
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t csxMfsDividerOffsetF2;                          /**< Frequency divider offset for channel 2. This value is added to
                                                                  * base (channel 0) Tx divider to form channel 2 frequency
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
    #endif

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
        uint8_t isxRawTarget;                                   /**< Raw count target in percentage for ISX calibration
                                                                  * \note This structure is available only for the fifth-generation low power CAPSENSE&trade;
                                                                  */
        uint8_t isxCalibrationError;                            /**< Acceptable calibration error
                                                                  * \note This structure is available only for the fifth-generation low power CAPSENSE&trade;
                                                                  */
        uint8_t csdShieldMode;                                  /**< Shield mode
                                                                 * * CY_CAPSENSE_SHIELD_DISABLED
                                                                 * * CY_CAPSENSE_SHIELD_ACTIVE
                                                                 * * CY_CAPSENSE_SHIELD_PASSIVE
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint8_t numProOffsetCycles;                             /**< Maximum number of clk_mod cycles for the PRO_OFFSET state.
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint8_t proOffsetCdacComp;                              /**< Compensation CAPDAC size during PRO_OFFSET.
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
        uint8_t chopPolarity;                                   /**< Select polarity for system level chopping
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint8_t numBadScans;                                    /**< 1 to 7, repeat scan upon "bad" scan. Disabled = 0.
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint8_t counterMode;                                    /**< Select overflow or saturate mode for raw count:
                                                                 * * 0 - CY_CAPSENSE_COUNTER_MODE_SATURATE
                                                                 * * 1 - CY_CAPSENSE_COUNTER_MODE_OVERFLOW
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif /* (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP) */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN)
        uint8_t sensorConnection;                               /**< Sensor Connection. In CS-DMA mode, sensor connection always set to CTRLMUX.
                                                                 * * 0 - CY_CAPSENSE_AMUX_SENSOR_CONNECTION_METHOD:
                                                                 *       All AMUX capable GPIOs available as sensor.
                                                                 * * 1 - CY_CAPSENSE_CTRLMUX_SENSOR_CONNECTION_METHOD:
                                                                 *       Only dedicated GPIO available as sensor.
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
        uint8_t syncClockEn;                                    /**< Enable external synchronization signals
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
        uint8_t syncMode;                                       /**< Synchronization mode:
                                                                 * * 0 - CY_CAPSENSE_SYNC_MODE_OFF
                                                                 * * 1 - CY_CAPSENSE_SYNC_EXTERNAL
                                                                 * * 2 - CY_CAPSENSE_SYNC_INTERNAL
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
        uint8_t masterChannelId;                                /**< The ID of the Master channel MULTI-CHIP solution.
                                                                 * This channel will generate msc_ext_frm_start_out
                                                                 * and msc_ext_sync_clk_out signals
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
        uint8_t numChannels;                                    /**< The number of CAPSENSE&trade; enabled MSCv3 blocks in the current chip
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
        uint8_t channelOffset;                                  /**< The ID of the first channel that belongs to the current chip
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
        uint8_t syncFrameStartEn;                               /**< Enable external synchronization signals
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN */
} cy_stc_capsense_common_config_t;


/** Declares BIST Context Data Structure */
typedef struct
{
    cy_en_capsense_bist_hw_config_t hwConfig;                   /**< A HW configuration for BIST operations */
    cy_en_capsense_bist_io_state_t currentISC;                  /**< The current state of sensors when not being measured during the sensor capacitance measurement */
    cy_en_capsense_bist_io_state_t shieldCapISC;                /**< The configured inactive electrode connection for BIST shield electrode capacitance measurement.
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_HIGHZ
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_SHIELD
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_GROUND */
    cy_en_capsense_bist_io_state_t eltdCapCsdISC;               /**< The configured inactive electrode connection for BIST CSD sensor or electrode capacitance measurement:
                                                                     The states are the same as of the previous parameter */
    cy_en_capsense_bist_io_state_t eltdCapCsxISC;               /**< The configured inactive electrode connection for BIST CSX sensor or electrode capacitance measurement:
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_HIGHZ
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_GROUND */
    cy_en_capsense_bist_io_state_t intrEltdCapShieldISC;        /**< The internal inactive electrode connection used during the BIST shield electrode capacitance measurement:
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_HIGHZ
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_SHIELD
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_GROUND */
    cy_en_capsense_bist_io_state_t intrEltdCapCsdISC;           /**< The internal inactive electrode connection used during the BIST CSD sensor or electrode capacitance measurement:
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_HIGHZ
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_SHIELD
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_GROUND */
    cy_en_capsense_bist_io_state_t intrEltdCapCsxISC;           /**< The internal inactive electrode connection used during the BIST CSX sensor or electrode capacitance measurement:
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_HIGHZ
                                                                   * * CY_CAPSENSE_SNS_CONNECTION_GROUND */
    uint32_t testResultMask;                                    /**< The bit mask of test results (PASS/FAIL) */
#if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
    uint32_t shieldCap;                                         /**< The shield capacitance measurement result in femtofarads
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
#endif

#if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
    uint32_t * ptrChShieldCap;                                  /**< The pointer to the channel shield capacitance measurement result array
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
#endif

#if ((CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
    uint16_t vddaVoltage;                                       /**< The result of VDDA measurement in millivolts
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
#endif

    uint32_t eltdCapSnsClkFreqHz;                               /**< The value of the SnsClk frequency is Hz */
    uint16_t * ptrWdgtCrc;                                      /**< The pointer to the widget CRC array */

    uint16_t wdgtCrcCalc;                                       /**< A calculated by test CRC for a widget context structure */

    uint16_t eltdCapModClk;                                     /**< The ModClk divider for electrode capacitance measurement scans */
    uint16_t eltdCapSnsClk;                                     /**< The SnsClk divider for electrode capacitance measurement scans */

#if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN)
    uint16_t curBistWdId;                                       /**< The current widget ID for BIST operations
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade;.
                                                                 */
#endif

    uint8_t eltdCapSenseGroup;                                  /**< The sensor group for capacitance measurement:
                                                                    * * 0 - UNDEFINED   (CY_CAPSENSE_UNDEFINED_GROUP)
                                                                    * * 1 - CSD         (CY_CAPSENSE_CSD_GROUP)
                                                                    * * 2 - CSX         (CY_CAPSENSE_CSX_GROUP) */
    uint8_t crcWdgtId;                                          /**< The first CRC failed widget ID */
    uint8_t snsIntgShortSettlingTime;                           /**< The sensor and shield short check time in microseconds */
    uint8_t shortedWdId;                                        /**< The first shorted to GND/VDDA/ELTD widget ID */
    uint8_t shortedSnsId;                                       /**< The first shorted to GND/VDDA/ELTD sensor ID */

#if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
    uint32_t regSwHsPSelScan;                                   /**< Internal pre-calculated data for faster operation */
    uint32_t regSwHsPSelCmodInit;                               /**< Internal pre-calculated data for faster operation */
    uint32_t regSwHsPSelCtankInit;                              /**< Internal pre-calculated data for faster operation */
    uint32_t regSwDsiSel;                                       /**< Internal pre-calculated data for faster operation */
    uint32_t regSwShieldSelScan;                                /**< Internal pre-calculated data for faster operation */
    uint32_t regSwResInit;                                      /**< Internal pre-calculated data for faster operation */
    uint32_t regSwResScan;                                      /**< Internal pre-calculated data for faster operation */
    uint32_t regSwBypSel;                                       /**< Internal pre-calculated data for faster operation */
    uint32_t regSwAmuxbufSel;                                   /**< Internal pre-calculated data for faster operation */
    uint32_t regAmbuf;                                          /**< Internal pre-calculated data for faster operation */
    uint32_t regHscmpScan;                                      /**< Internal pre-calculated data for faster operation */
    uint32_t regSwRefgenSel;                                    /**< Internal pre-calculated data for faster operation */
    uint32_t regConfig;                                         /**< Internal pre-calculated data for faster operation */
    uint32_t regIoSel;                                          /**< Internal pre-calculated data for faster operation */
    uint32_t regAmbufShield;                                    /**< Internal pre-calculated data for faster operation */
    uint32_t regHscmpScanShield;                                /**< Internal pre-calculated data for faster operation */
    uint32_t regSwShieldSelScanShield;                          /**< Internal pre-calculated data for faster operation */
    uint32_t regSwHsPSelScanShield;                             /**< Internal pre-calculated data for faster operation */
    uint32_t regSwBypSelShield;                                 /**< Internal pre-calculated data for faster operation */
    uint32_t regSwAmuxbufSelShield;                             /**< Internal pre-calculated data for faster operation */
    uint32_t regConfigShield;                                   /**< Internal pre-calculated data for faster operation */
    uint32_t regIoSelShield;                                    /**< Internal pre-calculated data for faster operation */

    uint32_t extCapIdacPa;                                      /**< The IDAC value in pA for external capacitor capacity measurements
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint16_t extCapModClk;                                      /**< The ModClk divider for external capacitor capacity measurements
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint16_t extCapSnsClk;                                      /**< The SnsClk divider for external capacitor capacity measurements
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint16_t extCapWDT;                                         /**< The SW watchdog timeout used to prevent a hang in case of short
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint16_t extCapVrefMv;                                      /**< The Vref value in mV for external capacitor capacity measurements
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint16_t cModCap;                                           /**< The Cmod capacitance measurement result in picofarads
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint16_t cIntACap;                                          /**< The CintA capacitance measurement result in picofarads
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint16_t cIntBCap;                                          /**< The CIntB capacitance measurement result in picofarads
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint16_t cShieldCap;                                        /**< The Cshield capacitance measurement result in picofarads
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint16_t capacitorSettlingTime;                             /**< The maximum possible external capacitor charge/discharge time in microseconds
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint16_t vddaModClk;                                        /**< The ModClk divider for VDDA measurements
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint16_t vddaVrefMv;                                        /**< The Vref value in mV for VDDA measurements
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint16_t eltdCapVrefMv;                                     /**< The Vref value in mV for electrode capacitance measurement scans
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint16_t eltdCapResolution;                                 /**< The resolution for electrode capacitance measurement scans
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */

    uint8_t vddaIdacDefault;                                    /**< The IDAC default code for Vdda measurements
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint8_t vddaAzCycles;                                       /**< The auto-zero time in Sns cycles for Vdda measurements
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint8_t vddaAcqCycles;                                      /**< The acquisition time in Sns cycles - 1 for Vdda measurements
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint8_t fineInitTime;                                       /**< Number of dummy SnsClk periods at fine initialization for BIST scans
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint8_t eltdCapVrefGain;                                    /**< The Vref gain for electrode capacitance measurement scans
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint8_t vddaVrefGain;                                       /**< The Vref gain for VDDA measurements
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    uint8_t extCapVrefGain;                                     /**< The Vref gain for external capacitor capacitance measurements
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
#endif

#if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
    const cy_stc_capsense_electrode_config_t * curPtrEltdCfg;   /**< The pointer to the current electrode configuration for BIST operations
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
    uint32_t eltdInactiveDm;                                    /**< Internal pre-calculated data for faster operation */
    en_hsiom_sel_t eltdInactiveHsiom;                           /**< Internal pre-calculated data for faster operation */

    uint16_t curBistSlotId;                                     /**< The current slot ID for BIST operations
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade; and fifth-generation
                                                                 * low power CAPSENSE&trade;.
                                                                 */
    uint16_t eltdCapSubConvNum;                                  /**< The sub-conversion number for electrode capacitance measurement scans
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade; and fifth-generation
                                                                 * low power CAPSENSE&trade;.
                                                                 */
    uint16_t eltdCapNumEpiCycles;                               /**< Number of clk_mod cycles to be run during EPILOGUE
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade; and fifth-generation
                                                                 * low power CAPSENSE&trade;.
                                                                 */
    uint16_t eltdCapNumCoarseInitChargeCycles;                  /**< Configure duration of Cmod initialization, phase 1
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade; and fifth-generation
                                                                 * low power CAPSENSE&trade;.
                                                                 */
    uint16_t eltdCapNumCoarseInitSettleCycles;                  /**< Configure duration of Cmod initialization, phase 2
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade; and fifth-generation
                                                                 * low power CAPSENSE&trade;.
                                                                 */
    uint16_t eltdCapNumFineInitWaitCycles;                      /**< Number of ProDummy Wait Cycles
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade; and fifth-generation
                                                                 * low power CAPSENSE&trade;.
                                                                 */

#if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_TST_EXTERNAL_CAP_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_TST_VDDA_EN))
    uint16_t extCapDischargeTime;                               /**< The discharging time in us needed to discharge
                                                                 * the external capacitor before the measurement
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade; and fifth-generation
                                                                 * low power CAPSENSE&trade;.
                                                                 */
    uint16_t extCapSubConvNum;                                  /**< The sub-conversion number for Cmod measurement
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade; and fifth-generation
                                                                 * low power CAPSENSE&trade;.
                                                                 */
#endif

#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_TST_EXTERNAL_CAP_EN)
    uint16_t extCapWDT;                                         /**< The SW watchdog timeout used to prevent a hang
                                                                 * in case of short the external capacitor
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade; and fifth-generation
                                                                 * low power CAPSENSE&trade;.
                                                                 */
    uint16_t cMod01Cap;                                         /**< The MSC0 Cmod1 capacitance measurement result
                                                                 * in picofarads
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade; and fifth-generation
                                                                 * low power CAPSENSE&trade;.
                                                                 */
    uint16_t cMod02Cap;                                         /**< The MSC0 Cmod2 capacitance measurement result
                                                                 * in picofarads
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade; and fifth-generation
                                                                 * low power CAPSENSE&trade;.
                                                                 */

#if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || \
     ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP) && (1u == MSCLP_CMOD34_PRESENT)))
    uint16_t cMod03Cap;                                         /**< The MSC0 Cmod3 capacitance measurement result
                                                                 * in picofarads
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade; and fifth-generation
                                                                 * low power CAPSENSE&trade;.
                                                                 */
    uint16_t cMod04Cap;                                         /**< The MSC0 Cmod4 capacitance measurement result
                                                                 * in picofarads
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade; and fifth-generation
                                                                 * low power CAPSENSE&trade;.
                                                                 */
#endif /* ((CY_CAPSENSE_PLATFORM_BLOCK_FORTH_GEN_LP) || \
           ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP) && (MSCLP_CMOD34_PRESENT))) */

#if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN)
    uint16_t cMod11Cap;                                         /**< The MSC1 Cmod1 capacitance measurement result
                                                                 * in picofarads
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade;.
                                                                 */
    uint16_t cMod12Cap;                                         /**< The MSC1 Cmod2 capacitance measurement result
                                                                 * in picofarads
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade;.
                                                                 */
    uint16_t cMod13Cap;                                         /**< The MSC1 Cmod3 capacitance measurement result
                                                                 * in picofarads
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade;.
                                                                 */
    uint16_t cMod14Cap;                                         /**< The MSC1 Cmod4 capacitance measurement result
                                                                 * in picofarads
                                                                 * \note This field is available only for the fifth-
                                                                 * generation CAPSENSE&trade;.
                                                                 */
#endif /* (CY_CAPSENSE_PLATFORM_BLOCK_FORTH_GEN) */

#endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_TST_EXTERNAL_CAP_EN) */

    uint8_t eltdCapNumFineInitCycles;                           /**< Number of ProDummy SubConversions
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
    uint8_t eltdCapRefCdac;                                     /**< The reference CDAC code for electrode capacitance measurement scans
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
    uint8_t curBistChId;                                        /**< The current MSCv3 channel ID for BIST operations
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
    uint8_t skipChannelMask;                                    /**< The skip channel mask for BIST operations
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
    uint8_t eltdCapScanMode;                                    /**< The scan mode for sensor (electrode) capacitance measurement
                                                                 * * 0u - scan by slots (CY_CAPSENSE_BIST_CAP_SLOT_SCAN)
                                                                 * * 1u - scan by electrodes (CY_CAPSENSE_BIST_CAP_ELTD_SCAN)
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
#endif
}
cy_stc_capsense_bist_context_t;


#if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
/** Declares the BIST structure with custom scan parameters
 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
 */
typedef struct
{
    uint16_t modClk;                                            /**< The ModClk divider for a custom scan. The minimum value is 1 and the maximum depends on a divider type,
                                                                     but for a reliable CSD HW block operation, it is recommended to provide
                                                                     a modulation clock frequency in the range from 1 to 50 MHz */
    uint16_t snsClk;                                            /**< The SnsClk divider for a custom scan. The minimum value is 4 and the maximum is 4095,
                                                                     but for a reliable CSD HW block operation, it is recommended to provide
                                                                     an sensor clock frequency in the range from 100 to 6000 kHz */
    uint16_t convNum;                                           /**< The number of conversions for a custom scan. The maximum raw counts is equal (convNum * snsClkDivider - 1),
                                                                     that corresponds to (2^Resolution - 1) in older notations. The minimum value is 4 and the maximum is 65535,
                                                                     but as the maximum raw counts is 65535, the convNum value should be less than (65536 / snsClkDivider) */
    cy_en_capsense_bist_io_state_t customISC;                   /**< The inactive state of sensors during the custom scan */
    uint8_t reserved0;                                          /**< Reserved field */

    uint8_t vrefGain;                                           /**< The Vref gain for a custom scan */
    uint8_t idacMod;                                            /**< Sets the code of the modulation IDAC for a custom scan */
    uint8_t idacGainIndex;                                      /**< Index of IDAC gain in table \ref cy_stc_capsense_idac_gain_table_t */
    uint8_t fineInitTime;                                       /**< Number of dummy SnsClk periods at fine initialization for a custom scan */

}cy_stc_capsense_bist_custom_parameters_t;
#endif


/** Declares active sensor details */
typedef struct
{
    #if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
        const cy_stc_capsense_widget_config_t * ptrWdConfig;    /**< Pointer to the widget configuration structure of the active sensor */
        cy_stc_capsense_widget_context_t * ptrWdContext;        /**< Pointer to the widget context structure of the active sensor */
        uint8_t scanScope;                                      /**< Keeps request of scanning either:
                                                                   * * CY_CAPSENSE_SCAN_SCOPE_SNGL_SNS - Single sensor
                                                                   * * CY_CAPSENSE_SCAN_SCOPE_ALL_SNS_MASK - All sensors of one widget
                                                                   * * CY_CAPSENSE_SCAN_SCOPE_ALL_WD_MASK - All widgets */
        uint8_t mfsChannelIndex;                                /**< MFS channel index
                                                                  * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                  */
        uint8_t rxIndex;                                        /**< Current Rx ID */
        uint8_t txIndex;                                        /**< Current Tx ID */
    #endif

    const cy_stc_capsense_electrode_config_t * ptrEltdConfig;   /**< Pointer to the electrode configuration structure of the active sensor */
    const cy_stc_capsense_electrode_config_t * ptrRxConfig;     /**< Pointer to the Rx electrode configuration structure of the active sensor */
    const cy_stc_capsense_electrode_config_t * ptrTxConfig;     /**< Pointer to the Tx electrode configuration structure of the active sensor */

    cy_stc_capsense_sensor_context_t * ptrSnsContext;           /**< Pointer to the sensor context structure */

    uint16_t currentChannelSlotIndex;                           /**< Current slot Index for channel */
    uint16_t sensorIndex;                                       /**< Current sensor ID */
    uint8_t widgetIndex;                                        /**< Current widget ID */
    uint8_t currentSenseMethod;                                 /**< Current sensing method */
    uint8_t connectedSnsState;                                  /**< Shows if the current sensor is connected to analog bus */
} cy_stc_capsense_active_scan_sns_t;


/**
* Provides the typedef for the callback function that is intended to be called when
* the \ref cy_en_capsense_callback_event_t events occurs.
*/
typedef void (*cy_capsense_callback_t)(cy_stc_capsense_active_scan_sns_t * ptrActiveScan);

#if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
    /**
    * Provides the typedef for the callback function that is called by the
    * Cy_CapSense_Enable() function to change the CAPSENSE&trade; configuration from
    * the default configuration to the user's specific use cases.
    * Refer to \ref group_capsense_callbacks section.
    *
    * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
    */
    typedef void (*cy_capsense_ds_init_callback_t)(void * context);
#endif

/**
* Provides the typedef for the callback function that is called by the
* Cy_CapSense_RunTuner() function to establish communication with
* the CAPSENSE&trade; Tuner tool to monitor CAPSENSE&trade; operation.
* For the fifth-generation low power CAPSENSE&trade; the callback is called only once for each new scan.
* For the previous CAPSENSE&trade; generations the callback is called once per scan cycle or periodically if device is in suspended mode.
* Refer to \ref group_capsense_callbacks section.
*/
typedef void (*cy_capsense_tuner_send_callback_t)(void * context);

/**
* Provides the typedef for the callback function that is called by the
* Cy_CapSense_RunTuner() function to establish communication with
* the CAPSENSE&trade; Tuner tool to support life-time tuning.
* Refer to \ref group_capsense_callbacks section.
*/
typedef void (*cy_capsense_tuner_receive_callback_t)(uint8_t ** commandPacket, uint8_t ** tunerPacket, void * context);


/** Declares internal Context Data Structure */
typedef struct
{
    cy_capsense_callback_t ptrSSCallback;                          /**< Pointer to a user's Start Sample callback function. Refer to \ref group_capsense_callbacks section */
    cy_capsense_callback_t ptrEOSCallback;                         /**< Pointer to a user's End Of Scan callback function. Refer to \ref group_capsense_callbacks section */
    cy_capsense_tuner_send_callback_t ptrTunerSendCallback;        /**< Pointer to a user's tuner callback function. Refer to \ref group_capsense_callbacks section */
    cy_capsense_tuner_receive_callback_t ptrTunerReceiveCallback;  /**< Pointer to a user's tuner callback function. Refer to \ref group_capsense_callbacks section */

    void (* ptrISRCallback)(void * context);                       /**< Pointer to the scan interrupt handler */

    #if (!CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        uint32_t csdInactiveSnsDm;                                 /**< Internal pre-calculated data for faster operation */
        uint32_t csxInactiveSnsDm;                                 /**< Internal pre-calculated data for faster operation */
    #endif

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
        uint32_t csdRegConfig;                                     /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegSwHsPSelScan;                               /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegSwHsPSelCmodInit;                           /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegSwHsPSelCtankInit;                          /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegSwBypSel;                                   /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegSwResScan;                                  /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegSwResInit;                                  /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegSwDsiSel;                                   /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegAmuxbufInit;                                /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegSwAmuxbufSel;                               /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegSwShieldSelScan;                            /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegHscmpInit;                                  /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegHscmpScan;                                  /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdIdacAConfig;                                   /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdIdacBConfig;                                   /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegSwCmpPSel;                                  /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegSwCmpNSel;                                  /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegIoSel;                                      /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegRefgen;                                     /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csdRegSwRefGenSel;                                /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */

        uint32_t csxRegConfigInit;                                 /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csxRegConfigScan;                                 /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csxRegSwResInit;                                  /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csxRegSwResPrech;                                 /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csxRegSwResScan;                                  /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csxRegAMuxBuf;                                    /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csxRegRefgen;                                     /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csxRegRefgenSel;                                  /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csxRegSwCmpNSel;                                  /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint32_t csxRegSwRefGenSel;                                /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint16_t csdVrefVoltageMv;                                 /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint8_t csdCmodConnection;                                 /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint8_t csdCshConnection;                                  /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
        uint8_t csdVrefGain;                                       /**< Internal pre-calculated data for faster operation
                                                                    * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                    */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN */

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
        cy_capsense_ds_init_callback_t ptrEODsInitCallback;        /**< Pointer to a user's End Of Data Structure Initialization callback function. Refer to \ref group_capsense_callbacks section
                                                                    * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                    */
        #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN)
            uint32_t snsCtlReg[CY_CAPSENSE_TOTAL_CH_NUMBER];       /**< Keeps value of non-retention SNS_CTL register for LFT mode */
        #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN */

        #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
            uint32_t snsCtlReg;                                    /**< Keeps value of non-retention SNS_CTL register for LFT mode */
            uint32_t activeWakeupTimer;                            /**< The wakeup timer value for the ACTIVE scan mode in microseconds
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint32_t activeWakeupTimerCycles;                      /**< The wakeup timer value for the ACTIVE scan mode in ILO cycles
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint32_t wotScanInterval;                              /**< Scan refresh interval (us) while in Wake-on-Touch mode.
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint32_t wotScanIntervalCycles;                        /**< The scan refresh interval value for the Wake-on-Touch scan mode in ILO cycles
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint32_t iloCompensationFactor;                        /**< The ILO compensation factor value, calculated as actual ILO frequency (Hz) * 2^14 / 1000000
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */

        uint16_t numCoarseInitChargeCycles;                        /**< Configure duration of Cmod initialization, phase 1
                                                                    * \note This field is available only for the fifth-generation and for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint16_t numCoarseInitSettleCycles;                        /**< Configure duration of Cmod initialization, phase 2
                                                                    * \note This field is available only for the fifth-generation and for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint16_t currentSlotIndex;                                 /**< Current slot ID
                                                                    * \note This field is available only for the fifth-generation and for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint16_t endSlotIndex;                                     /**< The last slot ID for the current frame
                                                                    * \note This field is available only for the fifth-generation and for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint16_t numValidSlots;                                    /**< Number of valid slots
                                                                    * \note This field is available only for the fifth-generation and for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint16_t firstValidSlot;                                  /**< The first valid slots ID
                                                                    * \note This field is available only for the fifth-generation and for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint16_t lfsrPoly;                                         /**< LFSR Polynomial
                                                                    * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                    */
        #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN)
            uint16_t numFineInitWaitCycles;                        /**< Number of ProDummy Wait Cycles
                                                                    * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                    */
            uint16_t numEpiCycles;                                 /**< Number of clk_mod cycles to be run during EPILOGUE
                                                                    * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                    */
        #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN */

        #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
            uint16_t numProWaitKrefDelayPrs;                       /**< Number of Kref/4 ProDummy Wait Cycles if PRS is enabled
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint16_t numProWaitKrefDelay;                          /**< Number of Kref/4 ProDummy Wait Cycles if PRS is disabled
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint16_t numEpiKrefDelayPrs;                           /**< Number of Kref/4 cycles to be run during EPILOGUE if PRS is enabled
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint16_t numEpiKrefDelay;                              /**< Number of Kref/4 cycles to be run during EPILOGUE if PRS is disabled
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint16_t numSlots;                                     /**< The number of slots in the current frame
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint16_t startSlotIndex;                               /**< The start slot ID for the current scan
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint16_t wotTimeout;                                   /**< The number of frames to be scanned in Wake-on-Touch mode when there is no touch.
                                                                    * The maximum value is limited to the 14 bits, the applicable range is [1..16383].
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */

        uint8_t intrIsxInactSnsConn;                               /**< Internal inactive electrode connection for ISX scan:
                                                                    * * CY_CAPSENSE_SNS_CONNECTION_HIGHZ
                                                                    * * CY_CAPSENSE_SNS_CONNECTION_GROUND */
        uint8_t numFineInitCycles;                                 /**< Number of ProDummy SubConversions
                                                                    * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint8_t lfsrScale;                                         /**< LFSR Scale value
                                                                    * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint8_t cdacDitherSeed;                                    /**< Dither CDAC Seed
                                                                    * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint8_t cdacDitherPoly;                                    /**< Dither CDAC Polynomial
                                                                    * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint8_t modClk;                                            /**< The modulator clock divider
                                                                    * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint8_t scanSingleSlot;                                    /**< Request of scanning just one slot with keeping HW configuration after scan:
                                                                    * * CY_CAPSENSE_SCAN_SNGL_SLOT - Single slot scanning
                                                                    * * CY_CAPSENSE_SCAN_MULTIPLE_SLOT - Multiple slot scanning
                                                                    * \note This field is available only for the fifth-generation and for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint8_t numProOffsetCycles;                                /**< Maximum number of clk_mod cycles for the PRO_OFFSET state.
                                                                    * \note This field is available only for the fifth-generation and for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint8_t proOffsetCdacComp;                                 /**< Compensation CAPDAC size during PRO_OFFSET.
                                                                    * \note This field is available only for the fifth-generation and for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint8_t hwConfigState;                                     /**< Contains the current hw state, it is configured or not and if yes then to what operation
                                                                    * \note This field is available only for the fifth-generation and for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint8_t slotAutoCalibrMode;                                /**< The slot auto-calibration mode:
                                                                    * * 0 - CY_CAPSENSE_CAL_MODE_REF_CDAC_SUC_APPR
                                                                    * * 2 - CY_CAPSENSE_CAL_MODE_COMP_CDAC_SUC_APPR
                                                                    * * 3 - CY_CAPSENSE_CAL_MODE_FINE_CDAC_SUC_APPR
                                                                    * \note This field is available only for the fifth-generation and for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint8_t intrCsdRawTarget;                                  /**< Internal auto-calibration target in percentage for CSD widgets
                                                                    * \note This field is available only for the fifth-generation and for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint8_t intrCsxRawTarget;                                  /**< Internal auto-calibration target in percentage for CSX widgets
                                                                    * \note This field is available only for the fifth-generation and for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
        uint8_t intrIsxRawTarget;                                  /**< Internal auto-calibration target in percentage for ISX widgets
                                                                    * \note This field is available only for the fifth-generation and for the fifth-generation low power CAPSENSE&trade;
                                                                    */
        #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN)
            uint8_t numSenseMethod;                                /**< The number of sense methods, used in the project
                                                                    * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                    */
            uint8_t mapSenseMethod[CY_CAPSENSE_REG_MODE_NUMBER];   /**< The map array of sense methods, used in the project
                                                                    * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                    */
        #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN */

        #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
            uint8_t csdCdacDitherEn;                               /**< Enabled CDAC dithering for CSD sensing method
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint8_t csxCdacDitherEn;                               /**< Enabled CDAC dithering for CSX sensing method
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint8_t isxCdacDitherEn;                               /**< Enabled CDAC dithering for ISX sensing method
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint8_t bslnCoefSlow;                                  /**< Baseline IIR filter coefficient (slow) for Low power widget.
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint8_t bslnCoefFast;                                  /**< Baseline IIR filter coefficient (fast) for Low power widget.
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint8_t bslnUpdateDelay;                               /**< Specifies the value from which timer is decremented from on consecutive scans where the baseline update IIR produces a zero.
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint8_t iirCoeffLp;                                    /**< Rawcount IIR filter coefficient for Low power widget
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */

            uint8_t firstActSubFrame;                              /**< The flag for a first Active sub-frame. It is used for Active Low Refresh-rate scans
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint8_t numFunc;                                       /**< The number of pin functions, used in the project
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint8_t mapPinState[CY_CAPSENSE_CTRLMUX_PIN_STATE_NUMBER]; /**< The map array of CTRLMUX pin functions, used in the project
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint8_t operatingMode;                                 /**< The internal fifth-generation low power CAPSENSE&trade; HW block operating mode
                                                                    * * 0 - CY_CAPSENSE_CTL_OPERATING_MODE_CPU
                                                                    * * 2 - CY_CAPSENSE_CTL_OPERATING_MODE_AS_MS
                                                                    * * 3 - CY_CAPSENSE_CTL_OPERATING_MODE_LP_AOS
                                                                    * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                    */
            uint8_t mrssStateAfterScan;                            /**< Defines the MRSS state after scan frame is complete. By default MRSS is left enabled */
            uint8_t repeatScanEn;                                  /**< Defines if repeating the previous scan is allowed for the RepeatScan() function usage */
        #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */

    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN || CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */

    #if (!CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        en_hsiom_sel_t csxInactiveSnsHsiom;                        /**< Internal pre-calculated data for faster operation */
        en_hsiom_sel_t csdInactiveSnsHsiom;                        /**< Internal pre-calculated data for faster operation */
    #endif

    uint8_t intrCsdInactSnsConn;                                   /**< Internal inactive electrode connection for CSD scan:
                                                                    * * CY_CAPSENSE_SNS_CONNECTION_HIGHZ
                                                                    * * CY_CAPSENSE_SNS_CONNECTION_SHIELD
                                                                    * * CY_CAPSENSE_SNS_CONNECTION_GROUND */
    uint8_t intrCsxInactSnsConn;                                   /**< Internal inactive electrode connection for CSX scan:
                                                                    * * CY_CAPSENSE_SNS_CONNECTION_HIGHZ
                                                                    * * CY_CAPSENSE_SNS_CONNECTION_GROUND
                                                                    * * CY_CAPSENSE_SNS_CONNECTION_VDDA_BY_2 */
    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP) && (0u != CY_CAPSENSE_RC_HW_IIR_FILTER_EN))
        uint8_t hwIirInit;                                         /**< Flag to reset/initialize HW IIR filter for active widgets during calibration, first scan, etc. */
    #endif
}cy_stc_capsense_internal_context_t;


/** Declares the structure that is intended to store the \ref cy_stc_capsense_widget_context_t
 *  data structure fields, the CRC checking should be applied for.
 */
typedef struct
{
    uint16_t fingerThVal;                                       /**< The value of the .fingerTh field of the \ref cy_stc_capsense_widget_context_t structure */
    uint16_t proxThVal;                                         /**< The value of the .proxTh field of the \ref cy_stc_capsense_widget_context_t structure */
    uint16_t fingerCapVal;                                      /**< The value of the .fingerCap field of the \ref cy_stc_capsense_widget_context_t structure */
    uint16_t sigPFCVal;                                         /**< The value of the .sigPFC field of the \ref cy_stc_capsense_widget_context_t structure */
    uint16_t resolutionVal;                                     /**< The value of the .resolution field of the \ref cy_stc_capsense_widget_context_t structure */
    uint16_t lowBslnRstVal;                                     /**< The value of the .lowBslnRst field of the \ref cy_stc_capsense_widget_context_t structure */
    uint16_t snsClkVal;                                         /**< The value of the .snsClk field of the \ref cy_stc_capsense_widget_context_t structure */
    uint16_t rowSnsClkVal;                                      /**< The value of the .rowSnsClk field of the \ref cy_stc_capsense_widget_context_t structure */
    uint16_t noiseThVal;                                        /**< The value of the .noiseTh field of the \ref cy_stc_capsense_widget_context_t structure */
    uint16_t nNoiseThVal;                                       /**< The value of the .nNoiseTh field of the \ref cy_stc_capsense_widget_context_t structure */
    uint16_t hysteresisVal;                                     /**< The value of the .hysteresis field of the \ref cy_stc_capsense_widget_context_t structure */
    uint16_t maxRawCountVal;                                    /**< The value of the .maxRawCount field of the \ref cy_stc_capsense_widget_context_t structure */
    uint16_t maxRawCountRowVal;                                 /**< The value of the .maxRawCountRow field of the \ref cy_stc_capsense_widget_context_t structure */
    uint8_t onDebounceVal;                                      /**< The value of the .onDebounce field of the \ref cy_stc_capsense_widget_context_t structure */
    uint8_t snsClkSourceVal;                                    /**< The value of the .snsClkSource field of the \ref cy_stc_capsense_widget_context_t structure */
    uint8_t bslnCoeffVal;                                       /**< The value of the .bslnCoeff field of the \ref cy_stc_capsense_widget_context_t structure */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
        uint8_t idacModVal[CY_CAPSENSE_MAX_SUPPORTED_FREQ_NUM];     /**< The value of the .idacMod field of the \ref cy_stc_capsense_widget_context_t structure */
        uint8_t idacGainIndexVal;                                   /**< The value of the .idacGainIndex field of the \ref cy_stc_capsense_widget_context_t structure */
        uint8_t rowIdacModVal[CY_CAPSENSE_MAX_SUPPORTED_FREQ_NUM];  /**< The value of the .rowIdacMod field of the \ref cy_stc_capsense_widget_context_t structure */
    #endif /* (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN) */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN)
        uint8_t cdacDitherEnVal;                                    /**< The value of the .cdacDitherEn field of the \ref cy_stc_capsense_widget_context_t structure */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        uint8_t cicShiftVal;                                        /**< The value of the .cicShift field of the \ref cy_stc_capsense_widget_context_t structure */
        uint8_t rowCicShiftVal;                                     /**< The value of the .rowCicShift field of the \ref cy_stc_capsense_widget_context_t structure */
    #endif

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP) && \
         ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_FINE_EN) || \
          (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CDAC_FINE_EN) || \
          (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CDAC_FINE_EN)))
        uint8_t cdacFineVal;                                        /**< The value of the .cdacFine field of the \ref cy_stc_capsense_widget_context_t structure */
        uint8_t rowCdacFineVal;                                     /**< The value of the .rowCdacFine field of the \ref cy_stc_capsense_widget_context_t structure */
    #endif

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
        uint16_t cdacCompDividerVal;                                /**< The value of the .cdacCompDivider field of the \ref cy_stc_capsense_widget_context_t structure */
        uint8_t cdacRefVal;                                         /**< The value of the .cdacRef field of the \ref cy_stc_capsense_widget_context_t structure */
        uint8_t rowCdacRefVal;                                      /**< The value of the .rowCdacRef field of the \ref cy_stc_capsense_widget_context_t structure */
        uint8_t cicRateVal;                                         /**< The value of the .cicRate field of the \ref cy_stc_capsense_widget_context_t structure */
        uint8_t lfsrBitsVal;                                        /**< The value of the .lfsrBits field of the \ref cy_stc_capsense_widget_context_t structure */
        uint8_t cdacDitherValueVal;                                 /**< The value of the .cdacDitherValue field of the \ref cy_stc_capsense_widget_context_t structure */
        uint8_t coarseInitBypassEnVal;                              /**< The value of the .coarseInitBypassEn field of the \ref cy_stc_capsense_widget_context_t structure */
    #endif /* (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) */
}cy_stc_capsense_widget_crc_data_t;
/** \} */


/******************************************************************************/
/** \addtogroup group_capsense_structures *//** \{ */
/******************************************************************************/

/** Declares top-level Context Data Structure */
typedef struct
{
    uint16_t configId;                                          /**< 16-bit CRC calculated by the CAPSENSE&trade; Configurator tool for the CAPSENSE&trade; configuration.
                                                                   * Used by the CAPSENSE&trade; Tuner tool to identify if the FW corresponds to the specific user configuration. */
    uint16_t tunerCmd;                                          /**< Tuner Command Register \ref cy_en_capsense_tuner_cmd_t.
                                                                   * Used for the communication between the CAPSENSE&trade; Tuner tool and the middleware */
    uint16_t scanCounter;                                       /**< This counter increments after each scan of active widgets. */
    uint8_t tunerSt;                                            /**< State of CAPSENSE&trade; middleware tuner module. \ref cy_en_capsense_tuner_state_t */
    uint8_t initDone;                                           /**< Keep information whether initialization was done or not */
    volatile uint32_t status;                                   /**< Middleware status information:
                                                                  * * Bit[0-3] - The set [x] bit of the result means that the previously initiated scan for the [x] channel is in progress.
                                                                  *              For MSCv3 each bit shows a busyness of a corresponding sensing channel. 
                                                                  *              The next scan frame cannot be started (CY_CAPSENSE_BUSY_ALL_CH_MASK)
                                                                  * * Bit[4] - The last or currently scanned widget type is Active widget (CY_CAPSENSE_MW_STATE_ACTIVE_WD_SCAN_MASK)
                                                                  * * Bit[5] - The last or currently scanned widget type is Low Power widget (CY_CAPSENSE_MW_STATE_LP_WD_SCAN_MASK)
                                                                  * * Bit[6] - Reserved
                                                                  * * Bit[7] - The previously initiated scan is in progress (CY_CAPSENSE_BUSY)
                                                                  * * Bit[8] - Reserved
                                                                  * * Bit[9] - Reserved
                                                                  * * Bit[10] - A touch is detected on any low power widget. 
                                                                  *             The bit is automatically cleared when a new low power scan triggered (CY_CAPSENSE_MW_STATE_LP_ACTIVE_MASK)
                                                                  * * Bit[11] - CapSense Middleware performs BIST functionality which might include multiple HW scanning 
                                                                  *             and result processing (CY_CAPSENSE_MW_STATE_BIST_MASK)
                                                                  * * Bit[12] - The auto-calibration in Single CDAC mode (CY_CAPSENSE_MW_STATE_CALIBRATION_SINGLE_MASK)
                                                                  * * Bit[13] - The auto-calibration is in progress. The next scan frame cannot be started (CY_CAPSENSE_MW_STATE_CALIBRATION_MASK)
                                                                  * * Bit[14] - The smart sensing algorithm is in progress. The next scan frame cannot be started (CY_CAPSENSE_MW_STATE_SMARTSENSE_MASK)
                                                                  * * Bit[15] - Middleware initialization is in progress and the next 
                                                                  *             scan frame cannot be initiated (CY_CAPSENSE_MW_STATE_INITIALIZATION_MASK)
                                                                  * * Bit[16-31] - The set [x] number of the result means that the previously initiated
                                                                  *                scan for the [x] slot is completed or in progress. In CS-DMA mode, this field is set only for the first
                                                                  *                scanned slot (CY_CAPSENSE_MW_STATE_SCAN_SLOT_MASK[x])
                                                                  * \note For the the forth-generation CAPSENSE&trade; only Bit[7] is available.
                                                                  */
    uint32_t timestampInterval;                                 /**< Timestamp interval used at increasing the timestamp by Cy_CapSense_IncrementGestureTimestamp() */
    uint32_t timestamp;                                         /**< Current timestamp should be kept updated and operational, which is vital for the
                                                                   * operation of Gesture and Ballistic multiplier features */
    #if (CY_CAPSENSE_PLATFORM_BLOCK_FOURTH_GEN)
        uint8_t modCsdClk;                                      /**< The modulator clock divider for the CSD widgets
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
        uint8_t modCsxClk;                                      /**< The modulator clock divider for the CSX widgets
                                                                 * \note This field is available only for the fourth-generation CAPSENSE&trade;.
                                                                 */
    #endif

    uint8_t tunerCnt;                                           /**< Command counter of CAPSENSE&trade; middleware tuner module */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        uint16_t lpDataSt;                                       /**< State of Low Power data processing:
                                                                  * * Bit[0] = 0 (Default) - data is not copied and cannot be transmitted to Tuner
                                                                  * * Bit[0] = 1 - data copied by CAPSENSE&trade; and transmitted to Tuner.
                                                                  * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                  */
        uint8_t lpFirstSnsId;                                    /**< The first scanned low power sensor within LP frame.
                                                                  * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                  */
        uint8_t lpSnsNumber;                                     /**< The number of consecutive scanned low power sensors from the .lpFirstSnsID.
                                                                  * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                  */
        uint8_t lpNumFrame;                                      /**< The number of fully scanned low power frames available in the packet.
                                                                  * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                  */
        uint8_t lpScanCounter;                                   /**< This counter increments after each scan of low power widgets.
                                                                  * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                  */
        uint8_t lpScanSt;                                            /**< The state / status of low power sensor baselines:
                                                                  * * Bit[0] = 0 - baseline reset: does not happen
                                                                  * * Bit[0] = 1 - baseline reset: happen
                                                                  * * Bit[1] = 0 - baseline is not valid due to FIFO overflow
                                                                  * * Bit[1] = 1 - baseline is valid.
                                                                  * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                  */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */

} cy_stc_capsense_common_context_t;


#if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
    /** Declares historic rawcount low power sensors */
    typedef uint16_t cy_stc_capsense_lp_historic_context_t;
#endif


/** Declares top-level CAPSENSE&trade; context data structure */
typedef struct
{
    const cy_stc_capsense_common_config_t * ptrCommonConfig;    /**< Pointer to the common configuration structure */
    cy_stc_capsense_common_context_t * ptrCommonContext;        /**< Pointer to the common context structure */
    cy_stc_capsense_internal_context_t * ptrInternalContext;    /**< Pointer to the internal context structure */
    const cy_stc_capsense_widget_config_t * ptrWdConfig;        /**< Pointer to the widget configuration structure */
    cy_stc_capsense_widget_context_t * ptrWdContext;            /**< Pointer to the widget context structure */
    const cy_stc_capsense_pin_config_t * ptrPinConfig;          /**< Pointer to the pin configuration structure */
    const cy_stc_capsense_pin_config_t * ptrShieldPinConfig;    /**< Pointer to the shield pin configuration structure */
    cy_stc_capsense_active_scan_sns_t * ptrActiveScanSns;       /**< Pointer to the current active sensor structure */
    cy_stc_capsense_bist_context_t * ptrBistContext;            /**< Pointer to the BIST context structure */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN)
        cy_stc_msc_base_config_t * ptrBaseFrameContext;         /**< Pointer to the first member of the context structure of base configuration array
                                                                 * \note This field is available only for the fifth-generation CAPSENSE&trade;.
                                                                 */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        cy_stc_msclp_base_config_t * ptrBaseFrameContext;       /**< Pointer to the first member of the context structure of base configuration array
                                                                 * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
        uint32_t * ptrSensorFrameContext;                       /**< Pointer to the context structure of sensor configuration
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN || CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        uint32_t * ptrSensorFrameLpContext;                     /**< Pointer to the context structure of low power sensor configuration
                                                                 * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
        const cy_stc_capsense_scan_slot_t * ptrScanSlots;       /**< Pointer to the scan order slot structure
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN || CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        const cy_stc_capsense_scan_slot_t * ptrLpScanSlots;     /**< Pointer to the low power scan order slot structure
                                                                 * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN || CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        cy_stc_capsense_lp_historic_context_t * ptrLpHistoricContext;
                                                                /**< Pointer to the low power historic data
                                                                 * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                 */
    #endif /* CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP */
} cy_stc_capsense_context_t;

/** \} */


/*******************************************************************************
* Function Prototypes
*******************************************************************************/

/******************************************************************************/
/** \addtogroup group_capsense_high_level *//** \{ */
/******************************************************************************/

uint32_t Cy_CapSense_IsAnyWidgetActive(const cy_stc_capsense_context_t * context);

#if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
    uint32_t Cy_CapSense_IsAnyLpWidgetActive(const cy_stc_capsense_context_t * context);
#endif

uint32_t Cy_CapSense_IsWidgetActive(
                uint32_t widgetId,
                const cy_stc_capsense_context_t * context);
uint32_t Cy_CapSense_IsSensorActive(
                uint32_t widgetId,
                uint32_t sensorId,
                const cy_stc_capsense_context_t * context);
#if (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_PROXIMITY_EN)
    uint32_t Cy_CapSense_IsProximitySensorActive(
                    uint32_t widgetId,
                    uint32_t sensorId,
                    const cy_stc_capsense_context_t * context);
#endif
#if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_TOUCHPAD_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MATRIX_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SLIDER_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LIQUID_LEVEL_EN))
    cy_stc_capsense_touch_t * Cy_CapSense_GetTouchInfo(
                    uint32_t widgetId,
                    const cy_stc_capsense_context_t * context);
#endif
/** \} */


/******************************************************************************/
/** \addtogroup group_capsense_low_level *//** \{ */
/******************************************************************************/

cy_capsense_status_t Cy_CapSense_GetParam(
                uint32_t paramId,
                uint32_t * value,
                const void * ptrTuner,
                const cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_SetParam(
                uint32_t paramId,
                uint32_t value,
                void * ptrTuner,
                cy_stc_capsense_context_t * context);
uint16_t Cy_CapSense_GetCRC(
                const uint8_t *ptrData,
                uint32_t len);
cy_capsense_status_t Cy_CapSense_SetWidgetStatus(
                uint32_t widgetId,
                uint32_t mode,
                uint32_t value,
                cy_stc_capsense_context_t * context);
uint32_t Cy_CapSense_IsWidgetEnabled(
                uint32_t widgetId,
                const cy_stc_capsense_context_t * context);
#if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
    uint32_t Cy_CapSense_IsSlotEnabled(
                    uint32_t slotId,
                    const cy_stc_capsense_context_t * context);
#endif
/** \} */


/******************************************************************************/
/** \cond SECTION_CAPSENSE_INTERNAL */
/** \addtogroup group_capsense_internal *//** \{ */
/******************************************************************************/

cy_capsense_status_t Cy_CapSense_CheckConfigIntegrity(
                const cy_stc_capsense_context_t * context);
uint16_t Cy_CapSense_GetCrcWidget(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context);
#if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
    void Cy_CapSense_SetSnsFrameValidity(
                    uint32_t widgetId,
                    cy_stc_capsense_context_t * context);
#endif

/** This enumeration is obsolete and should not be used further.
 * Instead some of the following macros with the _GROUP suffix should be used:
 * \ref group_capsense_macros_settings.
 */
typedef enum
{
    CY_CAPSENSE_UNDEFINED_E             = 0x00u,                /**< Undefined method used at initialization */
    CY_CAPSENSE_SENSE_METHOD_CSD_E      = 0x01u,                /**< CSD sensing method */
    CY_CAPSENSE_SENSE_METHOD_CSX_E      = 0x02u,                /**< CSX sensing method */
    CY_CAPSENSE_SENSE_METHOD_BIST_E     = 0x03u,                /**< BIST sensing method */
} cy_en_capsense_sensing_method_t;


/** This structure is obsolete and should not be used further.
 * Instead cy_stc_capsense_active_scan_sns_t should be used.
 */
#define cy_stc_active_scan_sns_t        cy_stc_capsense_active_scan_sns_t


/** \} \endcond */


#if defined(__cplusplus)
}
#endif

#endif /* (defined(CY_IP_MXCSDV2) || defined(CY_IP_M0S8CSDV2) || defined(CY_IP_M0S8MSCV3) || defined(CY_IP_M0S8MSCV3LP)) */

#endif /* CY_CAPSENSE_STRUCTURE_H */


/* [] END OF FILE */
