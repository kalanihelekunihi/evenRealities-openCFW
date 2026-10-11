/***************************************************************************//**
* \file cy_capsense_lib.h
* \version 6.10.0
*
* \brief
* The file contains application programming interface to the CAPSENSE&trade; library.
*
********************************************************************************
* \copyright
* Copyright 2018-2025, Cypress Semiconductor Corporation (an Infineon company)
* or an affiliate of Cypress Semiconductor Corporation. All rights reserved.
* You may use this file only in accordance with the license, terms, conditions,
* disclaimers, and limitations in the end user license agreement accompanying
* the software package with which this file was provided.
*******************************************************************************/


#if !defined(CY_CAPSENSE_LIB_H)
#define CY_CAPSENSE_LIB_H

#include "cy_syslib.h"

#if defined(__cplusplus)
extern "C" {
#endif


/*******************************************************************************
* Public definitions
*******************************************************************************/

/******************************************************************************/
/** \addtogroup group_capsense_macros_touch *//** \{ */
/******************************************************************************/
/** No touch detected */
#define CY_CAPSENSE_ADVANCED_CENTROID_NO_TOUCHES                        (0x00u)
/** An error in touch calculation or number of detected touches is above supported touches */
#define CY_CAPSENSE_ADVANCED_CENTROID_POSITION_ERROR                    (0xFFu)
/** \} */


/******************************************************************************/
/** \addtogroup group_capsense_macros_miscellaneous *//** \{ */
/******************************************************************************/
/** Left shift of returned liquid level */
#define CY_CAPSENSE_LLW_RESULT_SHIFT                                    (14u)
/** \} */


/*******************************************************************************
* Structures
*******************************************************************************/

/******************************************************************************/
/** \addtogroup group_capsense_structures *//** \{ */
/******************************************************************************/

/** Declares Adaptive Filter configuration parameters */
typedef struct
{
    uint8_t maxK;                                   /**< Maximum filter coefficient */
    uint8_t minK;                                   /**< Minimum filter coefficient */
    uint8_t noMovTh;                                /**< No-movement threshold */
    uint8_t littleMovTh;                            /**< Little movement threshold */
    uint8_t largeMovTh;                             /**< Large movement threshold */
    uint8_t divVal;                                 /**< Divisor value */
    uint8_t reserved0;                              /**< Reserved field */
    uint8_t reserved1;                              /**< Reserved field */
} cy_stc_capsense_adaptive_filter_config_t;

/** Declares Advanced Centroid configuration parameters */
typedef struct
{
    uint16_t fingerTh;                              /**< Finger threshold of widget */
    uint16_t penultimateTh;                         /**< Penultimate threshold */
    uint16_t virtualSnsTh;                          /**< Virtual sensor threshold */
    uint16_t resolutionX;                           /**< X axis maximum position */
    uint16_t resolutionY;                           /**< Y axis maximum position */
    uint8_t crossCouplingTh;                        /**< Cross-coupling threshold */
    uint8_t snsCountX;                              /**< Number of segments on X axis */
    uint8_t snsCountY;                              /**< Number of segments on Y axis */
    uint8_t edgeCorrectionEn;                       /**< Edge correction enabled */
    uint8_t twoFingersEn;                           /**< Two-finger detection enabled */
} cy_stc_capsense_advanced_centroid_config_t;

/** Declares position structure that keep information of a single touch.
* Depending on a widget type each structure field keeps the following 
* information:
* 
* <table class="doxtable">
*   <tr>
*     <th>Structure Field</th>
*     <th>Slider</th>
*     <th>Matrix Buttons</th>
*     <th>CSD Touchpad</th>
*     <th>CSX Touchpad</th>
*     <th>Liquid Level</th>
*   </tr>
*   <tr>
*     <td>x</td>
*     <td>X-axis position</td>
*     <td>Active Column</td>
*     <td>X-axis position</td>
*     <td>X-axis position</td>
*     <td>Liquid level</td>
*   </tr>
*   <tr>
*     <td>y</td>
*     <td>Reserved</td>
*     <td>Active Row</td>
*     <td>Y-axis position</td>
*     <td>Y-axis position</td>
*     <td>Reserved</td>
*   </tr>
*   <tr>
*     <td>z</td>
*     <td>Reserved</td>
*     <td>Reserved</td>
*     <td>Reserved</td>
*     <td>MSB = Age of touch; LSB = Z-value represents a touch strength (summ of sensor diff counts divided by 16
*        that form 3x3 matrix with a local maximum in the center). It is not used by Middleware, however can be
*        re-used by users to define a touch shape or a finger size.</td>
*     <td>Reserved</td>
*   </tr>
*   <tr>
*     <td>id</td>
*     <td>Reserved</td>
*     <td>Logical number of button</td>
*     <td>Reserved</td>
*     <td>MSB = Debounce; LSB = touch ID</td>
*     <td>Reserved</td>
*   </tr>
* </table>
*/
typedef struct
{
    uint16_t x;                                     /**< X position */
    uint16_t y;                                     /**< Y position */
    uint16_t z;                                     /**< Z value */
    uint16_t id;                                    /**< ID of touch */
} cy_stc_capsense_position_t;

/** Declares touch structure used to store positions of Touchpad, Matrix buttons, Slider and
 *  Liquid Level widgets */
typedef struct
{
    cy_stc_capsense_position_t * ptrPosition;       /**< Pointer to the array containing the position information. 
                                                         A number of elements is defined by numPosition. */
    uint8_t numPosition;                            /**< Total number of detected touches on a widget:
                                                    *    * 0 - no touch is detected 
                                                    *    * 1 - a single touch is detected
                                                    *    * 2 - two touches are detected
                                                    *    * 3 - three touches are detected
                                                    *    * CY_CAPSENSE_POSITION_MULTIPLE - multiple touches are detected 
                                                    *        and information in position structure should be ignored.
                                                    *
                                                    * The below table specifies a number of touches could be reported for a specific widget.
                                                    * <table class="doxtable">
                                                    *    <tr>
                                                    *      <th colspan="2">CAPSENSE</th>
                                                    *      <th colspan="5">Number of positions</th>
                                                    *    </tr>
                                                    *    <tr align="center">
                                                    *       <td>Sensing method</td>
                                                    *       <td>Widget type</td>
                                                    *       <td>0</td>
                                                    *       <td>1</td>
                                                    *       <td>2</td>
                                                    *       <td>&emsp;&emsp;3&emsp;&emsp;</td>
                                                    *       <td>Multiple</td>
                                                    *    </tr>
                                                    *    <tr align="center">
                                                    *      <td rowspan="6">CSD</td>
                                                    *      <td>Button</td>
                                                    *      <td rowspan="10">&emsp;No touch&emsp; <br> &emsp;detected&emsp;</td>
                                                    *      <td colspan="3">Number of active sensors <br> (up to number of sensors)</td>
                                                    *      <td>N/A</td>
                                                    *    </tr>
                                                    *    <tr align="center">
                                                    *      <td>Matrix button</td>
                                                    *      <td>Single touch <br> detected</td>
                                                    *      <td>N/A</td>
                                                    *      <td>N/A</td>
                                                    *      <td>Multiple touches <br>  detected</td>
                                                    *    </tr>
                                                    *    <tr align="center">
                                                    *      <td>Linear slider</td>
                                                    *      <td>Single touch <br> detected</td>
                                                    *      <td>N/A</td>
                                                    *      <td>N/A</td>
                                                    *      <td>N/A</td>
                                                    *    </tr>
                                                    *    <tr align="center">
                                                    *      <td>Radial slider</td>
                                                    *      <td>Single touch <br> detected</td>
                                                    *      <td>N/A</td>
                                                    *      <td>N/A</td>
                                                    *      <td>N/A</td>
                                                    *    </tr>
                                                    *    <tr align="center">
                                                    *      <td>Touchpad</td>
                                                    *      <td>Single touch <br> detected</td>
                                                    *      <td>Two touches <br> detected</td>
                                                    *      <td>N/A</td>
                                                    *      <td>Multiple touches <br> detected</td>
                                                    *    </tr>
                                                    *    <tr align="center">
                                                    *      <td>Proximity</td>
                                                    *      <td colspan="3">Number of active sensors <br> (up to number of sensors)</td>
                                                    *      <td>N/A</td>
                                                    *    </tr>
                                                    *    <tr align="center">
                                                    *      <td rowspan="4">CSX</td>
                                                    *      <td>Button</td>
                                                    *      <td colspan="3">Number of active sensors <br> (up to number of sensors)</td>
                                                    *      <td>N/A</td>
                                                    *    </tr>
                                                    *    <tr align="center">
                                                    *      <td>Matrix button</td>
                                                    *      <td colspan="3">Number of active sensors <br> (up to number of sensors)</td>
                                                    *      <td>N/A</td>
                                                    *    </tr>
                                                    *    <tr align="center">
                                                    *      <td>Linear slider</td>
                                                    *      <td>Single touch <br> detected</td>
                                                    *      <td>N/A</td>
                                                    *      <td>N/A</td>
                                                    *      <td>N/A</td>
                                                    *    </tr>
                                                    *    <tr align="center">
                                                    *      <td>Touchpad</td>
                                                    *      <td colspan="3">Number of touches <br> (up to 3)</td>
                                                    *      <td>N/A</td>
                                                    *    </tr>
                                                    * </table>
                                                    */
} cy_stc_capsense_touch_t;

/** Declares HW smart sensing algorithm data structure for fourth-generation CAPSENSE&trade; */
typedef struct
{
    uint32_t sensorCap;                             /**< Sensor parasitic capacitance in fF 10^-15 */
    uint32_t iDacGain;                              /**< IDAC gain in pA */
    uint16_t * ptrSenseClk;                         /**< Pointer to SnsClk divider */
    uint16_t * sigPFC;                              /**< Pointer to sigPFC value (75% of Signal Per Finger Capacitance) */
    uint16_t snsClkConstantR;                       /**< Resistance in series to a sensor */
    uint16_t vRef;                                  /**< Vref in mVolts  */
    uint16_t fingerCap;                             /**< Finger capacitance in fF 10^-15 (Set in Basic tab in pF 10^-12) */
    uint16_t snsClkInputClock;                      /**< Frequency for sense clock divider in kHz */
    uint16_t calTarget;                             /**< Calibration target in percentage */
    uint8_t iDacMod;                                /**< Modulation idac code */
    uint8_t iDacComp;                               /**< Compensation idac code */
} cy_stc_capsense_auto_tune_config_t;

/** Declares HW smart sensing algorithm data structure for fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade; */
typedef struct
{
    uint32_t snsCapacitance;                        /**< Sensor parasitic capacitance in fF 10^-15 */
    uint32_t modClock;                              /**< Modulation clock frequency in Hz */
    uint16_t nSub0;                                 /**< Base number of sub-conversions */
    uint16_t nSub1;                                 /**< Final number of sub-conversions */
    uint16_t raw;                                   /**< Sensor raw counts */
    uint16_t snsResistance;                         /**< Resistance in series to a sensor */
    uint16_t kRef0;                                 /**< Base sense frequency */
    uint16_t kRef1;                                 /**< Final sense frequency */
    uint16_t fingerCap;                             /**< Finger capacitance in fF 10^-15 (Set in Basic tab in pF 10^-12) */
    uint16_t sigPFC;                                /**< sigPFC value (75% of signal Per Finger Capacitance) */
    uint8_t refCdac;                                /**< Reference CAP DAC code for getting capacitance and calibration target for getting Nsub */
    uint8_t correctionCoeff;                        /**< Correction coefficient for CTRL_MUX mode */
} cy_stc_capsense_hw_smartsense_config_t;

/** Declares Noise envelope data structure when smart sensing algorithm is enabled */
typedef struct
{
    uint16_t param0;                                /**< Parameter 0 configuration */
    uint16_t param1;                                /**< Parameter 1 configuration */
    uint16_t param2;                                /**< Parameter 2 configuration */
    uint16_t param3;                                /**< Parameter 3 configuration */
    uint16_t param4;                                /**< Parameter 4 configuration */
    uint8_t  param5;                                /**< Parameter 5 configuration */
    uint8_t  param6;                                /**< Parameter 6 configuration */
} cy_stc_capsense_smartsense_csd_noise_envelope_t;

/** Declares Update Thresholds structure */
typedef struct
{
    uint16_t fingerTh;                              /**< Widget finger threshold */
    uint8_t  noiseTh;                               /**< Widget noise threshold */
    uint8_t  nNoiseTh;                              /**< Widget negative noise threshold */
    uint8_t  hysteresis;                            /**< Widget hysteresis for the signal crossing finger threshold */
} cy_stc_capsense_smartsense_update_thresholds_t;

/** Declares Ballistics Multiplier Configuration data structure */
typedef struct
{
    uint8_t  accelCoeff;                            /**< Acceleration Coefficient */
    uint8_t  speedCoeff;                            /**< Speed Coefficient */
    uint8_t  divisorValue;                          /**< Divisor Value */
    uint8_t  speedThresholdX;                       /**< Speed Threshold X */
    uint8_t  speedThresholdY;                       /**< Speed Threshold Y */
    uint8_t  reserved0;                             /**< Reserved field */
    uint8_t  reserved1;                             /**< Reserved field */
    uint8_t  reserved2;                             /**< Reserved field */
} cy_stc_capsense_ballistic_config_t;

/** Declares Ballistics Multiplier Configuration data structure */
typedef struct
{
    uint32_t currentTimestamp;                      /**< Current timestamp */
    uint32_t oldTimestamp;                          /**< Previous timestamp */
    int32_t deltaXfrac;                             /**< Fraction of X-axis displacement */
    int32_t deltaYfrac;                             /**< Fraction of Y-axis displacement */
    uint16_t x;                                     /**< X-axis position */
    uint16_t y;                                     /**< Y-axis position */
    uint8_t touchNumber;                            /**< Current number of touches */
    uint8_t oldTouchNumber;                         /**< Previous number of touches */
    uint8_t reserved0;                              /**< Reserved field */
    uint8_t reserved1;                              /**< Reserved field */
} cy_stc_capsense_ballistic_context_t;

/** Declares Ballistic Displacement structure */
typedef struct
{
    int16_t deltaX;                                 /**< X-axis displacement */
    int16_t deltaY;                                 /**< Y-axis displacement */
} cy_stc_capsense_ballistic_delta_t;

/** \} */

/** Declares ALP filter data structure */
typedef struct
{
    uint32_t dataParam0;                            /**< Parameter 0 context */
    uint16_t dataParam1;                            /**< Parameter 1 context */
    uint16_t dataParam2;                            /**< Parameter 2 context */
    uint16_t dataParam3;                            /**< Parameter 3 context */
    uint16_t dataParam4;                            /**< Parameter 4 context */
    uint16_t dataParam5;                            /**< Parameter 5 context */
    uint16_t dataParam6;                            /**< Parameter 6 context */
    uint8_t dataParam7;                             /**< Parameter 7 context */
} cy_stc_capsense_alp_fltr_channel_t;

/** Declares ALP filter configuration structure */
typedef struct
{
    uint16_t configParam0;                          /**< Parameter 0 configuration */
    uint16_t configParam1;                          /**< Parameter 1 configuration */
    uint16_t configParam2;                          /**< Parameter 2 configuration */
    uint8_t configParam3;                           /**< Parameter 3 configuration */
    uint8_t configParam4;                           /**< Parameter 4 configuration */
    uint8_t configParam5;                           /**< Parameter 5 configuration */
} cy_stc_capsense_alp_fltr_config_t;


/*******************************************************************************
* Function Prototypes
*******************************************************************************/

/******************************************************************************/
/** \cond SECTION_CAPSENSE_INTERNAL */
/** \addtogroup group_capsense_internal *//** \{ */
/******************************************************************************/

/*******************************************************************************
* Function Name: Cy_CapSense_AdaptiveFilterInitialize_Lib
****************************************************************************//**
*
* Initializes the Adaptive Filter context structure by writing default
* adaptive coefficient for the AIIR filter.
*
* \param config
* The pointer to the configuration structure of the Adaptive Filter.
*
* \param context
* The pointer to the context structure of the Adaptive Filter.
*
*******************************************************************************/
void Cy_CapSense_AdaptiveFilterInitialize_Lib(
                const cy_stc_capsense_adaptive_filter_config_t * config, 
                cy_stc_capsense_position_t * context);

/*******************************************************************************
* Function Name: Cy_CapSense_AdaptiveFilterRun_Lib
****************************************************************************//**
*
* This function runs the Adaptive Filter algorithm for the centroid position.
*
* The function supposes that the filter history is updated at first touch
* outside of the library. I.e. at the first touchdown the filter history has
* to be initialized by touch positions before calling this function.
*
* \param config
* The pointer to the configuration structure of the Adaptive Filter.
*
* \param context
* The pointer to the context structure of the Adaptive Filter.
*
* \param currentX
* The pointer to X position.
*
* \param currentY
* The pointer to Y position.
*
*******************************************************************************/
void Cy_CapSense_AdaptiveFilterRun_Lib(
                const cy_stc_capsense_adaptive_filter_config_t * config,
                cy_stc_capsense_position_t * context, 
                uint32_t * currentX, 
                uint32_t * currentY);

/*******************************************************************************
* Function Name: Cy_CapSense_AdvancedCentroidGetTouchCoordinates_Lib
****************************************************************************//**
*
* This API calculates the centroids for up to two fingers.
*
* \param config
* The pointer to the configuration structure of the Advanced Centroid.
*
* \param ptrSns
* The pointer to the array with sensor raw counts.
*
* \param touch
* The pointer to touch structure.
*
*******************************************************************************/
void Cy_CapSense_AdvancedCentroidGetTouchCoordinates_Lib(
                const cy_stc_capsense_advanced_centroid_config_t * config,
                const uint16_t * ptrSns,
                cy_stc_capsense_touch_t * touch);

/*******************************************************************************
* Function Name: Cy_CapSense_BallisticMultiplier_Lib
****************************************************************************//**
*
* This function runs the ballistic multiplier.
*
* \param config
* The pointer to the configuration structure of the Advanced Centroid.
*
* \param touch
* The pointer to touch structure.
*
* \param displacement
* The pointer to position displacement
*
* \param timestamp
* The current timestamp
*
* \param context
* The pointer to the context structure of the Ballistic Multiplier.
*
*******************************************************************************/
void Cy_CapSense_BallisticMultiplier_Lib(
                const cy_stc_capsense_ballistic_config_t * config, 
                const cy_stc_capsense_touch_t * touch,
                cy_stc_capsense_ballistic_delta_t * displacement,
                uint32_t timestamp,
                cy_stc_capsense_ballistic_context_t * context);

/*******************************************************************************
* Function Name: Cy_CapSense_AlpRun_Lib
****************************************************************************//**
*
* Applies advanced low pass filter algorithm on raw counts.
*
* \param ptrFilterObj
* The pointer to sensor filter data structure
*
* \param ptrFilterConfig
* The pointer to sensor filter configuration structure
*
* \param rawCount
* The pointer to sensor raw count
*
* \param baseline
* The pointer to sensor baseline
*
*******************************************************************************/
void Cy_CapSense_AlpRun_Lib(
                cy_stc_capsense_alp_fltr_channel_t * ptrFilterObj, 
                const cy_stc_capsense_alp_fltr_config_t * ptrFilterConfig,
                uint16_t * rawCount, 
                const uint16_t * baseline);

/*******************************************************************************
* Function Name: Cy_CapSense_AlpInitialize_Lib
****************************************************************************//**
*
* Initializes filter data structure.
*
* \param ptrFilterObj
* Pointer to filter data structure
*
* \param rawCount
* Pointer to sensor raw count
*
*******************************************************************************/
void Cy_CapSense_AlpInitialize_Lib(
                cy_stc_capsense_alp_fltr_channel_t * ptrFilterObj, 
                const uint16_t * rawCount);

/*******************************************************************************
* Function Name: Cy_CapSense_AlpResetState_Lib
****************************************************************************//**
*
* Resets state machine of the filter.
*
* \param ptrFilterObj
* Pointer to the filter data structure
*
*******************************************************************************/
void Cy_CapSense_AlpResetState_Lib(
                cy_stc_capsense_alp_fltr_channel_t * ptrFilterObj);

/*******************************************************************************
* Function Name: Cy_CapSense_AlpGetAverage_Lib
****************************************************************************//**
*
* Returns the output of internal average filter
*
* \param ptrFilterObj
* Pointer to the filter data structure
*
* \return
* Returns the output of internal average filter
*
*******************************************************************************/
uint32_t Cy_CapSense_AlpGetAverage_Lib(
                const cy_stc_capsense_alp_fltr_channel_t * ptrFilterObj);

/*******************************************************************************
* Function Name: Cy_CapSense_TunePrescalers_Lib
****************************************************************************//**
*
* This internal function tunes the Sense Clock divider.
*
* \param config
* The configuration structure.
*
* \return 
* Cp in fF (10^-15)
*
*******************************************************************************/
uint32_t Cy_CapSense_TunePrescalers_Lib(
                cy_stc_capsense_auto_tune_config_t * config);

/*******************************************************************************
* Function Name: Cy_CapSense_TuneSensitivity_Lib
****************************************************************************//**
*
* Configure scanning resolution to achieve the sufficient sensitivity.
*
* This function requires non-zero Modulator IDAC code (if IDAC is equal to zero it 
* is considered as non-valid use case).
*
* \param config
* The configuration structure.
*
* \return 
* Scan resolution
*
*******************************************************************************/
uint8_t Cy_CapSense_TuneSensitivity_Lib(
                cy_stc_capsense_auto_tune_config_t * config);

/*******************************************************************************
* Function Name: Cy_CapSense_GetSmartSenseCapacitance
****************************************************************************//**
*
* Returns capacitance that corresponds to the provided parameters.
*
* \param autoTuneConfig
* The configuration structure.
*
* \return
* Returns capacitance in femto-farads.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetSmartSenseCapacitance(
                cy_stc_capsense_hw_smartsense_config_t * autoTuneConfig);

/*******************************************************************************
* Function Name: Cy_CapSense_GetSmartSenseFrequencyDivider
****************************************************************************//**
*
* Returns minimum sense clock divider.
*
* \param autoTuneConfig
* The configuration structure.
*
* \return
* Returns sense clock divider.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetSmartSenseFrequencyDivider(
                cy_stc_capsense_hw_smartsense_config_t * autoTuneConfig);

/*******************************************************************************
* Function Name: Cy_CapSense_GetSmartSenseNumSubconversions
****************************************************************************//**
*
* Returns optimum number of sub-conversions.
*
* \param autoTuneConfig
* The configuration structure.
*
* \return
* Returns number of sub-conversions.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetSmartSenseNumSubconversions(
                cy_stc_capsense_hw_smartsense_config_t * autoTuneConfig);

/*******************************************************************************
* Function Name: Cy_CapSense_UpdateThresholds_Lib
****************************************************************************//**
*
* Updates noise and finger thresholds for a specified widget.
*
* This function comprises an algorithm of thresholds auto-tune. The thresholds
* object contains updated thresholds after this API is called.
*
* \param ptrNoiseEnvelope 
* The pointer to the noise-envelope object in RAM.
*
* \param ptrThresholds    
* The pointer to the thresholds object.
*
* \param sigPFC           
* Signal per touch sensitivity.
*
* \param startFlag           
* The flag indicates a first sensor in a widget.
*
*******************************************************************************/
void Cy_CapSense_UpdateThresholds_Lib(
                const cy_stc_capsense_smartsense_csd_noise_envelope_t * ptrNoiseEnvelope,
                cy_stc_capsense_smartsense_update_thresholds_t * ptrThresholds,
                uint16_t sigPFC,
                uint32_t startFlag);

/*******************************************************************************
* Function Name: Cy_CapSense_InitializeNoiseEnvelope_Lib
****************************************************************************//**
*
* Initializes the noise-envelope filter.
*
* \param rawCount         
* The RawCount value for a given sensor.
*
* \param sigPFC           
* Signal per finger capacitance.
*
* \param ptrNoiseEnvelope 
* The pointer to the noise-envelope RAM object of the sensor.
*
*******************************************************************************/
void Cy_CapSense_InitializeNoiseEnvelope_Lib(
                uint16_t rawCount,
                uint16_t sigPFC,
                cy_stc_capsense_smartsense_csd_noise_envelope_t * ptrNoiseEnvelope);

/*******************************************************************************
* Function Name: Cy_CapSense_RunNoiseEnvelope_Lib
****************************************************************************//**
*
* Runs the noise-envelope filter.
*
* \param rawCount         
* The RawCount value for a given sensor.
*
* \param sigPFC           
* Signal per touch sensitivity.
*
* \param ptrNoiseEnvelope 
* The pointer to the noise-envelope RAM object of the sensor.
*
*******************************************************************************/
void Cy_CapSense_RunNoiseEnvelope_Lib(
                uint16_t rawCount,
                uint16_t sigPFC,
                cy_stc_capsense_smartsense_csd_noise_envelope_t * ptrNoiseEnvelope);

/*******************************************************************************
* Function Name: Cy_CapSense_GetLiquidLevel
****************************************************************************//**
*
* Calculates liquid level.
*
* \param ptrLlwConfig
* Specifies the pointer to liquid level configuration.
*
* \param ptrLlwContext
* Specifies the pointer to sensor context structure which belongs to the
* desired widget.
*
* \return
* Returns a calculated liquid level in range
* from 0 to 2 ^ CY_CAPSENSE_LLW_RESULT_SHIFT
*
*******************************************************************************/
uint16_t Cy_CapSense_GetLiquidLevel_Lib(
                const uint8_t * ptrLlwConfig,
                const uint16_t * ptrLlwContext);

/*******************************************************************************
* Function Name: Cy_CapSense_CommonModeFilter_Lib
****************************************************************************//**
*
* Applies common mode filter to all sensors inside a desired widget.
*
* \param cmfThreshold
* Specifies the common mode filter threshold.
*
* \param numSns
* Specifies the number of sensors in a desired widget.
*
* \param ptrSnsContext
* Specifies the pointer to the sensor context structure. The structure size
* is 10-byte wide.
*
*******************************************************************************/
void Cy_CapSense_CommonModeFilter_Lib(const uint16_t cmfThreshold,
                const uint16_t numSns,
                uint16_t * ptrSnsContext);

/*******************************************************************************
* Function Name: Cy_CapSense_GetSmartSenseIsxInductance
****************************************************************************//**
*
* Returns inductance per resistance that corresponds to the provided parameters.
*
* \param autoTuneConfig
* The configuration structure.
*
* \return
* Returns inductance divided by total resistance in 10^-10.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetSmartSenseIsxInductance(
                cy_stc_capsense_hw_smartsense_config_t * autoTuneConfig);

/*******************************************************************************
* Function Name: Cy_CapSense_GetSmartSenseIsxFrequencyDivider
****************************************************************************//**
*
* Returns sense clock divider.
*
* \param autoTuneConfig
* The configuration structure.
*
* \return
* Returns sense clock divider.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetSmartSenseIsxFrequencyDivider(
                cy_stc_capsense_hw_smartsense_config_t * autoTuneConfig);

/*******************************************************************************
* Function Name: Cy_CapSense_GetSmartSenseIsxNumSubconversions
****************************************************************************//**
*
* Returns optimum number of sub-conversions.
*
* \param autoTuneConfig
* The configuration structure.
*
* \return
* Returns the calculated number of sub-conversions.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetSmartSenseIsxNumSubconversions(
                cy_stc_capsense_hw_smartsense_config_t * autoTuneConfig);

/** \} \endcond */

#if defined(__cplusplus)
}
#endif

#endif /* CY_CAPSENSE_LIB_H */


/* [] END OF FILE */
