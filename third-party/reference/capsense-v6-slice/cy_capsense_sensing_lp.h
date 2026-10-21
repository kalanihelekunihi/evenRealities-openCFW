/***************************************************************************//**
* \file cy_capsense_sensing_lp.h
* \version 6.10.0
*
* \brief
* This file provides the function prototypes specific to the scanning module.
*
********************************************************************************
* \copyright
* Copyright 2020-2025, Cypress Semiconductor Corporation (an Infineon company)
* or an affiliate of Cypress Semiconductor Corporation. All rights reserved.
* You may use this file only in accordance with the license, terms, conditions,
* disclaimers, and limitations in the end user license agreement accompanying
* the software package with which this file was provided.
*******************************************************************************/


#if !defined(CY_CAPSENSE_SENSING_LP_H)
#define CY_CAPSENSE_SENSING_LP_H

#include "cy_syslib.h"
#include "cy_sysclk.h"
#include "cy_capsense_common.h"
#include "cy_capsense_structure.h"
#if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
    #include "cy_msclp.h"
#endif

#if (defined(CY_IP_M0S8MSCV3LP))

#if defined(__cplusplus)
extern "C" {
#endif


/*******************************************************************************
* Function Prototypes
*******************************************************************************/

/******************************************************************************/
/** \addtogroup group_capsense_high_level *//** \{ */
/******************************************************************************/
#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
    cy_capsense_status_t Cy_CapSense_ScanLpSlots(
                    uint32_t startLpSlotId,
                    uint32_t numberLpSlots,
                    cy_stc_capsense_context_t * context);
    cy_capsense_status_t Cy_CapSense_ScanAllLpSlots(
                    cy_stc_capsense_context_t * context);
    cy_capsense_status_t Cy_CapSense_ScanAllLpWidgets(
                    cy_stc_capsense_context_t * context);
    cy_capsense_status_t Cy_CapSense_ConfigureMsclpWotTimer(
                    uint32_t wakeupTimer,
                    cy_stc_capsense_context_t * context);
#endif /* CY_CAPSENSE_LP_EN */

cy_capsense_status_t Cy_CapSense_ConfigureMsclpTimer(
                uint32_t wakeupTimer,
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_IloCompensate(
                cy_stc_capsense_context_t * context);
/** \} */


/******************************************************************************/
/** \addtogroup group_capsense_low_level *//** \{ */
/******************************************************************************/
#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
    cy_capsense_status_t Cy_CapSense_LpSlotPinState(
                    uint32_t lpSlotId,
                    const cy_stc_capsense_electrode_config_t * ptrEltdCfg,
                    uint32_t pinState,
                    cy_stc_capsense_context_t * context);
#endif /* CY_CAPSENSE_LP_EN */

#if (((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CALIBRATION_EN) || \
      (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CALIBRATION_EN) || \
      (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CALIBRATION_EN)) && \
      (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN))
cy_capsense_status_t Cy_CapSense_CalibrateAllLpWidgets(
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_CalibrateAllLpSlots(
                cy_stc_capsense_context_t * context);
#endif

#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_RC_HW_IIR_FILTER_EN)
    cy_capsense_status_t Cy_CapSense_ScanInitializeHwIirAllSlots(
                cy_stc_capsense_context_t * context);
    cy_capsense_status_t Cy_CapSense_ScanInitializeHwIirSlots(
                uint32_t startSlotId,
                uint32_t numberSlots,
                cy_stc_capsense_context_t * context);
#endif
/** \} */


/******************************************************************************/
/** \cond SECTION_CAPSENSE_INTERNAL */
/** \addtogroup group_capsense_internal *//** \{ */
/******************************************************************************/
cy_capsense_status_t Cy_CapSense_ScanSlots_V3Lp(
                uint32_t startSlotId,
                uint32_t numberSlots,
                cy_stc_capsense_context_t * context);
void Cy_CapSense_ScanSlotsInternal(
                uint32_t startSlotId,
                uint32_t numberSlots,
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_ScanWidget_V3Lp(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_ScanSensor_V3Lp(
                uint32_t widgetId,
                uint32_t sensorId,
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_ScanAllWidgets_V3Lp(
                cy_stc_capsense_context_t * context);
void Cy_CapSense_InterruptHandler_V3Lp(
                const MSCLP_Type * base,
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_RepeatScan(
                cy_stc_capsense_context_t * context);
void Cy_CapSense_SetBusyFlags(cy_stc_capsense_context_t * context);
void Cy_CapSense_ClrBusyFlags(cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_SsInitialize(
                cy_stc_capsense_context_t * context);
uint32_t Cy_CapSense_WatchdogCyclesNum(
                uint32_t desiredTimeUs,
                uint32_t cpuFreqMHz,
                uint32_t cyclesPerLoop);
void Cy_CapSense_ScanISR(void * capsenseContext);
void Cy_CapSense_SetCmodInDesiredState(
                uint32_t desiredDriveMode,
                en_hsiom_sel_t desiredHsiom,
                uint32_t desiredMscCtrl,
                const cy_stc_capsense_context_t * context);
void Cy_CapSense_InitActivePtrSns(
                uint32_t sensorId,
                cy_stc_capsense_context_t * context);
void Cy_CapSense_InitActivePtrWd(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context);
void Cy_CapSense_InitActivePtr(
                uint32_t widgetId,
                uint32_t sensorId,
                cy_stc_capsense_context_t * context);
void Cy_CapSense_SetIOsInDesiredState(
                uint32_t desiredDriveMode,
                en_hsiom_sel_t desiredHsiom,
                uint32_t desiredPinOutput,
                uint32_t desiredMscCtrl,
                const cy_stc_capsense_context_t * context);
void Cy_CapSense_SsConfigPinRegisters(
                GPIO_PRT_Type * base,
                uint32_t pinNum,
                uint32_t dm,
                en_hsiom_sel_t hsiom,
                uint32_t mscCtrl);
cy_capsense_status_t Cy_CapSense_SlotPinState_V3Lp(
                uint32_t slotId,
                const cy_stc_capsense_electrode_config_t * ptrEltdCfg,
                uint32_t pinState,
                cy_stc_capsense_context_t * context);

#if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CALIBRATION_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CALIBRATION_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CALIBRATION_EN))
#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_REF_AUTO_EN)
    cy_capsense_status_t Cy_CapSense_CalibrateRefCdac(
                    uint32_t widgetId,
                    cy_stc_capsense_context_t * context);
#endif
#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_FINE_AUTO_EN)
    cy_capsense_status_t Cy_CapSense_CalibrateFineCdac(
                    uint32_t widgetId,
                    cy_stc_capsense_context_t * context);
#endif
#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_COMP_DIV_AUTO_EN)
    cy_capsense_status_t Cy_CapSense_CalibrateCompDivider(
                    uint32_t widgetId,
                    cy_stc_capsense_context_t * context);
#endif
#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_COMP_AUTO_EN)
    cy_capsense_status_t Cy_CapSense_CalibrateCompCdac(
                    uint32_t widgetId,
                    cy_stc_capsense_context_t * context);
#endif
cy_capsense_status_t Cy_CapSense_VerifyCalibration(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_VerifyReferenceCdac(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_CalibrateAllWidgets_V3Lp(
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_CalibrateAllSlots_V3Lp(
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_SetCalibrationTarget_V3Lp(
                uint32_t calibrTarget,
                uint32_t snsMethod,
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_CalibrateWidget_V3Lp(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context);
#endif
cy_capsense_status_t Cy_CapSense_WaitEndScan(
                uint32_t timeout,
                cy_stc_capsense_context_t * context);
void Cy_CapSense_SetShieldPinsInDesiredState(
                uint32_t desiredDriveMode,
                en_hsiom_sel_t desiredHsiom,
                uint32_t desiredMscCtrl,
                const cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_SwitchHwConfiguration(
                uint32_t configuration,
                cy_stc_capsense_context_t * context);
uint32_t Cy_CapSense_GetLfsrDitherVal(
                uint32_t lfsrBits,
                uint32_t lfsrScale);
uint32_t Cy_CapSense_GetLfsrDitherLimit(
                uint32_t snsClkDivider,
                uint32_t snsClkDividerMin,
                uint32_t ditherLimitPercents,
                uint32_t lfsrScale);
cy_capsense_status_t Cy_CapSense_InitializeSourceSenseClk(
                const cy_stc_capsense_context_t * context);

#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_EN)
    cy_capsense_status_t Cy_CapSense_SsAutoTune(
                    cy_stc_capsense_context_t * context);
    cy_capsense_status_t Cy_CapSense_IsSmarSenseWidgetValid(
                    const cy_stc_capsense_widget_config_t * ptrWdConfig);
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN)
        uint32_t Cy_CapSense_SsSquareRoot16(uint16_t value);
    #endif
#endif

cy_capsense_mw_state_t Cy_CapSense_MwState_V3Lp(
                const cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_ScanAbort_V3Lp(
                cy_stc_capsense_context_t * context);

#if (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CIC2_FILTER_EN)
    uint32_t Cy_CapSense_GetCIC2SamplesMax(uint32_t cic2Rate);
    uint32_t Cy_CapSense_GetCIC2HwDivider(uint32_t cic2Samples);
    uint32_t Cy_CapSense_GetCIC2HwShift(uint32_t cic2Samples);
    #if (CY_CAPSENSE_CIC2_FILTER_AUTO_EN)
        cy_capsense_status_t Cy_CapSense_InitializeCic2Shift(
                        cy_stc_capsense_context_t * context);
    #endif
    #if (CY_CAPSENSE_CIC_RATE_MODE_AUTO_EN)
        cy_capsense_status_t Cy_CapSense_InitializeCic2Rate(
                        cy_stc_capsense_context_t * context);
    #endif
#endif /* #if (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CIC2_FILTER_EN) */

void Cy_CapSense_SetupCpuOperatingMode(cy_stc_capsense_context_t * context);
void Cy_CapSense_StartCpuScan(const uint32_t * scanConfig, cy_stc_capsense_context_t * context);
uint32_t Cy_CapSense_WaitEndOfCpuScan(uint32_t watchdogTime, cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_ExecuteSaturatedScan(
                uint32_t * ptrMaxRaw,
                uint32_t widgetId,
                uint32_t scanSlotId,
                uint32_t mode,
                cy_stc_capsense_context_t * context);
void Cy_CapSense_ConfigureSaturationMode(
                cy_stc_capsense_context_t * context);
uint32_t Cy_CapSense_GetScanWatchdogTime(
                uint32_t widgetId,
                uint32_t scanSlotId,
                cy_stc_capsense_context_t * context);

/** \} \endcond */


/*******************************************************************************
* Local definition
*******************************************************************************/
#define CY_CAPSENSE_MSCLP_INTR_ALL_MSK                          (MSCLP_INTR_MASK_SUB_SAMPLE_Msk |\
                                                                 MSCLP_INTR_MASK_SAMPLE_Msk |\
                                                                 MSCLP_INTR_MASK_SCAN_Msk |\
                                                                 MSCLP_INTR_MASK_INIT_Msk |\
                                                                 MSCLP_INTR_MASK_FRAME_Msk |\
                                                                 MSCLP_INTR_MASK_CONFIG_REQ_Msk |\
                                                                 MSCLP_INTR_MASK_FIFO_UNDERFLOW_Msk |\
                                                                 MSCLP_INTR_MASK_FIFO_OVERFLOW_Msk)

#define CY_CAPSENSE_MSCLP_INTR_LP_ALL_MSK                       (MSCLP_INTR_LP_SIG_DET_Msk |\
                                                                 MSCLP_INTR_LP_FR_TIMEOUT_Msk |\
                                                                 MSCLP_INTR_LP_FRAME_Msk |\
                                                                 MSCLP_INTR_LP_CE_DONE_Msk |\
                                                                 MSCLP_INTR_LP_IMO_UP_Msk)

#define CY_CAPSENSE_CDAC_MAX_CODE                               (0xFFu)
#define CY_CAPSENSE_CAL_REF_CDAC_MIN_CODE                       (0x7u)
#define CY_CAPSENSE_REF_CDAC_LSB_X100                           (886u)
#define CY_CAPSENSE_MULTIPLIER_TWO                              (2u)

#define CY_CAPSENSE_CAL_REF_CDAC_MIDDLE_CODE                    (0x80u)
#define CY_CAPSENSE_CAL_FINE_CDAC_MIDDLE_CODE                   (0x10u)
#define CY_CAPSENSE_CAL_COMP_CDAC_MIDDLE_CODE                   (0x80u)

#define CY_CAPSENSE_CAL_FINE_CDAC_Msk                           (0x1FUL)
#define CY_CAPSENSE_CAL_CDAC_Msk                                (0x1FE0UL)
#define CY_CAPSENSE_CAL_CDAC_Pos                                (5u)

#define CY_CAPSENSE_CAL_MIDDLE_VALUE                            (0x1000u)
#define CY_CAPSENSE_CAL_NUM_SCANS_VALUE                         (8u)
#define CY_CAPSENSE_CAL_FINE_NUM_SCANS_VALUE                    (13u)

#define CY_CAPSENSE_CAL_MODE_REF_CDAC_SUC_APPR                  (0u)
#define CY_CAPSENSE_CAL_MODE_COMP_CDAC_SUC_APPR                 (2u)

#define CY_CAPSENSE_CAL_MODE_COMP_CDAC_CODE_MIN                 (0u)
#define CY_CAPSENSE_CAL_MODE_COMP_CDAC_CODE_MAX                 (1u)
#define CY_CAPSENSE_CAL_MODE_COMP_CDAC_CODE_VAL                 (2u)

#define CY_CAPSENSE_MRSS_TURN_ON                                (0u)
#define CY_CAPSENSE_MRSS_TURN_OFF                               (1u)
#define CY_CAPSENSE_MRSS_IMO_TURN_ON                            (2u)
#define CY_CAPSENSE_MRSS_IMO_TURN_OFF                           (3u)

#define CY_CAPSENSE_LFSR_RANGE_0_DITHER_MAX                     (2u)
#define CY_CAPSENSE_LFSR_RANGE_1_DITHER_MAX                     (4u)
#define CY_CAPSENSE_LFSR_RANGE_2_DITHER_MAX                     (8u)
#define CY_CAPSENSE_LFSR_RANGE_3_DITHER_MAX                     (16u)

#define CY_CAPSENSE_2PH_PRS_SNS_CLOCK_DIVIDER_SHIFT             (1u)
#define CY_CAPSENSE_4PH_PRS_SNS_CLOCK_DIVIDER_SHIFT             (2u)

#define CY_CAPSENSE_DIRECT_SNS_CLOCK_DIVIDER_MAX                (4096u)
#define CY_CAPSENSE_2PH_DIRECT_SNS_CLOCK_DIVIDER_MIN            (4u)
#define CY_CAPSENSE_4PH_DIRECT_SNS_CLOCK_DIVIDER_MIN            (8u)

#define CY_CAPSENSE_SMARTSENSE_WD_MAX_NUMBER                    (64u)

#define CY_CAPSENSE_SMARTSENSE_CSD_PRELIMINARY_SCAN_NSUB        (64u)
#define CY_CAPSENSE_SMARTSENSE_CSD_PRELIMINARY_SCAN_SNS_CLK     (256u)
#define CY_CAPSENSE_SMARTSENSE_CSD_PRELIMINARY_SCAN_REF_CDAC    (100u)

#define CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_NSUB        (185u)
#define CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_SNS_CLK     (200u)
#define CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_REF_CDAC    (255u)
#define CY_CAPSENSE_SMARTSENSE_ISX_SNS_CLK_MIN                  (8u)
#define CY_CAPSENSE_SMARTSENSE_ISX_SNS_CLK_STEP                 (4u)
#define CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_STOP        (95u)

#define CY_CAPSENSE_MAX_EPI_KREF_DELAY_PRS_NUMBER               (255u)
#define CY_CAPSENSE_MAX_PRO_WAIT_KREF_DELAY_PRS_NUMBER          (31u)

#define CY_CAPSENSE_CALIBRATION_REF_CDAC_MASK                   (0x01u)
#define CY_CAPSENSE_CALIBRATION_COMP_DIV_MASK                   (0x02u)
#define CY_CAPSENSE_CALIBRATION_COMP_CDAC_MASK                  (0x04u)

#define CY_CAPSENSE_SLOT_COUNT_MAX_VALUE                        (0xFFFFu)

#define CY_CAPSENSE_RC_HW_IIR_FILTER_COEFF_POS                  (24u)
#define CY_CAPSENSE_RC_HW_IIR_FILTER_COEFF_MASK                 (0x0F000000u)
#define CY_CAPSENSE_FRC_HW_IIR_FILTER_MASK                      (0x00FFFFFFu)

/* Max number of Low Power sensor historical raw counts to be stored in IP RAM */
#define CY_CAPSENSE_FIFO_SNS_RAW_HISTORY_NUM                    (21uL)
/* Max number of Low Power sensors */
#define CY_CAPSENSE_FIFO_SNS_LP_MAX_NUM                         (8u)
/* Max number of Active sensor configurations to be stored in IP RAM */
#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_RC_HW_IIR_FILTER_EN)
    #define CY_CAPSENSE_FIFO_SNS_MAX_NUM                            (MSCLP_SNS_SRAM_WORD_SIZE / (CY_MSCLP_11_SNS_REGS + 1u))
#else
    #define CY_CAPSENSE_FIFO_SNS_MAX_NUM                            (MSCLP_SNS_SRAM_WORD_SIZE / (CY_MSCLP_6_SNS_REGS + 1u))
#endif/* The wakeup timer maximum value for ACTIVE scan mode in milliseconds */
#define CY_CAPSENSE_MAX_WAKEUP_TIMER_MS                         (2000u)

/* CAPSENSE ILO compensation constants */
#define CY_CAPSENSE_1M_DIVIDER                                  (1000000uL)
#define CY_CAPSENSE_ILO_COMPENSATE_SHIFT                        (14u)

/* The default compensation factor for nominal ILO frequency (40KHz) */
#define CY_CAPSENSE_DEFAULT_ILO_FACTOR                          ((CY_SYSCLK_ILO_FREQ << CY_CAPSENSE_ILO_COMPENSATE_SHIFT) /\
                                                                 CY_CAPSENSE_1M_DIVIDER)

/*******************************************************************************
* HSIOM and PC Macros redefinition platform dependent and for readability
*******************************************************************************/
#define CY_CAPSENSE_HSIOM_SEL_GPIO                          (HSIOM_SEL_GPIO)
#define CY_CAPSENSE_HSIOM_SEL_CSD_SHIELD                    (HSIOM_SEL_CSD_SHIELD)
#define CY_CAPSENSE_HSIOM_SEL_CSD_SENSE                     (HSIOM_SEL_CSD_SENSE)
#define CY_CAPSENSE_HSIOM_SEL_AMUXA                         (HSIOM_SEL_AMUXA)
#define CY_CAPSENSE_HSIOM_SEL_AMUXB                         (HSIOM_SEL_AMUXB)
#define CY_CAPSENSE_DM_GPIO_ANALOG                          (CY_GPIO_DM_ANALOG)
#define CY_CAPSENSE_DM_GPIO_STRONG_IN_OFF                   (CY_GPIO_DM_STRONG_IN_OFF)


#if (CY_CAPSENSE_DISABLE == CY_CAPSENSE_USE_CAPTURE)

/*******************************************************************************
* Constant definition
*******************************************************************************/
/*
 *  Definition of the default configuration of the MSCLP HW registers that is
 *  intended to be used on the MSCLP HW block capturing stage.
 *  The configuration includes:
 *  1. Start of the analog settling process:
 *      - Enables the MSCLP HW block;
 *      - Enables all the sub-blocks of the MSCLP HW block;
 *      - Enables the Sense Modulator output;
 *  2. Clear all of the pending interrupt requests of the MSCLP HW block;
 *  3. Sets into default state the rest of the MSCLP HW block registers which are not related
 *     to actions #1 and #2.
*/

    #define CY_CAPSENSE_MSC_CONFIG_DEFAULT                  \
    {                                                       \
        .ctl                = MSCLP_CTL_SENSE_EN_Msk |      \
                              MSCLP_CTL_MSCCMP_EN_Msk |     \
                              MSCLP_CTL_ENABLED_Msk,        \
        .scanCtl1           = 0x00uL,                       \
        .scanCtl2           = 0x00uL,                       \
        .initCtl1           = 0x00uL,                       \
        .initCtl2           = 0x00uL,                       \
        .initCtl3           = 0x00uL,                       \
        .initCtl4           = 0x00uL,                       \
        .senseDutyCtl       = 0x00uL,                       \
        .sensePeriodCtl     = 0x00uL,                       \
        .filterCtl          = 0x00uL,                       \
        .ccompCdacCtl       = 0x00uL,                       \
        .ditherCdacCtl      = 0x00uL,                       \
        .mscCmpCtl          = 0x00uL,                       \
        .obsCtl             = 0x00uL,                       \
        .aosCtl             = 0x00uL,                       \
        .ceCtl              = 0x00uL,                       \
        .pumpCtl            = 0x00uL,                       \
        .imoCtl             = 0x00uL,                       \
        .intr               = 0x00uL,                       \
        .intrSet            = 0x00uL,                       \
        .intrMask           = 0x00uL,                       \
        .intrLp             = 0x00uL,                       \
        .intrLpSet          = 0x00uL,                       \
        .intrLpMask         = 0x00uL,                       \
        .swSelCdacRe        = 0x00uL,                       \
        .swSelCdacCo        = 0x00uL,                       \
        .swSelCdacCf        = 0x00uL,                       \
        .swSelBgr           = 0x00uL,                       \
        .swSelCswFunc[0u]   = 0x00uL,                       \
        .swSelCswFunc[1u]   = 0x00uL,                       \
        .swSelCswFunc[2u]   = 0x00uL,                       \
        .swSelCswFunc[3u]   = 0x00uL,                       \
        .swSelCswFunc[4u]   = 0x00uL,                       \
        .swSelCswFunc[5u]   = 0x00uL,                       \
        .swSelCswFunc[6u]   = 0x00uL,                       \
        .swSelCswFunc[7u]   = 0x00uL,                       \
        .mode[0u] =                                         \
        {                                                   \
            .senseDutyCtl   = 0x00uL,                       \
            .swSelCdacFl    = 0x00uL,                       \
            .swSelTop       = 0x00uL,                       \
            .swSelComp      = 0x00uL,                       \
            .swSelSh        = 0x00uL,                       \
            .swSelCmod1     = 0x00uL,                       \
            .swSelCmod2     = 0x00uL,                       \
        },                                                  \
        .mode[1u] =                                         \
        {                                                   \
            .senseDutyCtl   = 0x00uL,                       \
            .swSelCdacFl    = 0x00uL,                       \
            .swSelTop       = 0x00uL,                       \
            .swSelComp      = 0x00uL,                       \
            .swSelSh        = 0x00uL,                       \
            .swSelCmod1     = 0x00uL,                       \
            .swSelCmod2     = 0x00uL,                       \
        },                                                  \
        .mode[2u] =                                         \
        {                                                   \
            .senseDutyCtl   = 0x00uL,                       \
            .swSelCdacFl    = 0x00uL,                       \
            .swSelTop       = 0x00uL,                       \
            .swSelComp      = 0x00uL,                       \
            .swSelSh        = 0x00uL,                       \
            .swSelCmod1     = 0x00uL,                       \
            .swSelCmod2     = 0x00uL,                       \
        },                                                  \
        .mode[3u] =                                         \
        {                                                   \
            .senseDutyCtl   = 0x00uL,                       \
            .swSelCdacFl    = 0x00uL,                       \
            .swSelTop       = 0x00uL,                       \
            .swSelComp      = 0x00uL,                       \
            .swSelSh        = 0x00uL,                       \
            .swSelCmod1     = 0x00uL,                       \
            .swSelCmod2     = 0x00uL,                       \
        },                                                  \
    }

    extern const cy_stc_msclp_base_config_t cy_capsense_msclpCfg;
#endif

#define CY_CAPSENSE_CSD_CDAC_COMP_USAGE             ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_COMP_EN))
#define CY_CAPSENSE_CSD_CDAC_COMP_AUTO_USAGE        ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CALIBRATION_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_COMP_EN))
#define CY_CAPSENSE_CSD_CDAC_COMP_DIV_AUTO_USAGE    (CY_CAPSENSE_CSD_CDAC_COMP_USAGE &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CALIBRATION_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_COMP_DIV_AUTO_EN))
#define CY_CAPSENSE_CSD_CDAC_CALIBRATION_USAGE      ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CALIBRATION_EN))
#define CY_CAPSENSE_CSD_CDAC_REF_AUTO_USAGE         (CY_CAPSENSE_CSD_CDAC_CALIBRATION_USAGE &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_REF_AUTO_EN))
#define CY_CAPSENSE_CSD_CDAC_FINE_USAGE             ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_FINE_EN))

#define CY_CAPSENSE_CSX_CDAC_COMP_USAGE             ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CDAC_COMP_EN))
#define CY_CAPSENSE_CSX_CDAC_COMP_AUTO_USAGE        ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CALIBRATION_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CDAC_COMP_EN))
#define CY_CAPSENSE_CSX_CDAC_COMP_DIV_AUTO_USAGE    ((CY_CAPSENSE_CSX_CDAC_COMP_USAGE) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CALIBRATION_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CDAC_COMP_DIV_AUTO_EN))
#define CY_CAPSENSE_CSX_CDAC_CALIBRATION_USAGE      ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CALIBRATION_EN))
#define CY_CAPSENSE_CSX_CDAC_REF_AUTO_USAGE         (CY_CAPSENSE_CSX_CDAC_CALIBRATION_USAGE &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CDAC_REF_AUTO_EN))
#define CY_CAPSENSE_CSX_CDAC_FINE_USAGE             ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CDAC_FINE_EN))

#define CY_CAPSENSE_ISX_CDAC_COMP_USAGE             ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CDAC_COMP_EN))
#define CY_CAPSENSE_ISX_CDAC_COMP_AUTO_USAGE        ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CALIBRATION_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CDAC_COMP_EN))
#define CY_CAPSENSE_ISX_CDAC_COMP_DIV_AUTO_USAGE    ((CY_CAPSENSE_ISX_CDAC_COMP_USAGE) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CALIBRATION_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CDAC_COMP_DIV_AUTO_EN))
#define CY_CAPSENSE_ISX_CDAC_CALIBRATION_USAGE      ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CALIBRATION_EN))
#define CY_CAPSENSE_ISX_CDAC_REF_AUTO_USAGE         (CY_CAPSENSE_ISX_CDAC_CALIBRATION_USAGE &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CDAC_REF_AUTO_EN))
#define CY_CAPSENSE_ISX_CDAC_FINE_USAGE             ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN) &&\
                                                     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CDAC_FINE_EN))

#define CY_CAPSENSE_CDAC_COMP_USAGE                 ((CY_CAPSENSE_CSD_CDAC_COMP_USAGE) ||\
                                                     (CY_CAPSENSE_CSX_CDAC_COMP_USAGE) ||\
                                                     (CY_CAPSENSE_ISX_CDAC_COMP_USAGE))
#define CY_CAPSENSE_CDAC_COMP_AUTO_USAGE            ((CY_CAPSENSE_CSD_CDAC_COMP_AUTO_USAGE) ||\
                                                     (CY_CAPSENSE_CSX_CDAC_COMP_AUTO_USAGE) ||\
                                                     (CY_CAPSENSE_ISX_CDAC_COMP_AUTO_USAGE))
#define CY_CAPSENSE_CDAC_COMP_DIV_AUTO_USAGE        ((CY_CAPSENSE_CSD_CDAC_COMP_DIV_AUTO_USAGE) ||\
                                                     (CY_CAPSENSE_CSX_CDAC_COMP_DIV_AUTO_USAGE) ||\
                                                     (CY_CAPSENSE_ISX_CDAC_COMP_DIV_AUTO_USAGE))
#define CY_CAPSENSE_CDAC_REF_AUTO_USAGE             ((CY_CAPSENSE_CSD_CDAC_REF_AUTO_USAGE) ||\
                                                     (CY_CAPSENSE_CSX_CDAC_REF_AUTO_USAGE) ||\
                                                     (CY_CAPSENSE_ISX_CDAC_REF_AUTO_USAGE))
#define CY_CAPSENSE_CDAC_FINE_USAGE                 ((CY_CAPSENSE_CSD_CDAC_FINE_USAGE) ||\
                                                     (CY_CAPSENSE_CSX_CDAC_FINE_USAGE) ||\
                                                     (CY_CAPSENSE_ISX_CDAC_FINE_USAGE))

#define CY_CAPSENSE_CALIBRATION_EN_POS               (0u)
#define CY_CAPSENSE_CDAC_COMP_USAGE_POS              (1u)
#define CY_CAPSENSE_CDAC_COMP_DIV_AUTO_USAGE_POS     (2u)
#define CY_CAPSENSE_CDAC_REF_AUTO_USAGE_POS          (3u)
#define CY_CAPSENSE_CDAC_CDAC_FINE_USAGE_POS         (4u)

#define CY_CAPSENSE_CALIBRATION_EN_MSK               (CY_CAPSENSE_ENABLE << CY_CAPSENSE_CALIBRATION_EN_POS)
#define CY_CAPSENSE_CDAC_COMP_USAGE_MSK              (CY_CAPSENSE_ENABLE << CY_CAPSENSE_CDAC_COMP_USAGE_POS)
#define CY_CAPSENSE_CDAC_COMP_DIV_AUTO_USAGE_MSK     (CY_CAPSENSE_ENABLE << CY_CAPSENSE_CDAC_COMP_DIV_AUTO_USAGE_POS)
#define CY_CAPSENSE_CDAC_REF_AUTO_USAGE_MSK          (CY_CAPSENSE_ENABLE << CY_CAPSENSE_CDAC_REF_AUTO_USAGE_POS)
#define CY_CAPSENSE_CDAC_CDAC_FINE_USAGE_MSK         (CY_CAPSENSE_ENABLE << CY_CAPSENSE_CDAC_CDAC_FINE_USAGE_POS)

#define CY_CAPSENSE_CDAC_REF_MODE_MASK               (0x3u)
#define CY_CAPSENSE_CDAC_REF_MODE_POS                (0u)
#define CY_CAPSENSE_CDAC_FINE_MODE_MASK              (0xCu)
#define CY_CAPSENSE_CDAC_FINE_MODE_POS               (2u)
#define CY_CAPSENSE_CDAC_COMP_MODE_MASK              (0x30u)
#define CY_CAPSENSE_CDAC_COMP_MODE_POS               (4u)
#define CY_CAPSENSE_CDAC_COMP_DIV_MODE_MASK          (0xC0u)
#define CY_CAPSENSE_CDAC_COMP_DIV_MODE_POS           (6u)
#define CY_CAPSENSE_CDAC_BOOST_VAL_MASK              (0x700u)
#define CY_CAPSENSE_CDAC_BOOST_VAL_POS               (8u)

#define CY_CAPSENSE_CDAC_MODE_DISABLED               (0x0u)
#define CY_CAPSENSE_CDAC_MODE_MANUAL                 (0x1u)
#define CY_CAPSENSE_CDAC_MODE_AUTO                   (0x2u)

#define CY_CAPSENSE_CDAC_REF_MODE_MANUAL_MASK        (CY_CAPSENSE_CDAC_MODE_MANUAL << CY_CAPSENSE_CDAC_REF_MODE_POS)
#define CY_CAPSENSE_CDAC_REF_MODE_AUTO_MASK          (CY_CAPSENSE_CDAC_MODE_AUTO << CY_CAPSENSE_CDAC_REF_MODE_POS)
#define CY_CAPSENSE_CDAC_FINE_MODE_MANUAL_MASK       (CY_CAPSENSE_CDAC_MODE_MANUAL << CY_CAPSENSE_CDAC_FINE_MODE_POS)
#define CY_CAPSENSE_CDAC_FINE_MODE_AUTO_MASK         (CY_CAPSENSE_CDAC_MODE_AUTO << CY_CAPSENSE_CDAC_FINE_MODE_POS)
#define CY_CAPSENSE_CDAC_COMP_MODE_MANUAL_MASK       (CY_CAPSENSE_CDAC_MODE_MANUAL << CY_CAPSENSE_CDAC_COMP_MODE_POS)
#define CY_CAPSENSE_CDAC_COMP_MODE_AUTO_MASK         (CY_CAPSENSE_CDAC_MODE_AUTO << CY_CAPSENSE_CDAC_COMP_MODE_POS)
#define CY_CAPSENSE_CDAC_COMP_DIV_MODE_AUTO_MASK     (CY_CAPSENSE_CDAC_MODE_AUTO << CY_CAPSENSE_CDAC_COMP_DIV_MODE_POS)

#if CY_CAPSENSE_CSD_CDAC_CALIBRATION_USAGE
    #define CY_CAPSENSE_CSD_CDAC_CALIBRATION_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_CSD_CDAC_CALIBRATION_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#if CY_CAPSENSE_CSD_CDAC_COMP_USAGE
    #define CY_CAPSENSE_CSD_CDAC_COMP_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_CSD_CDAC_COMP_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#if CY_CAPSENSE_CSD_CDAC_COMP_DIV_AUTO_USAGE
    #define CY_CAPSENSE_CSD_CDAC_COMP_DIV_AUTO_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_CSD_CDAC_COMP_DIV_AUTO_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#if CY_CAPSENSE_CSD_CDAC_REF_AUTO_USAGE
    #define CY_CAPSENSE_CSD_CDAC_REF_AUTO_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_CSD_CDAC_REF_AUTO_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#if CY_CAPSENSE_CSD_CDAC_FINE_USAGE
    #define CY_CAPSENSE_CSD_CDAC_FINE_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_CSD_CDAC_FINE_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#define CY_CAPSENSE_CSD_CALIBRATION_EN_MSK           (CY_CAPSENSE_CSD_CDAC_CALIBRATION_USAGE_EN    << CY_CAPSENSE_CALIBRATION_EN_POS)
#define CY_CAPSENSE_CSD_CDAC_COMP_USAGE_MSK          (CY_CAPSENSE_CSD_CDAC_COMP_USAGE_EN           << CY_CAPSENSE_CDAC_COMP_USAGE_POS)
#define CY_CAPSENSE_CSD_CDAC_COMP_DIV_AUTO_USAGE_MSK (CY_CAPSENSE_CSD_CDAC_COMP_DIV_AUTO_USAGE_EN  << CY_CAPSENSE_CDAC_COMP_DIV_AUTO_USAGE_POS)
#define CY_CAPSENSE_CSD_CDAC_REF_AUTO_USAGE_MSK      (CY_CAPSENSE_CSD_CDAC_REF_AUTO_USAGE_EN       << CY_CAPSENSE_CDAC_REF_AUTO_USAGE_POS)
#define CY_CAPSENSE_CSD_CDAC_CDAC_FINE_USAGE_MSK     (CY_CAPSENSE_CSD_CDAC_FINE_USAGE_EN           << CY_CAPSENSE_CDAC_CDAC_FINE_USAGE_POS)

#define CY_CAPSENSE_CSD_CALIBRATION_MODE_MSK         ((CY_CAPSENSE_CSD_CALIBRATION_EN_MSK)           |\
                                                      (CY_CAPSENSE_CSD_CDAC_COMP_USAGE_MSK)          |\
                                                      (CY_CAPSENSE_CSD_CDAC_COMP_DIV_AUTO_USAGE_MSK) |\
                                                      (CY_CAPSENSE_CSD_CDAC_REF_AUTO_USAGE_MSK)      |\
                                                      (CY_CAPSENSE_CSD_CDAC_CDAC_FINE_USAGE_MSK))

#if CY_CAPSENSE_CSX_CDAC_CALIBRATION_USAGE
    #define CY_CAPSENSE_CSX_CDAC_CALIBRATION_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_CSX_CDAC_CALIBRATION_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#if CY_CAPSENSE_CSX_CDAC_COMP_USAGE
    #define CY_CAPSENSE_CSX_CDAC_COMP_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_CSX_CDAC_COMP_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#if CY_CAPSENSE_CSX_CDAC_COMP_DIV_AUTO_USAGE
    #define CY_CAPSENSE_CSX_CDAC_COMP_DIV_AUTO_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_CSX_CDAC_COMP_DIV_AUTO_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#if CY_CAPSENSE_CSX_CDAC_REF_AUTO_USAGE
    #define CY_CAPSENSE_CSX_CDAC_REF_AUTO_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_CSX_CDAC_REF_AUTO_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#if CY_CAPSENSE_CSX_CDAC_FINE_USAGE
    #define CY_CAPSENSE_CSX_CDAC_FINE_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_CSX_CDAC_FINE_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#define CY_CAPSENSE_CSX_CALIBRATION_EN_MSK           (CY_CAPSENSE_CSX_CDAC_CALIBRATION_USAGE_EN    << CY_CAPSENSE_CALIBRATION_EN_POS)
#define CY_CAPSENSE_CSX_CDAC_COMP_USAGE_MSK          (CY_CAPSENSE_CSX_CDAC_COMP_USAGE_EN           << CY_CAPSENSE_CDAC_COMP_USAGE_POS)
#define CY_CAPSENSE_CSX_CDAC_COMP_DIV_AUTO_USAGE_MSK (CY_CAPSENSE_CSX_CDAC_COMP_DIV_AUTO_USAGE_EN  << CY_CAPSENSE_CDAC_COMP_DIV_AUTO_USAGE_POS)
#define CY_CAPSENSE_CSX_CDAC_REF_AUTO_USAGE_MSK      (CY_CAPSENSE_CSX_CDAC_REF_AUTO_USAGE_EN       << CY_CAPSENSE_CDAC_REF_AUTO_USAGE_POS)
#define CY_CAPSENSE_CSX_CDAC_CDAC_FINE_USAGE_MSK     (CY_CAPSENSE_CSX_CDAC_FINE_USAGE_EN           << CY_CAPSENSE_CDAC_CDAC_FINE_USAGE_POS)

#define CY_CAPSENSE_CSX_CALIBRATION_MODE_MSK          ((CY_CAPSENSE_CSX_CALIBRATION_EN_MSK)           |\
                                                       (CY_CAPSENSE_CSX_CDAC_COMP_USAGE_MSK)          |\
                                                       (CY_CAPSENSE_CSX_CDAC_COMP_DIV_AUTO_USAGE_MSK) |\
                                                       (CY_CAPSENSE_CSX_CDAC_REF_AUTO_USAGE_MSK)      |\
                                                       (CY_CAPSENSE_CSX_CDAC_CDAC_FINE_USAGE_MSK))

#if CY_CAPSENSE_ISX_CDAC_CALIBRATION_USAGE
    #define CY_CAPSENSE_ISX_CDAC_CALIBRATION_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_ISX_CDAC_CALIBRATION_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#if CY_CAPSENSE_ISX_CDAC_COMP_USAGE
    #define CY_CAPSENSE_ISX_CDAC_COMP_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_ISX_CDAC_COMP_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#if CY_CAPSENSE_ISX_CDAC_COMP_DIV_AUTO_USAGE
    #define CY_CAPSENSE_ISX_CDAC_COMP_DIV_AUTO_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_ISX_CDAC_COMP_DIV_AUTO_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#if CY_CAPSENSE_ISX_CDAC_REF_AUTO_USAGE
    #define CY_CAPSENSE_ISX_CDAC_REF_AUTO_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_ISX_CDAC_REF_AUTO_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#if CY_CAPSENSE_ISX_CDAC_FINE_USAGE
    #define CY_CAPSENSE_ISX_CDAC_FINE_USAGE_EN (CY_CAPSENSE_ENABLE)
#else
    #define CY_CAPSENSE_ISX_CDAC_FINE_USAGE_EN (CY_CAPSENSE_DISABLE)
#endif

#define CY_CAPSENSE_ISX_CALIBRATION_EN_MSK           (CY_CAPSENSE_ISX_CDAC_CALIBRATION_USAGE_EN    << CY_CAPSENSE_CALIBRATION_EN_POS)
#define CY_CAPSENSE_ISX_CDAC_COMP_USAGE_MSK          (CY_CAPSENSE_ISX_CDAC_COMP_USAGE_EN           << CY_CAPSENSE_CDAC_COMP_USAGE_POS)
#define CY_CAPSENSE_ISX_CDAC_COMP_DIV_AUTO_USAGE_MSK (CY_CAPSENSE_ISX_CDAC_COMP_DIV_AUTO_USAGE_EN  << CY_CAPSENSE_CDAC_COMP_DIV_AUTO_USAGE_POS)
#define CY_CAPSENSE_ISX_CDAC_REF_AUTO_USAGE_MSK      (CY_CAPSENSE_ISX_CDAC_REF_AUTO_USAGE_EN       << CY_CAPSENSE_CDAC_REF_AUTO_USAGE_POS)
#define CY_CAPSENSE_ISX_CDAC_CDAC_FINE_USAGE_MSK     (CY_CAPSENSE_ISX_CDAC_FINE_USAGE_EN           << CY_CAPSENSE_CDAC_CDAC_FINE_USAGE_POS)

#define CY_CAPSENSE_ISX_CALIBRATION_MODE_MSK          ((CY_CAPSENSE_ISX_CALIBRATION_EN_MSK)           |\
                                                       (CY_CAPSENSE_ISX_CDAC_COMP_USAGE_MSK)          |\
                                                       (CY_CAPSENSE_ISX_CDAC_COMP_DIV_AUTO_USAGE_MSK) |\
                                                       (CY_CAPSENSE_ISX_CDAC_REF_AUTO_USAGE_MSK)      |\
                                                       (CY_CAPSENSE_ISX_CDAC_CDAC_FINE_USAGE_MSK))

#define CY_CAPSENSE_CPU_CLK_MHZ                     (CY_CAPSENSE_CPU_CLK / CY_CAPSENSE_CONVERSION_MEGA)

/* Used for the Cy_CapSense_ExecuteSaturatedScan() function to obtain the MAX raw count. */
#define CY_CAPSENSE_SATURATED_MAX_COUNT             (0u)
/* Used for the Cy_CapSense_ExecuteSaturatedScan() function to obtain the scan duration. */
#define CY_CAPSENSE_SATURATED_SCAN_TIME             (1u)


#if defined(__cplusplus)
}
#endif

#endif /* CY_IP_M0S8MSCV3LP */

#endif /* CY_CAPSENSE_SENSING_LP_H */


/* [] END OF FILE */
