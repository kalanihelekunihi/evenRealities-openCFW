/***************************************************************************//**
* \file cy_capsense_sensing_lp.c
* \version 6.10.0
*
* \brief
* This file contains the source of functions common for different scanning
* modes.
*
********************************************************************************
* \copyright
* Copyright 2020-2025, Cypress Semiconductor Corporation (an Infineon company)
* or an affiliate of Cypress Semiconductor Corporation. All rights reserved.
* You may use this file only in accordance with the license, terms, conditions,
* disclaimers, and limitations in the end user license agreement accompanying
* the software package with which this file was provided.
*******************************************************************************/


#include <stddef.h>
#include <string.h>
#include "cy_syslib.h"
#include "cy_sysclk.h"
#include "cy_gpio.h"
#include "cy_device_headers.h"
#include "cycfg_capsense.h"
#include "cycfg_capsense_defines.h"
#include "cycfg_peripherals.h"
#include "cy_capsense_common.h"
#include "cy_capsense_sensing.h"
#include "cy_capsense_sensing_lp.h"
#include "cy_capsense_generator_lp.h"
#include "cy_capsense_structure.h"
#include "cy_capsense_processing.h"
#include "cy_capsense_lib.h"
#include "cy_capsense_selftest.h"
#if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
    #include "cy_msclp.h"
#endif

#if (defined(CY_IP_M0S8MSCV3LP))

/*******************************************************************************
* Local definition
*******************************************************************************/
#define CY_CAPSENSE_CSD_CCOMP_CALC_DIV                  (4u * CY_CAPSENSE_PERCENTAGE_100)
#define CY_CAPSENSE_CSX_CCOMP_CALC_DIV                  (8u * CY_CAPSENSE_PERCENTAGE_100)

#define CY_CAPSENSE_EXT_FRAME_START_MODE_SCAN           (1u)
#define CY_CAPSENSE_EXT_FRAME_START_MODE_LP_SCAN        (2u)

#define CY_CAPSENSE_CTL_OPERATING_MODE_CPU              (0u)
#define CY_CAPSENSE_CTL_OPERATING_MODE_AS_MS            (2u)
#define CY_CAPSENSE_CTL_OPERATING_MODE_LP_AOS           (3u)

#define CY_CAPSENSE_SCAN_ST_BSLN_RESET_MSK              (0x01u)
#define CY_CAPSENSE_SCAN_ST_BSLN_VALID_MSK              (0x02u)

/* Offset in words to the first counted SNS registers */
#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_RC_HW_IIR_FILTER_EN)
    #define CY_CAPSENSE_CTL_CFG_OFFSET_VAL              (0u)
#else
    #define CY_CAPSENSE_CTL_CFG_OFFSET_VAL              (8u)
#endif

#define CY_CAPSENSE_CTL_SNS_CTL_OFFSET_VAL              (CY_MSCLP_6_SNS_REGS - 1u)
#define CY_CAPSENSE_CTL_LP_SNS_CTL_OFFSET_VAL           (CY_MSCLP_11_SNS_REGS - 1u)
#define CY_CAPSENSE_LP_AOS_SNS_CFG_REGS_NUM             (5u)

/* CIC2 Filter Divider */
#define CY_CAPSENSE_CIC2_DIVIDER_MAX                    (256u)
/* CIC2 Filter Shift */
#define CY_CAPSENSE_CIC2_SHIFT_MAX                      (15u)

/* CIC2 Accumulator parameters */
#define CY_CAPSENSE_CIC2_ACC_BIT_NUM                    (24u)
#define CY_CAPSENSE_CIC2_ACC_MAX_VAL                    ((1uL << CY_CAPSENSE_CIC2_ACC_BIT_NUM) - 1u)

#define CY_CAPSENSE_AUTOTUNE_SIGPFC_PERCENTAGE          (75u)

/* CAPSENSE ILO compensation constants */
#define CY_CAPSENSE_ILO_FACTOR_SHIFT                    (24u)
#define CY_CAPSENSE_ILO_COMPENSATE_DELAY                (500u)

/* The minimum allowed value of CDAC compensation divider */
#define CY_CAPSENSE_CDAC_COMP_DIV_MIN_MSCLP             (3u)

#define CY_CAPSENSE_ROW_SNS_CALIBRATION                 (0u)
#define CY_CAPSENSE_COL_SNS_CALIBRATION                 (1u)

/* 
* Raw count value equals to appropriate sensor capacitance with dithering configuration. 
* Calculated according to the equation:
* rawCount = (snsCap * CY_CAPSENSE_CONVERSION_HECTO) / CY_CAPSENSE_REF_CDAC_LSB_X100;
*/
#define CY_CAPSENSE_DITHERING_SNS_CAP_300_FEMTO_RAW     (33u)
#define CY_CAPSENSE_DITHERING_SNS_CAP_500_FEMTO_RAW     (56u)
#define CY_CAPSENSE_DITHERING_SNS_CAP_1000_FEMTO_RAW    (112u)
#define CY_CAPSENSE_DITHERING_SNS_CAP_3000_FEMTO_RAW    (338u)
#define CY_CAPSENSE_DITHERING_SNS_CAP_5000_FEMTO_RAW    (564u)
#define CY_CAPSENSE_DITHERING_SNS_CAP_10000_FEMTO_RAW   (1128u)

/* CDAC dithering modes */
#define CY_CAPSENSE_CDAC_DITHERING_MODE_DISABLE         (0x0u)
#define CY_CAPSENSE_CDAC_DITHERING_MODE_MANUAL          (0x1u)
#define CY_CAPSENSE_CDAC_DITHERING_MODE_AUTO            (0x2u)

#define CY_CAPSENSE_CDAC_DITHERING_CDAC_REF             (100u)
#define CY_CAPSENSE_CDAC_DITHERING_NUM_SUBCONV          (100u)
#define CY_CAPSENSE_CDAC_DITHERING_COMP_DIV             (256u)
#define CY_CAPSENSE_CDAC_DITHERING_KREF                 (256u)
#define CY_CAPSENSE_CDAC_DITHERING_CLOCK_REF_RATE       (0x1u)

/* LLS foam rejection duty cycle configuration */
#define CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_WIDTH_SEL_FOAM      (0x1uL)
#define CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_CYCLES_FOAM   (0x1uL) 

/*
* Watchdog time in us for CDAC auto-dithering scan is calculated according to the equation:
* WdtTime = (fineInit + Nsub + KrefDelay) * Kref * 3 / modClockFreqMhz.
* The calculated value is the duration of one sample with the three-time margin.
*/
#define CY_CAPSENSE_CDAC_DITHERING_WATCHDOG_TIME        (((CY_CAPSENSE_NUM_FINE_INIT_CYCLES + \
                                                           CY_CAPSENSE_CDAC_DITHERING_NUM_SUBCONV + \
                                                           CY_CAPSENSE_NUM_EPI_KREF_DELAY) * \
                                                           CY_CAPSENSE_CDAC_DITHERING_KREF * 3u) / \
                                                           CY_CAPSENSE_MOD_CLOCK_MHZ)

#define CY_CAPSENSE_AOS_CTL_FR_TIMEOUT_INTERVAL_MAX_VALUE (MSCLP_AOS_CTL_FR_TIMEOUT_INTERVAL_Msk >> MSCLP_AOS_CTL_FR_TIMEOUT_INTERVAL_Pos)

/*******************************************************************************
* Constants
*******************************************************************************/
#if (CY_CAPSENSE_DISABLE == CY_CAPSENSE_USE_CAPTURE)
    const cy_stc_msclp_base_config_t cy_capsense_msclpCfg = CY_CAPSENSE_MSC_CONFIG_DEFAULT;
#endif

/******************************************************************************/
/** \cond SECTION_CAPSENSE_INTERNAL */
/** \addtogroup group_capsense_internal *//** \{ */
/******************************************************************************/
#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
cy_capsense_status_t Cy_CapSense_MixedSensorsCheck(
                uint32_t startSlotId,
                uint32_t numberSlots,
                uint32_t * ptrHwCfg,
                cy_stc_capsense_context_t * context);
#endif

cy_capsense_status_t Cy_CapSense_SlotPinStateInternal(
                uint32_t * ptrSnsFrm,
                const cy_stc_capsense_electrode_config_t * ptrEltdCfg,
                uint32_t pinState,
                cy_stc_capsense_context_t * context);

uint32_t Cy_CapSense_GetLfsrBitsAuto(
                const cy_stc_capsense_widget_config_t * ptrWdConfig,
                const cy_stc_capsense_context_t * context);

uint32_t Cy_CapSense_GetClkSrcSSCAuto(
                const cy_stc_capsense_widget_config_t * ptrWdConfig,
                const cy_stc_capsense_context_t * context);

uint32_t Cy_CapSense_GetClkSrcPRSAuto(
                const cy_stc_capsense_widget_context_t * ptrWdContext,
                const cy_stc_capsense_context_t * context);

uint32_t Cy_CapSense_GetLfsrBitsNumber(
                uint32_t snsClkDivider,
                uint32_t snsClkDividerMin,
                uint32_t ditherLimitPercents,
                uint32_t lfsrScale);

uint32_t Cy_CapSense_RunSSCAuto(
                uint32_t autoSelMode,
                uint32_t lfsrDitherCycles,
                uint32_t ditherLimitCycles,
                uint32_t lfsrPolySize,
                uint32_t subConvNumber);

uint32_t Cy_CapSense_GetPolySize(uint32_t lfsrPoly);

#if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CALIBRATION_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CALIBRATION_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CALIBRATION_EN))
cy_capsense_status_t Cy_CapSense_ScanSlotInternalCPU(
                uint32_t startSlotId,
                uint32_t numberSlots,
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_ScanWidgetInternalCPU(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context);
uint32_t Cy_CapSense_MinRawSearch(
                uint32_t widgetId,
                uint32_t rowFlag,
                cy_stc_capsense_context_t * context);
#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
uint32_t Cy_CapSense_MaxRawSearch(
                uint32_t widgetId,
                uint32_t rowFlag,
                cy_stc_capsense_context_t * context);
#endif
uint32_t Cy_CapSense_CalculateAbsDiff(
                uint32_t a,
                uint32_t b);
void Cy_CapSense_SetWidgetFrameRefCdacCodes(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context);
void Cy_CapSense_SetWidgetFrameCompCdacCode(
                uint32_t widgetId,
                uint32_t mode,
                cy_stc_capsense_context_t * context);
void Cy_CapSense_SetCompDivider(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_CdacSuccessAppr(
                uint32_t widgetId,
                uint32_t rowFlag,
                uint8_t calibrMask,
                uint8_t * cdacPtr,
                cy_stc_capsense_context_t * context);
uint32_t Cy_CapSense_CalculateRawTarget(
                uint32_t widgetId,
                uint32_t rowFlag,
                cy_stc_capsense_context_t * context);
#endif

void Cy_CapSense_TransferRawCounts(
                uint32_t startSlotId,
                uint32_t numberSlots,
                cy_stc_capsense_context_t * context);

#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
void Cy_CapSense_TransferLpRawCounts(
                uint32_t startSlotId,
                uint32_t numberSlots,
                cy_stc_capsense_context_t * context);
#endif

cy_capsense_status_t Cy_CapSense_WaitMrssStatusChange(
                uint32_t timeout,
                uint32_t mrssStatus,
                cy_stc_capsense_context_t * context);

uint32_t Cy_CapSense_MsclpTimerCalcCycles(
                uint32_t wakeupTimer,
                cy_stc_capsense_context_t * context);

#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_AUTO_DITHER_EN)
static cy_capsense_status_t Cy_CapSense_CdacDitherScaleCalc(
                cy_stc_capsense_context_t * context);
static cy_capsense_status_t Cy_CapSense_ConfigureAutoDitherMode(
                cy_stc_capsense_context_t * context);
static cy_capsense_status_t Cy_CapSense_CdacDitherGetMaxRaw(
                uint32_t * ptrSnsFrame,
                const cy_stc_capsense_widget_config_t * ptrWdCfg,
                uint32_t snsFrameSize,
                uint32_t * ptrRawCountMax,
                cy_stc_capsense_context_t * context);
#endif
#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LIQUID_LEVEL_FOAM_REJECTION_EN)
static cy_capsense_status_t Cy_CapSense_ShortIntegration(
                uint32_t startSlotId,
                uint32_t numberSlots,
                cy_stc_capsense_context_t * context);
#endif

/** \} \endcond */


/*******************************************************************************
* Function Name: Cy_CapSense_ScanSlotsInternal
****************************************************************************//**
*
* Transfers sensor frame to Sensor Data RAM and initiates the non-blocking scan
* of specified slots. If the specified slots configuration does not fit into the
* HW SNS RAM then only the CY_CAPSENSE_FIFO_SNS_MAX_NUM number of sensors will
* be scanned. The remaining sensors will be scanned in the next sub-frame(s).
*
* This is an internal function. Do not call this function directly from
* the application program.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param startSlotId
* The slot ID scan will be started from.
*
* \param numberSlots
* The number of slots will be scanned.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_ScanSlotsInternal(
                uint32_t startSlotId,
                uint32_t numberSlots,
                cy_stc_capsense_context_t * context)
{
    uint32_t index;
    uint32_t * ptrSensorFrame;
    __IOM uint32_t * ptrSensorData;
    MSCLP_Type * ptrHwBase = context->ptrCommonConfig->ptrChConfig->ptrHwBase;
    uint32_t numberSlotsLocal = (CY_CAPSENSE_FIFO_SNS_MAX_NUM > numberSlots) ? numberSlots : CY_CAPSENSE_FIFO_SNS_MAX_NUM;
    context->ptrInternalContext->numSlots = (uint16_t)numberSlotsLocal;

    if (0u != numberSlotsLocal)
    {
        /* Initialize frame data pointer */
        ptrSensorFrame = &context->ptrSensorFrameContext[startSlotId * CY_CAPSENSE_SENSOR_FRAME_SIZE];

        /* Initialize sensor data pointer */
        ptrSensorData = &ptrHwBase->SNS.SENSOR_DATA[0u];

        /* Disable HW IP to allow MRSS operations */
        ptrHwBase->CTL &= (~MSCLP_CTL_ENABLED_Msk);

        /* Disable PUMP to save power during the Sensor Data copy */
        #if (CY_MSCLP_VDDA_PUMP_TRESHOLD > CY_CAPSENSE_VDDA_MV)
            ptrHwBase->PUMP_CTL = 0u;
        #endif

        /* Check if IMO is running */
        if (0u == (ptrHwBase->MRSS_STATUS & MSCLP_MRSS_STATUS_IMO_UP_Msk))
        {
            /* Enable MRSS to provide access to the SNS_STC registers */
            ptrHwBase->MRSS_CMD = MSCLP_MRSS_CMD_MRSS_START_Msk;
            (void)Cy_CapSense_WaitMrssStatusChange(CY_MSCLP_CLK_LF_PERIOD_MAX * CY_MSCLP_MRSS_TIMEOUT_FULL,
                                                    CY_CAPSENSE_MRSS_IMO_TURN_ON, context);
        }
        else
        {
            ptrHwBase->MRSS_CMD = MSCLP_MRSS_CMD_MRSS_PUMP_STOP_Msk;
        }

        /* Copy sensor frame to Sensor Data RAM */
        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_RC_HW_IIR_FILTER_EN)
            for (index = 0u; index < numberSlotsLocal; index++)
            {
                /* Set raw count filter coefficient */
                ptrSensorData[CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL0] = (ptrSensorFrame[CY_CAPSENSE_SNS_HW_IIR_INDEX] &
                                                    CY_CAPSENSE_RC_HW_IIR_FILTER_COEFF_MASK) >> CY_CAPSENSE_RC_HW_IIR_FILTER_COEFF_POS;
                ptrSensorData[CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL1] = 0u;
                ptrSensorData[CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL2] = 0u;
                /* Set filtered raw count scaled */
                ptrSensorData[CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL3] = ptrSensorFrame[CY_CAPSENSE_SNS_HW_IIR_INDEX] & CY_CAPSENSE_FRC_HW_IIR_FILTER_MASK;
                ptrSensorData[CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL4] = 0u;
                /* Copy sensor frame to SEL and CTL registers */
                ptrSensorData[CY_CAPSENSE_FRM_LP_SNS_SW_SEL_CSW_LO_MASK2_INDEX] = ptrSensorFrame[CY_CAPSENSE_SNS_SW_SEL_CSW_LO_MASK2_INDEX];
                ptrSensorData[CY_CAPSENSE_FRM_LP_SNS_SW_SEL_CSW_LO_MASK1_INDEX] = ptrSensorFrame[CY_CAPSENSE_SNS_SW_SEL_CSW_LO_MASK1_INDEX];
                ptrSensorData[CY_CAPSENSE_FRM_LP_SNS_SW_SEL_CSW_LO_MASK0_INDEX] = ptrSensorFrame[CY_CAPSENSE_SNS_SW_SEL_CSW_LO_MASK0_INDEX];
                ptrSensorData[CY_CAPSENSE_FRM_LP_SNS_SCAN_CTL_INDEX] = ptrSensorFrame[CY_CAPSENSE_SNS_SCAN_CTL_INDEX];
                ptrSensorData[CY_CAPSENSE_FRM_LP_SNS_CDAC_CTL_INDEX] = ptrSensorFrame[CY_CAPSENSE_SNS_CDAC_CTL_INDEX];
                ptrSensorData[CY_CAPSENSE_FRM_LP_SNS_CTL_INDEX] = ptrSensorFrame[CY_CAPSENSE_SNS_CTL_INDEX];
                ptrSensorFrame += CY_CAPSENSE_SENSOR_FRAME_SIZE;
                ptrSensorData += CY_CAPSENSE_LP_SENSOR_FRAME_SIZE;
            }
        #else
            for (index = 0u; index < (numberSlotsLocal * CY_CAPSENSE_SENSOR_FRAME_SIZE); index++)
            {
                *ptrSensorData = *ptrSensorFrame;
                ptrSensorData++;
                ptrSensorFrame++;
            }
        #endif

        ptrSensorData--;
        /* Configure the last slot */
        *ptrSensorData |= MSCLP_SNS_SNS_CTL_LAST_Msk;

        /* Configure Sensor Data RAM start and slot size */
        CY_REG32_CLR_SET(ptrHwBase->SCAN_CTL2, MSCLP_SCAN_CTL2_FRAME_CFG_START_ADDR, 0u);
        CY_REG32_CLR_SET(ptrHwBase->CTL, MSCLP_CTL_CFG_OFFSET, CY_CAPSENSE_CTL_CFG_OFFSET_VAL);

        /* Configure FIFO */
        CY_REG32_CLR_SET(ptrHwBase->SCAN_CTL1, MSCLP_SCAN_CTL1_FRAME_RES_START_ADDR,
                                               MSCLP_SNS_SRAM_WORD_SIZE - numberSlotsLocal);

        if ((NULL != context->ptrInternalContext->ptrSSCallback) &&
            (CY_CAPSENSE_ENABLE == context->ptrInternalContext->firstActSubFrame))
        {
            context->ptrInternalContext->ptrSSCallback(context->ptrActiveScanSns);
        }

        /* Stop MRSS_IMO only for the first sub-frame in LP_AOS mode after the callback as it can operate with SNS registers */
        if ((CY_CAPSENSE_ENABLE == context->ptrInternalContext->firstActSubFrame) &&
            (0u != (ptrHwBase->MRSS_STATUS & MSCLP_MRSS_STATUS_IMO_UP_Msk)))
        {
            /* Stop the MRSS_IMO to save power */
            ptrHwBase->MRSS_CMD = MSCLP_MRSS_CMD_MRSS_STOP_Msk;
        }

        /* Check for the system VDDA value and enable PUMP if VDDA is less than the threshold */
        #if (CY_MSCLP_VDDA_PUMP_TRESHOLD > CY_CAPSENSE_VDDA_MV)
            ptrHwBase->PUMP_CTL = MSCLP_PUMP_CTL_PUMP_MODE_Msk;
        #endif

        /* Check if an external start is enabled */
        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_EXT_FRM_START_EN)
            if (0u == (context->ptrCommonContext->status & CY_CAPSENSE_MW_STATE_INITIALIZATION_MASK))
            {
                /* Set the external start scan mode to start LP_AOS sequencer */
                CY_REG32_CLR_SET(ptrHwBase->CTL, MSCLP_CTL_EXT_FRAME_START_MODE,
                                    CY_CAPSENSE_EXT_FRAME_START_MODE_LP_SCAN);

                /* Enable HW IP to allow a scan frame start */
                ptrHwBase->CTL |= MSCLP_CTL_ENABLED_Msk;
            }
            else
            {
                /* Enable HW IP to allow a scan frame start */
                ptrHwBase->CTL |= MSCLP_CTL_ENABLED_Msk;

                /* Start LP_AOS scan */
                ptrHwBase->WAKEUP_CMD = MSCLP_WAKEUP_CMD_START_FRAME_AOS_Msk;
            }
        #else
            /* Enable HW IP to allow a scan frame start */
            ptrHwBase->CTL |= MSCLP_CTL_ENABLED_Msk;

            /* Start scan */
            ptrHwBase->WAKEUP_CMD = MSCLP_WAKEUP_CMD_START_FRAME_AOS_Msk;
        #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_EXT_FRM_START_EN) */
    }
}


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
/*******************************************************************************
* Function Name: Cy_CapSense_MixedSensorsCheck
****************************************************************************//**
*
* Initiates the check of specified slots. Widgets with enabled MPSC feature
* can't be scanned with the others in one scan.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param startSlotId
* The slot ID scan will be started from.
*
* \param numberSlots
* The number of slots will be scanned.
*
* \param ptrHwCfg
* Pointer to a hardware config variable.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_MIXED_SENSORS    - Sensors with MPSC and w/o can't be scanned in one frame.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_MixedSensorsCheck(uint32_t startSlotId,
                                                   uint32_t numberSlots,
                                                   uint32_t * ptrHwCfg,
                                                   cy_stc_capsense_context_t * context)
{
    uint32_t curSlotIndex, wdIndex, snsIndex;
    const cy_stc_capsense_scan_slot_t * ptrScanSlots;
    const cy_stc_capsense_widget_config_t * ptrWdCfg;
    uint32_t regularWdCnt = 0u;
    uint32_t mpscWdCnt = 0u;
    uint32_t lastSlot = startSlotId + numberSlots - 1u;
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_SUCCESS;

    ptrScanSlots = context->ptrScanSlots;
    curSlotIndex = startSlotId;

    do
    {
        wdIndex  = ptrScanSlots[curSlotIndex].wdId;
        snsIndex = ptrScanSlots[curSlotIndex].snsId;
        ptrWdCfg = &context->ptrWdConfig[wdIndex];

        if ((CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod) &&
           (CY_CAPSENSE_MPSC_MIN_ORDER <= ptrWdCfg->mpOrder))
        {
            mpscWdCnt++;
        }
        else
        {
            regularWdCnt++;
        }

        if ((0u != regularWdCnt) && (0u != mpscWdCnt))
        {
            capStatus = CY_CAPSENSE_STATUS_MIXED_SENSORS;
            break;
        }

        /* Jump to the next widget */
        curSlotIndex += (ptrWdCfg->numSlots - snsIndex);
    } while (curSlotIndex <= lastSlot);

    if ((CY_CAPSENSE_STATUS_SUCCESS == capStatus) && (0u < mpscWdCnt))
    {
        *ptrHwCfg = CY_CAPSENSE_HW_CONFIG_MPSC_SCANNING;
    }

    return capStatus;
}
#endif /* CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED */


/*******************************************************************************
* Function Name: Cy_CapSense_ScanSlots_V3Lp
****************************************************************************//**
*
* Initiates the non-blocking scan of specified slots. 
*
* If the middleware is busy, do not initiate a new scan or set up widgets.
* Use the Cy_CapSense_IsBusy() function to check HW busyness at a particular moment.
* Use the Cy_CapSense_MwState() function to verify if MW executes any firmware 
* tasks related to initialization, scanning, and processing at a particular moment.
* The transition into system DEEP SLEEP mode is allowed after the scan is started.
*
* This function initiates a scan only for the first number of slots that could
* be fit into the Sensor Data RAM and then exits. Scans for the remaining slots
* started in the interrupt service routine (part of middleware), which triggered
* at the end of the scan completion.
*
* If the /ref activeWakeupTimer parameter set by the Cy_CapSense_ConfigureMsclpTimer()
* function is more than 0u, the correspondent time interval will be inserted before
* the frame scan start to provide a desired refresh rate.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param startSlotId
* The slot ID scan will be started from.
*
* \param numberSlots
* The number of slots will be scanned.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - Any of input parameters is invalid.
* - CY_CAPSENSE_STATUS_CONFIG_OVERFLOW  - The numberSlots parameter exceeds
*                                         the maximum number of sensor configurations
*                                         which is possible to be loaded into the
*                                         internal buffer of the CAPSENSE&trade HW block.
* - CY_CAPSENSE_STATUS_HW_BUSY          - The HW is busy with the previous scan.
* - CY_CAPSENSE_STATUS_HW_LOCKED        - The MSCLP HW block is captured by another
*                                         middleware.
* - CY_CAPSENSE_STATUS_TIMEOUT          - A timeout reached during the MRSS start.
* - CY_CAPSENSE_STATUS_MIXED_SENSORS    - Sensors with MPSC and w/o can't be scanned
*                                         in one frame.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ScanSlots_V3Lp(
                uint32_t startSlotId,
                uint32_t numberSlots,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_SUCCESS;
    uint32_t lastSlot;
    cy_stc_capsense_internal_context_t * ptrIntrCxt;
    MSCLP_Type * ptrHwBase;
    uint32_t hwCfg = CY_CAPSENSE_HW_CONFIG_REGULAR_SCANNING;

    if ((NULL == context) || (0u == numberSlots) || (CY_CAPSENSE_SLOT_COUNT <= startSlotId))
    {
        capStatus = CY_CAPSENSE_STATUS_BAD_PARAM;
    }

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_EXT_FRM_START_EN)
        if (CY_CAPSENSE_FIFO_SNS_MAX_NUM < numberSlots)
        {
            capStatus = CY_CAPSENSE_STATUS_CONFIG_OVERFLOW;
        }
    #endif

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
        if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
        {
            capStatus = Cy_CapSense_MixedSensorsCheck(startSlotId, numberSlots, &hwCfg, context);
        }
    #endif

    if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
    {
        lastSlot = startSlotId + numberSlots - 1u;
        if (CY_CAPSENSE_SLOT_COUNT > lastSlot)
        {
            if (CY_CAPSENSE_BUSY == Cy_CapSense_IsBusy(context))
            {
                /* Previous scan is not completed. Return the BUSY status */
                capStatus = CY_CAPSENSE_STATUS_HW_BUSY;
            }
            else
            {
                Cy_CapSense_SetBusyFlags(context);

                /* Set the Active widget scan status */
                ptrIntrCxt = context->ptrInternalContext;
                ptrHwBase = context->ptrCommonConfig->ptrChConfig->ptrHwBase;

                ptrIntrCxt->repeatScanEn = CY_CAPSENSE_DISABLE;

                if (((CY_CAPSENSE_HW_CONFIG_REGULAR_SCANNING == ptrIntrCxt->hwConfigState) ||
                     (CY_CAPSENSE_HW_CONFIG_MPSC_SCANNING == ptrIntrCxt->hwConfigState)) &&
                    (ptrIntrCxt->startSlotIndex == startSlotId) && (ptrIntrCxt->numSlots == numberSlots) &&
                    (CY_CAPSENSE_FIFO_SNS_MAX_NUM >= numberSlots) &&
                    (0u == (context->ptrCommonContext->status & CY_CAPSENSE_MW_STATE_CALIBRATION_MASK)) &&
                    (0u != (context->ptrCommonContext->status & CY_CAPSENSE_MW_STATE_ACTIVE_WD_SCAN_MASK)))
                {
                    ptrIntrCxt->repeatScanEn = CY_CAPSENSE_ENABLE;

                    /* Reset the start slot in the internal context structure */
                    ptrIntrCxt->currentSlotIndex = (uint16_t)startSlotId;

                    if (NULL != context->ptrInternalContext->ptrSSCallback)
                    {
                        context->ptrInternalContext->ptrSSCallback(context->ptrActiveScanSns);
                    }

                    /* Check if the external start is enabled */
                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_EXT_FRM_START_EN)
                        if (0u == (context->ptrCommonContext->status & CY_CAPSENSE_MW_STATE_INITIALIZATION_MASK))
                        {
                            /* Set the External Start scan mode to start the LP_AOS sequencer */
                            CY_REG32_CLR_SET(ptrHwBase->CTL, MSCLP_CTL_EXT_FRAME_START_MODE,
                                             CY_CAPSENSE_EXT_FRAME_START_MODE_LP_SCAN);
                            /* Enable HW IP to allow the scan frame start */
                            ptrHwBase->CTL |= MSCLP_CTL_ENABLED_Msk;
                        }
                        else
                        {
                            /* Enable HW IP to allow the scan frame start */
                            ptrHwBase->CTL |= MSCLP_CTL_ENABLED_Msk;
                            /* Disable the External Start scan mode during initialization and start scans immediately */
                            ptrHwBase->WAKEUP_CMD = MSCLP_WAKEUP_CMD_START_FRAME_AOS_Msk;
                        }
                    #else
                        /* Disable HW block per IFX 005467-513 */
                        ptrHwBase->CTL &= ~MSCLP_CTL_ENABLED_Msk;

                        /* Enable HW IP to allow the scan frame start */
                        ptrHwBase->CTL |= MSCLP_CTL_ENABLED_Msk;

                        /* Start scanning */
                        ptrHwBase->WAKEUP_CMD = MSCLP_WAKEUP_CMD_START_FRAME_AOS_Msk;
                    #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_EXT_FRM_START_EN) */
                }
                else
                {
                    capStatus = Cy_CapSense_SwitchHwConfiguration(hwCfg, context);

                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LIQUID_LEVEL_FOAM_REJECTION_EN)
                        if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
                        {
                            capStatus = Cy_CapSense_ShortIntegration(startSlotId, numberSlots, context);
                        }
                    #endif

                    if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
                    {
                        context->ptrCommonContext->status &= (uint32_t)~((uint32_t)CY_CAPSENSE_MW_STATE_WD_SCAN_MASK);
                        context->ptrCommonContext->status |= CY_CAPSENSE_MW_STATE_ACTIVE_WD_SCAN_MASK;

                        /* Check for the needed MSCv3LP operating mode */
                        ptrIntrCxt->operatingMode = CY_CAPSENSE_CTL_OPERATING_MODE_LP_AOS;
                        CY_REG32_CLR_SET(ptrHwBase->CTL, MSCLP_CTL_OPERATING_MODE,
                                                            CY_CAPSENSE_CTL_OPERATING_MODE_LP_AOS);
                        CY_REG32_CLR_SET(ptrHwBase->CTL, MSCLP_CTL_CFG_OFFSET, 0uL);

                        ptrHwBase->AOS_CTL &= ~MSCLP_AOS_CTL_FR_TIMEOUT_INTERVAL_Msk;
                        ptrHwBase->AOS_CTL |= (uint32_t)(1uL << MSCLP_AOS_CTL_FR_TIMEOUT_INTERVAL_Pos);

                        /* Set the active timer value */
                        context->ptrCommonConfig->ptrChConfig->ptrHwBase->AOS_CTL &= ~MSCLP_AOS_CTL_WAKEUP_TIMER_Msk;
                        context->ptrCommonConfig->ptrChConfig->ptrHwBase->AOS_CTL |=
                            (context->ptrInternalContext->activeWakeupTimerCycles << MSCLP_AOS_CTL_WAKEUP_TIMER_Pos);

                        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_RC_HW_IIR_FILTER_EN)
                            /* Enable HW processing */
                            ptrHwBase->CE_CTL = MSCLP_CE_CTL_ENABLED_Msk | ptrIntrCxt->hwIirInit;
                        #else
                            /* Disable HW processing */
                            ptrHwBase->CE_CTL = 0uL;
                        #endif

                        /* Unmask FRAME interrupt for ACTIVE and ALR modes (AS_MS and LP_AOS HW modes) */
                        ptrHwBase->INTR_LP_MASK = MSCLP_INTR_LP_FRAME_Msk;
                        (void)ptrHwBase->INTR_LP_MASK;

                        /* Initialize internal context */
                        ptrIntrCxt->startSlotIndex = (uint16_t)startSlotId;
                        ptrIntrCxt->currentSlotIndex = (uint16_t)startSlotId;
                        ptrIntrCxt->endSlotIndex = (uint16_t)lastSlot;
                        ptrIntrCxt->firstActSubFrame = CY_CAPSENSE_ENABLE;

                        if (CY_CAPSENSE_FIFO_SNS_MAX_NUM >= numberSlots)
                        {
                            /* Set the repeat scan flag */
                            ptrIntrCxt->repeatScanEn = CY_CAPSENSE_ENABLE;
                        }

                        /* Initialize the scan */
                        Cy_CapSense_ScanSlotsInternal(startSlotId, numberSlots, context);
                    }
                }
            }
        }
        else
        {
            capStatus = CY_CAPSENSE_STATUS_BAD_PARAM;
        }
    }

    return capStatus;
}


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_ScanLpSlots
****************************************************************************//**
*
* Initiates a non-blocking scan for specified low power slots and exits.
* Scanning is initiated only if no scan is in progress.
* Scans initiated by this function can be performed in different system power
* modes such as Active, Sleep or Deep Sleep.
* After all specified number of frames are scanned or if a touch is
* detected during the scan, the interrupt is fired, the CPU switches
* Power mode to Active and the interrupt service routine (part of middleware)
* transfers the last frame raw counts and clears the busy status.
* If the middleware is busy, do not initiate a new scan or set up widgets.
* Use the Cy_CapSense_IsBusy() function to check HW busyness at a particular moment.
* Use the Cy_CapSense_MwState() function to verify if MW executes any firmware 
* tasks related to initialization, scanning, and processing at a particular moment.
* The function clears the CY_CAPSENSE_MW_STATE_LP_ACTIVE_MASK status bit. It is
* set when a touch detection occurs during the low power slot scans and will remain
* set until the next Cy_CapSense_ScanLpSlots() function call.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param startLpSlotId
* The slot ID to start a scan from.
*
* \param numberLpSlots
* The number of slots to be scanned.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation completed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - The input parameter is invalid.
* - CY_CAPSENSE_STATUS_HW_BUSY          - The hardware is busy with the previous scan.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ScanLpSlots(
                uint32_t startLpSlotId,
                uint32_t numberLpSlots,
                cy_stc_capsense_context_t * context)
{
    uint32_t index;
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_BAD_PARAM;
    cy_stc_capsense_internal_context_t * ptrIntrCxt;
    uint32_t * ptrSensorFrameLp;
    MSCLP_Type * ptrHwBase;
    uint32_t lastLpSlot = startLpSlotId + numberLpSlots - 1u;

    if ((NULL != context) && (0u != numberLpSlots) &&
        (CY_CAPSENSE_FIFO_SNS_LP_MAX_NUM >= numberLpSlots) && (CY_CAPSENSE_SLOT_LP_COUNT > lastLpSlot))
    {
        /* Clear the signal detect status for low power scans */
        context->ptrCommonContext->status &= (~((uint32_t)CY_CAPSENSE_MW_STATE_LP_ACTIVE_MASK));
        if (CY_CAPSENSE_BUSY == Cy_CapSense_IsBusy(context))
        {
            /* Previous scan is not completed. Return the BUSY status */
            capStatus = CY_CAPSENSE_STATUS_HW_BUSY;
        }
        else
        {
            capStatus = Cy_CapSense_SwitchHwConfiguration(CY_CAPSENSE_HW_CONFIG_REGULAR_SCANNING, context);
            if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
            {
                Cy_CapSense_SetBusyFlags(context);

                ptrIntrCxt = context->ptrInternalContext;
                ptrHwBase = context->ptrCommonConfig->ptrChConfig->ptrHwBase;

                capStatus = CY_CAPSENSE_STATUS_SUCCESS;

                /* Set the repeat scan flag */
                ptrIntrCxt->repeatScanEn = CY_CAPSENSE_ENABLE;

                if (((startLpSlotId != ptrIntrCxt->currentSlotIndex) || (lastLpSlot != ptrIntrCxt->endSlotIndex)) ||
                    (0u == (context->ptrCommonContext->status & CY_CAPSENSE_MW_STATE_LP_WD_SCAN_MASK)))
                {
                    /* Initialize internal context */
                    ptrIntrCxt->currentSlotIndex = (uint16_t)startLpSlotId;
                    ptrIntrCxt->endSlotIndex = (uint16_t)lastLpSlot;
                    ptrIntrCxt->numSlots = (uint16_t)numberLpSlots;

                    /* Set the LP_AOS operating mode */
                    ptrIntrCxt->operatingMode = CY_CAPSENSE_CTL_OPERATING_MODE_LP_AOS;
                    CY_REG32_CLR_SET(ptrHwBase->CTL, MSCLP_CTL_OPERATING_MODE,
                                                     CY_CAPSENSE_CTL_OPERATING_MODE_LP_AOS);
                    CY_REG32_CLR_SET(ptrHwBase->CTL, MSCLP_CTL_CFG_OFFSET, 0u);

                    /* Enable HW processing */
                    ptrHwBase->CE_CTL = MSCLP_CE_CTL_ENABLED_Msk | MSCLP_CE_CTL_BLSD_EN_Msk;

                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_RC_IIR_FILTER_EN)
                        ptrHwBase->CE_CTL |= MSCLP_CE_CTL_RCF_EN_Msk;
                    #endif

                    /* Disable HW IP to allow MRSS operations */
                    ptrHwBase->CTL &= (~MSCLP_CTL_ENABLED_Msk);

                    /* Check if IMO is running */
                    if (0u == (ptrHwBase->MRSS_STATUS & MSCLP_MRSS_STATUS_IMO_UP_Msk))
                    {
                        /* Enable only REF and IMO to provide access to the SNS_STC registers */
                        #if (CY_MSCLP_VDDA_PUMP_TRESHOLD > CY_CAPSENSE_VDDA_MV)
                            ptrHwBase->PUMP_CTL = 0u;
                        #endif

                        ptrHwBase->MRSS_CMD = MSCLP_MRSS_CMD_MRSS_START_Msk;
                        capStatus = Cy_CapSense_WaitMrssStatusChange(
                                        CY_MSCLP_CLK_LF_PERIOD_MAX * CY_MSCLP_MRSS_TIMEOUT_SMALL,
                                        CY_CAPSENSE_MRSS_IMO_TURN_ON, context);
                    }
                    else
                    {
                        /* Stop the MRSS pump to save power */
                        ptrHwBase->MRSS_CMD = MSCLP_MRSS_CMD_MRSS_PUMP_STOP_Msk;
                    }


                    if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
                    {
                        /* Initialize frame data pointer */
                        ptrSensorFrameLp = &context->ptrSensorFrameLpContext[startLpSlotId * CY_MSCLP_11_SNS_REGS];

                        /* Copy sensor frame to Sensor Data RAM */
                        for (index = 0u; index < (numberLpSlots * CY_MSCLP_11_SNS_REGS); index++)
                        {
                            ptrHwBase->SNS.SENSOR_DATA[index] = ptrSensorFrameLp[index];
                        }

                        /* Configure the last slot */
                        ptrHwBase->SNS.SENSOR_DATA[((numberLpSlots - 1u) * CY_MSCLP_11_SNS_REGS) +
                                                   CY_CAPSENSE_CTL_LP_SNS_CTL_OFFSET_VAL] |= MSCLP_SNS_SNS_CTL_LAST_Msk;

                        /* Initialize channel engine to perform processing */
                        ptrHwBase->SNS.CE_INIT_CTL |= MSCLP_SNS_CE_INIT_CTL_SENSOR_INIT_Msk;

                        /* Check AHB2AHB bus response */
                        if ((ptrHwBase->SNS.BRIDGE_STATUS & MSCLP_SNS_BRIDGE_STATUS_READY_Msk) == 0u)
                        {
                            capStatus = CY_CAPSENSE_STATUS_TIMEOUT;
                        }

                        if (0u != (ptrHwBase->MRSS_STATUS & MSCLP_MRSS_STATUS_IMO_UP_Msk))
                        {
                            /* Stop the MRSS to save power */
                            ptrHwBase->MRSS_CMD = MSCLP_MRSS_CMD_MRSS_STOP_Msk;
                        }
                    }

                    if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
                    {
                        /* Configure Sensor Data RAM start and slot size */
                        CY_REG32_CLR_SET(ptrHwBase->SCAN_CTL2, MSCLP_SCAN_CTL2_FRAME_CFG_START_ADDR, 0u);
                        CY_REG32_CLR_SET(ptrHwBase->CTL, MSCLP_CTL_CFG_OFFSET, 0u);

                        /* Set AOS_CTL register with enabled MRSS power cycle */
                        ptrHwBase->AOS_CTL &= (uint32_t)~MSCLP_AOS_CTL_FR_TIMEOUT_INTERVAL_Msk;

                        /* Limit wotTimeout value to maximum if it exceeds range */
                        if (CY_CAPSENSE_AOS_CTL_FR_TIMEOUT_INTERVAL_MAX_VALUE < (uint32_t)context->ptrInternalContext->wotTimeout)
                        {
                            context->ptrInternalContext->wotTimeout = (uint16_t)CY_CAPSENSE_AOS_CTL_FR_TIMEOUT_INTERVAL_MAX_VALUE;
                        }
                        ptrHwBase->AOS_CTL |= (uint32_t)((uint32_t)context->ptrInternalContext->wotTimeout << MSCLP_AOS_CTL_FR_TIMEOUT_INTERVAL_Pos);
                        ptrHwBase->AOS_CTL |= MSCLP_AOS_CTL_MRSS_PWR_CYCLE_EN_Msk;

                        /* Set the WOT timer value */
                        context->ptrCommonConfig->ptrChConfig->ptrHwBase->AOS_CTL &= ~MSCLP_AOS_CTL_WAKEUP_TIMER_Msk;
                        context->ptrCommonConfig->ptrChConfig->ptrHwBase->AOS_CTL |=
                            (context->ptrInternalContext->wotScanIntervalCycles << MSCLP_AOS_CTL_WAKEUP_TIMER_Pos);

                        /* Check for system VDDA value and enable PUMP if VDDA is less then threshold */
                        #if (CY_MSCLP_VDDA_PUMP_TRESHOLD > CY_CAPSENSE_VDDA_MV)
                            ptrHwBase->PUMP_CTL = MSCLP_PUMP_CTL_PUMP_MODE_Msk;
                        #endif

                        /* Configure the start address of FIFO considering fractional part discarding after integer division */
                        CY_REG32_CLR_SET(ptrHwBase->SCAN_CTL1, MSCLP_SCAN_CTL1_FRAME_RES_START_ADDR,
                                         ((uint32_t)MSCLP_SNS_SRAM_WORD_SIZE -
                                          ((((uint32_t)MSCLP_SNS_SRAM_WORD_SIZE / numberLpSlots) - CY_MSCLP_11_SNS_REGS) * numberLpSlots)));
                    }
                }
                else
                {
                    if (0u != (ptrHwBase->MRSS_STATUS & MSCLP_MRSS_STATUS_MRSS_UP_Msk))
                    {
                        /* Disable HW IP to allow MRSS operations */
                        ptrHwBase->CTL &= (~MSCLP_CTL_ENABLED_Msk);

                        /* Stop the MRSS to save power */
                        ptrHwBase->MRSS_CMD = MSCLP_MRSS_CMD_MRSS_STOP_Msk;
                        (void)Cy_CapSense_WaitMrssStatusChange((CY_MSCLP_CLK_LF_PERIOD_MAX * CY_CAPSENSE_MULTIPLIER_TWO), CY_CAPSENSE_MRSS_TURN_OFF, context);
                    }
                }

                /* Set Low Power widget scan status */
                context->ptrCommonContext->status &= (uint32_t)~((uint32_t)CY_CAPSENSE_MW_STATE_WD_SCAN_MASK);
                context->ptrCommonContext->status |= CY_CAPSENSE_MW_STATE_LP_WD_SCAN_MASK;

                if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
                {
                    /* Start of scan callback */
                    if (NULL != ptrIntrCxt->ptrSSCallback)
                    {
                        ptrIntrCxt->ptrSSCallback(context->ptrActiveScanSns);
                    }

                    /* Disable HW block per IFX 005467-513 */
                    ptrHwBase->CTL &= ~MSCLP_CTL_ENABLED_Msk;

                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_EXT_FRM_START_EN)
                        /* Clear the external start scan mode */
                        ptrHwBase->CTL &= ~MSCLP_CTL_EXT_FRAME_START_MODE_Msk;
                    #endif

                    /* Enable HW IP to allow scans */
                    ptrHwBase->CTL |= MSCLP_CTL_ENABLED_Msk;

                    /* Un-mask FR_TIMEOUT interrupt in LP-AOS mode */
                    ptrHwBase->INTR_LP_MASK = MSCLP_INTR_LP_MASK_FR_TIMEOUT_Msk;
                    (void)ptrHwBase->INTR_LP_MASK;
                    /* Start scan */
                    ptrHwBase->WAKEUP_CMD |= MSCLP_WAKEUP_CMD_START_FRAME_AOS_Msk;
                }
            }
        }
    }

    return capStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_ScanAllLpWidgets
****************************************************************************//**
*
* Initiates a non-blocking scan for all low power widgets/sensors.
* If the middleware is busy, do not initiate a new scan or set up widgets.
* Use the Cy_CapSense_IsBusy() function to check HW busyness at a particular moment.
* Use the Cy_CapSense_MwState() function to verify if MW executes any firmware 
* tasks related to initialization, scanning, and processing at a particular moment.
*
* The function is the wrapper for the Cy_CapSense_ScanAllLpSlots() function.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - The input parameter is invalid.
* - CY_CAPSENSE_STATUS_HW_BUSY          - The hardware is busy with the previous scan.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ScanAllLpWidgets(
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_BAD_PARAM;

    if (NULL != context)
    {
        capStatus = Cy_CapSense_ScanLpSlots(0u, CY_CAPSENSE_SLOT_LP_COUNT, context);
    }

    return capStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_ScanAllLpSlots
****************************************************************************//**
*
* Initiates a non-blocking scan of all low power slots and then exits.
* Scanning is initiated only if no scan is in progress.
* A scan initiated by this function can be performed in different power modes
* such as Active, Sleep or Deep Sleep.
* After all specified  number of frames are scanned or if a touch is
* detected during the scan, the interrupt is fired, the CPU switches
* Power mode to Active and the interrupt service routine (part of middleware)
* updates the busy status.
* If the middleware is busy, do not initiate a new scan or set up widgets.
* Use the Cy_CapSense_IsBusy() function to check HW busyness at a particular moment.
* Use the Cy_CapSense_MwState() function to verify if MW executes any firmware 
* tasks related to initialization, scanning, and processing at a particular moment.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation completed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - The input parameter is invalid.
* - CY_CAPSENSE_STATUS_HW_BUSY          - The hardware is busy with the previous scan.
*
* \funcusage
* \snippet capsense/snippet/main.c snippet_Cy_CapSense_ScanAllLpSlots
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ScanAllLpSlots(
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_BAD_PARAM;

    if (NULL != context)
    {
        capStatus = Cy_CapSense_ScanLpSlots(0u, CY_CAPSENSE_SLOT_LP_COUNT, context);
    }

    return capStatus;
}
#endif /* CY_CAPSENSE_LP_EN */

/*******************************************************************************
* Function Name: Cy_CapSense_ScanAllWidgets_V3Lp
****************************************************************************//**
*
* Initiates the non-blocking scan for all widgets/sensors. 
*
* If the middleware is busy, do not initiate a new scan or set up widgets.
* Use the Cy_CapSense_IsBusy() function to check HW busyness at a particular moment.
* Use the Cy_CapSense_MwState() function to verify if MW executes any firmware 
* tasks related to initialization, scanning, and processing at a particular moment.
*
* The function is the wrapper for the Cy_CapSense_ScanAllSlots() function
* to provide the backward compatibility.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - The input parameter is invalid.
* - CY_CAPSENSE_STATUS_HW_BUSY          - The HW is busy with the previous scan.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ScanAllWidgets_V3Lp(cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_BAD_PARAM;

    if (NULL != context)
    {
        capStatus = Cy_CapSense_ScanSlots(0u, CY_CAPSENSE_SLOT_COUNT, context);
    }

    return capStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_ScanWidget_V3Lp
****************************************************************************//**
*
* Initiates the scanning of all sensors in the widget. 
* If the widget is of a low power type it is scanned with the LP_AoS scanning mode 
* (i.e. with the configured maximum number of frames and scan refresh interval).
*
* The function uses Cy_CapSense_ScanSlots() or Cy_CapSense_ScanLpSlots() function
* with the parameters of
* startSlotId and numberSlots retrieved from the firstSlotId and numSlots
* fields of the cy_stc_capsense_widget_config_t structure.
*
* If the middleware is busy, do not initiate a new scan or set up widgets.
* Use the Cy_CapSense_IsBusy() function to check HW busyness at a particular moment.
* Use the Cy_CapSense_MwState() function to verify if MW executes any firmware 
* tasks related to initialization, scanning, and processing at a particular moment.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
* This function is available in single-channel solution.
*
* \param widgetId
* Specifies the ID number of the widget. A macro for the widget ID can be found
* in the cycfg_capsense.h file defined as CY_CAPSENSE_<WIDGET_NAME>_WDGT_ID.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - The input parameter is invalid.
* - CY_CAPSENSE_STATUS_HW_BUSY          - The HW is busy with the previous scan.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ScanWidget_V3Lp(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_BAD_PARAM;

    if (NULL != context)
    {
        if (widgetId < CY_CAPSENSE_TOTAL_WIDGET_COUNT)
        {
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
                if ((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E == context->ptrWdConfig[widgetId].wdType)
                {
                    capStatus = Cy_CapSense_ScanLpSlots(context->ptrWdConfig[widgetId].firstSlotId,
                                                        context->ptrWdConfig[widgetId].numSlots, context);
                }
                else
                {
                    capStatus = Cy_CapSense_ScanSlots(context->ptrWdConfig[widgetId].firstSlotId,
                                                      context->ptrWdConfig[widgetId].numSlots, context);
                }
            #else
            {
                capStatus = Cy_CapSense_ScanSlots(context->ptrWdConfig[widgetId].firstSlotId,
                                                  context->ptrWdConfig[widgetId].numSlots, context);
            }
            #endif
        }
    }
    return capStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_ScanSensor_V3Lp
****************************************************************************//**
*
* Initiates the scanning of the selected sensor in the widget. If the widget is
* of a low power type its sensor is scanned with the LP_AoS scanning mode
* (i.e. with the configured maximum number of frames and scan refresh interval).
*
* If the middleware is busy, do not initiate a new scan or set up widgets.
* Use the Cy_CapSense_IsBusy() function to check HW busyness at a particular moment.
* Use the Cy_CapSense_MwState() function to verify if MW executes any firmware 
* tasks related to initialization, scanning, and processing at a particular moment.
* The function uses Cy_CapSense_ScanSlots() or Cy_CapSense_ScanLpSlots() function.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
* This function is available in single-channel solution.
*
* \param widgetId
* Specifies the ID number of the widget. A macro for the widget ID can be found
* in the cycfg_capsense.h file defined as CY_CAPSENSE_<WIDGET_NAME>_WDGT_ID.
*
* \param sensorId
* Specifies the ID number of the sensor within the widget. A macro for the
* sensor ID within a specified widget can be found in the cycfg_capsense.h
* file defined as CY_CAPSENSE_<WIDGET_NAME>_SNS<SENSOR_NUMBER>_ID.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - The input parameter is invalid.
* - CY_CAPSENSE_STATUS_HW_BUSY          - The HW is busy with the previous scan.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ScanSensor_V3Lp(
                uint32_t widgetId,
                uint32_t sensorId,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_BAD_PARAM;

    if ((NULL != context) &&
        (widgetId < CY_CAPSENSE_TOTAL_WIDGET_COUNT) &&
        (sensorId < context->ptrWdConfig[widgetId].numSns))
    {
        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
            if ((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E == context->ptrWdConfig[widgetId].wdType)
            {
                capStatus = Cy_CapSense_ScanLpSlots((sensorId + context->ptrWdConfig[widgetId].firstSlotId), 1u,
                                                    context);
            }
            else
            {
                capStatus = Cy_CapSense_ScanSlots((sensorId + context->ptrWdConfig[widgetId].firstSlotId), 1u, context);
            }
        #else
        {
            capStatus = Cy_CapSense_ScanSlots((sensorId + context->ptrWdConfig[widgetId].firstSlotId), 1u, context);
        }
        #endif
    }

    return capStatus;
}


#if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CALIBRATION_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CALIBRATION_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CALIBRATION_EN))
/*******************************************************************************
* Function Name: Cy_CapSense_CalibrateAllSlots_V3Lp
****************************************************************************//**
*
* Calibrates CapDACs for all widgets.
*
* The function is the wrapper for the Cy_CapSense_CalibrateAllWidgets() function
* to provide the backward compatibility.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
* This function is available in single-channel solution.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS       - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM     - The input parameter is invalid.
* - CY_CAPSENSE_STATUS_CALIBRATION_FAIL - The calibration failed if software
*                                         watchdog timeout occurred
*                                         during any calibration scan,
*                                         the scan was not completed, or
*                                         resulted raw counts
*                                         are outside the limits.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_CalibrateAllSlots_V3Lp(cy_stc_capsense_context_t * context)
{
    return Cy_CapSense_CalibrateAllWidgets_V3Lp(context);
}


/*******************************************************************************
* Function Name: Cy_CapSense_SetCalibrationTarget_V3Lp
****************************************************************************//**
*
* Sets the CapDAC auto-calibration raw count targets for CSD, CSX and/or ISX
* widgets.
*
* The function sets the specified raw count targets if CSD, CSX and/or
* ISX widgets are in the project and the auto-calibration is enabled for them.
* These targets will be used instead the configured ones by
* Cy_CapSense_CalibrateAllSlots(), Cy_CapSense_CalibrateAllWidgets() and
* Cy_CapSense_CalibrateWidget() functions.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param calibrTarget
* The raw counts target in percentage for the specified sensing method.
* It should be more than 0u and less than 100u. If the specified target is
* outside the range, then it will not be updated and
* the CY_CAPSENSE_STATUS_BAD_PARAM status will be returned.
*
* \param snsMethod
* Desired sensing method the calibration target should be updated for:
* * CY_CAPSENSE_CSD_GROUP - CSD sensing method
* * CY_CAPSENSE_CSX_GROUP - CSX sensing method
* * CY_CAPSENSE_ISX_GROUP - ISX sensing method
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - At least one of the input parameter is
*                                         invalid.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_SetCalibrationTarget_V3Lp(
                uint32_t calibrTarget,
                uint32_t snsMethod,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t calibStatus = CY_CAPSENSE_STATUS_BAD_PARAM;

    if (NULL != context)
    {
        if ((CY_CAPSENSE_PERCENTAGE_100 > calibrTarget) && (0u < calibrTarget))
        {
            switch (snsMethod)
            {
                #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN)
                    case CY_CAPSENSE_CSD_GROUP:
                        context->ptrInternalContext->intrCsdRawTarget = (uint8_t)calibrTarget;
                        break;
                #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN) */

                #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
                    case CY_CAPSENSE_CSX_GROUP:
                        context->ptrInternalContext->intrCsxRawTarget = (uint8_t)calibrTarget;
                        break;
                #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) */

                #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN)
                    case CY_CAPSENSE_ISX_GROUP:
                        context->ptrInternalContext->intrIsxRawTarget = (uint8_t)calibrTarget;
                        break;
                #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN) */

                default:
                    /* No action */
                    break;
            }
            calibStatus = CY_CAPSENSE_STATUS_SUCCESS;
        }
    }

    return calibStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_CalibrateAllWidgets_V3Lp
****************************************************************************//**
*
* Executes CapDAC auto-calibration for all all relevant Active widgets if
* enabled.
*
* Having enabled the CDAC auto-calibration algorithm is the most common use
* case. It helps to tune your system considering board-to-board variation,
* temperature drift, etc. CDAC auto-calibration is enabled by default.
*
* The function performs searching of Reference CDAC code, Compensation CDAC
* code and Compensation Divider (whichever is enabled) by using a successive
* approximation method to make the sensor's raw count closest to the
* defined targets. The auto-calibration target values are defined
* (by default) as:
* * 85% of the maximum raw count for CSD widgets
* * 40% of the maximum raw count for CSX widgets.
* * 40% of the maximum raw count for ISX widgets.
*
* To change calibration targets use the Cy_CapSense_SetCalibrationTarget() function.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - The input parameter is invalid.
* - CY_CAPSENSE_STATUS_CALIBRATION_FAIL - The calibration is failed due to
*                                         the issues with scanning (either
*                                         watchdog timer, interrupt breaking, etc.).
* - CY_CAPSENSE_STATUS_CALIBRATION_REF_CHECK_FAIL - The reference/fine CapDAC
*                                  calibration stage is failed as the raw count
*                                  minimum across widget is out of range.
* - CY_CAPSENSE_STATUS_CALIBRATION_CHECK_FAIL - The resulting rawcounts across
*                                  all sensors in widget are out of defined range.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_CalibrateAllWidgets_V3Lp(cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t calibStatus = CY_CAPSENSE_STATUS_SUCCESS;
    uint32_t widgetId;

    if (NULL != context)
    {
        for (widgetId = 0u; widgetId < context->ptrCommonConfig->numWd; widgetId++)
        {
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
                if (context->ptrWdConfig[widgetId].wdType != (uint8_t)CY_CAPSENSE_WD_LOW_POWER_E)
            #endif
            {
                calibStatus |= Cy_CapSense_CalibrateWidget_V3Lp(widgetId, context);
            }
        }
    }

    /* Disable repeated scans after calibrations */
    context->ptrInternalContext->repeatScanEn = CY_CAPSENSE_DISABLE;
    context->ptrCommonContext->status &= (uint32_t)~((uint32_t)CY_CAPSENSE_MW_STATE_WD_SCAN_MASK);

    return calibStatus;
}


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_CalibrateAllLpSlots
****************************************************************************//**
*
* Calibrates CapDACs for all Low power widgets.
*
* The function is the wrapper for the Cy_CapSense_CalibrateAllLpWidgets() function
* to provide the backward compatibility.
*
* \note
* This function is available only for the fifth-generation
* low power CAPSENSE&trade;.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS       - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM     - The input parameter is invalid.
* - CY_CAPSENSE_STATUS_CALIBRATION_FAIL - The calibration failed if software
*                                         watchdog timeout occurred
*                                         during any calibration scan,
*                                         the scan was not completed, or
*                                         resulted raw counts
*                                         are outside the limits.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_CalibrateAllLpSlots(cy_stc_capsense_context_t * context)
{
    return Cy_CapSense_CalibrateAllLpWidgets(context);
}
#endif


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_CalibrateAllLpWidgets
****************************************************************************//**
*
* Executes CapDAC auto-calibration for all relevant low power widgets if enabled.
*
* Having enabled the CDAC auto-calibration algorithm is the most common use
* case. It helps to tune your system considering board-to-board variation,
* temperature drift, etc. CDAC auto-calibration is enabled by default.
*
* The function performs searching of Reference CDAC code, Compensation CDAC
* code, Compensation Divider (whichever is enabled) by using a successive
* approximation method to make the sensor's raw count closest to the
* defined targets. The auto-calibration target values are defined
* (by default) as:
* * 85% of the maximum raw count for CSD widgets
* * 40% of the maximum raw count for CSX widgets.
* * 40% of the maximum raw count for ISX widgets.
*
* To change calibration targets use the Cy_CapSense_SetCalibrationTarget() function.
*
* \note
* This function is available only for the fifth-generation
* low power CAPSENSE&trade;.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - The input parameter is invalid.
* - CY_CAPSENSE_STATUS_CALIBRATION_FAIL - The calibration is failed due to
*                                         the issues with scanning (either
*                                         watchdog timer, interrupt breaking, etc.).
* - CY_CAPSENSE_STATUS_CALIBRATION_REF_CHECK_FAIL - The reference/fine CapDAC
*                                  calibration stage is failed as the raw count
*                                  minimum across widget is out of range.
* - CY_CAPSENSE_STATUS_CALIBRATION_CHECK_FAIL - The resulting rawcounts across
*                                  all sensors in widget are out of defined range.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_CalibrateAllLpWidgets(cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t calibStatus = CY_CAPSENSE_STATUS_SUCCESS;
    uint32_t widgetId;

    if (NULL != context)
    {
        for (widgetId = 0u; widgetId < context->ptrCommonConfig->numWd; widgetId++)
        {
            if (context->ptrWdConfig[widgetId].wdType == (uint8_t)CY_CAPSENSE_WD_LOW_POWER_E)
            {
                calibStatus |= Cy_CapSense_CalibrateWidget_V3Lp(widgetId, context);
            }
        }
    }

    /* Disable repeated scans after calibrations */
    context->ptrInternalContext->repeatScanEn = CY_CAPSENSE_DISABLE;
    context->ptrCommonContext->status &= (uint32_t)~((uint32_t)CY_CAPSENSE_MW_STATE_WD_SCAN_MASK);

    return calibStatus;
}
#endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN) */


#endif /*
        *  ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CALIBRATION_EN) || \
        *   (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CALIBRATION_EN) || \
        *   (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CALIBRATION_EN))
        */

/*******************************************************************************
* Function Name: Cy_CapSense_ConfigureMsclpTimer
****************************************************************************//**
*
* Configures the wakeup timer value for Active mode. The wakeup timer interval
* is introduced before each scan frame start. Use the function to implement
* different Active scan refresh rates (for instance an Active mode with
* the 128 Hz refresh rate and an Active Low Refresh Rate mode with the 32 Hz
* refresh rate).
*
* The minimum wakeup time value is corresponding to one ILO cycle (25us for
* 40KHz ILO). The maximum wakeup time value depends on actual ILO frequency and
* can be set to a value, corresponding to 2^16 ILO cycles (1638400us for
* 40KHz ILO). If the timer value exceeds 2^16 ILO cycles, it would be set to
* the maximum possible value.
* The real wakeup time interval depends on ILO frequency which have a big
* tolerance (above +/- 50 %), see device datasheets. In order to improve the
* timer accuracy, use Cy_CapSense_IloCompensate() function.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param wakeupTimer
* The desired wakeup timer value in microseconds.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS       - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM     - The input parameter is invalid.
*
* \funcusage
* \snippet capsense/snippet/main.c snippet_Cy_CapSense_ConfigureMsclpTimer
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ConfigureMsclpTimer(
                uint32_t wakeupTimer,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t result = CY_CAPSENSE_STATUS_BAD_PARAM;

    if (NULL != context)
    {
        result = CY_CAPSENSE_STATUS_SUCCESS;
        context->ptrInternalContext->activeWakeupTimer = wakeupTimer;

        /* Calculate and store compensated wakeup timer value */
        context->ptrInternalContext->activeWakeupTimerCycles =
            Cy_CapSense_MsclpTimerCalcCycles(wakeupTimer, context);

        if (0u != (context->ptrCommonContext->status & CY_CAPSENSE_MW_STATE_ACTIVE_WD_SCAN_MASK))
        {
            /* Update value for the wakeup timer */
            context->ptrCommonConfig->ptrChConfig->ptrHwBase->AOS_CTL &= ~MSCLP_AOS_CTL_WAKEUP_TIMER_Msk;
            context->ptrCommonConfig->ptrChConfig->ptrHwBase->AOS_CTL |=
                (uint32_t)(context->ptrInternalContext->activeWakeupTimerCycles << MSCLP_AOS_CTL_WAKEUP_TIMER_Pos);
        }
    }
    return result;
}


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_ConfigureMsclpWotTimer
****************************************************************************//**
*
* Configures the wakeup timer value for Wake-On-Touch mode. The wakeup time is
* introduced before each scan frame.
*
* The minimum wakeup time value is corresponding to one ILO cycle (25us for
* 40KHz ILO). The maximum wakeup time value depends on actual ILO frequency and
* can be set to a value, corresponding to 2^16 ILO cycles (1638400us for
* 40KHz ILO). If the timer value exceeds 2^16 ILO cycles, it would be set to
* the maximum possible value.
* The real wakeup time interval depends on ILO frequency which have a big
* tolerance (above +/- 50 %), see device datasheets. In order to improve the
* timer accuracy, use Cy_CapSense_IloCompensate() function.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param wakeupTimer
* The desired wakeup timer value in microseconds.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS       - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM     - The input parameter is invalid.
*
* \funcusage
* \snippet capsense/snippet/main.c snippet_Cy_CapSense_ScanAllLpSlots
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ConfigureMsclpWotTimer(
                uint32_t wakeupTimer,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t result = CY_CAPSENSE_STATUS_BAD_PARAM;

    if (NULL != context)
    {
        result = CY_CAPSENSE_STATUS_SUCCESS;
        context->ptrInternalContext->wotScanInterval = wakeupTimer;

        /* Calculate and store compensated wakeup timer value */
        context->ptrInternalContext->wotScanIntervalCycles =
            Cy_CapSense_MsclpTimerCalcCycles(wakeupTimer, context);

        if (0u != (context->ptrCommonContext->status & CY_CAPSENSE_MW_STATE_LP_WD_SCAN_MASK))
        {
            /* Update value for the wakeup timer */
            context->ptrCommonConfig->ptrChConfig->ptrHwBase->AOS_CTL &= ~MSCLP_AOS_CTL_WAKEUP_TIMER_Msk;
            context->ptrCommonConfig->ptrChConfig->ptrHwBase->AOS_CTL |=
                (uint32_t)(context->ptrInternalContext->wotScanIntervalCycles << MSCLP_AOS_CTL_WAKEUP_TIMER_Pos);
        }
    }
    return result;
}
#endif


/*******************************************************************************
* Function Name: Cy_CapSense_IloCompensate
****************************************************************************//**
*
* Measures the actual ILO frequency and calculates the compensation factor for MSCLP
* Active and Wake-On-Touch mode timers. In order to keep timer intervals
* accurate, call this function periodically.
* To set Active and Wake-On-Touch mode timers, use
* Cy_CapSense_ConfigureMsclpTimer() and Cy_CapSense_ConfigureMsclpWotTimer()
* functions correspondingly.
*
* \note SysClk should be clocked by IMO, otherwise the
* Cy_CapSense_IloCompensate() function can work incorrectly.
*
* \note If the System clock frequency is changed in runtime, the
* mtb-pdl-cat2 SystemCoreClockUpdate() function should be called before
* calling Cy_CapSense_IloCompensate().
*
* \note This function is blocking, function execution time is ~1ms, regardless
* of IMO frequency.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS       - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM     - The input parameter is invalid.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_IloCompensate(cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t result = CY_CAPSENSE_STATUS_BAD_PARAM;
    uint32_t dummyVar = CY_CAPSENSE_ILO_COMPENSATE_DELAY;
    uint16_t trimCnt2Val;

    if (NULL != context)
    {
        /* Perform ILO measurement and get only the result of SRSSLT_TST_TRIM_CNTR2.
        *  The measurement counts number of ILO clocks per set number of IMO clocks,
        *  which corresponds to IMO frequency(Hz) / 1024, so measurement time is
        *  always equal to 1 / 1024 seconds and actual ILO frequency is equal to
        *  SRSSLT_TST_TRIM_CNTR2 value * 1024 or SRSSLT_TST_TRIM_CNTR2 value * 2^10.
        */
        Cy_SysClk_IloStartMeasurement();
        while (CY_SYSCLK_SUCCESS != Cy_SysClk_IloCompensate(dummyVar, &dummyVar))
        {
            /* Wait for the end of ILO measurement */
        }
        trimCnt2Val = (uint16_t)SRSSLT_TST_TRIM_CNTR2;
        Cy_SysClk_IloStopMeasurement();

        /* Calculate ILO compensation factor using number of ILO clocks, measured
        *  by SRSSLT_TST_TRIM_CNTR2. Factor calculated as
        *  actual ILO frequency (Hz) * 2^14 / 1000000 or
        *  SRSSLT_TST_TRIM_CNTR2 * 2^24 / 1000000.
        *  Multiplier 2^14 is used for calculation optimization, so integer
        *  division by 1000000 can be performed during factor calculation.
        */
        context->ptrInternalContext->iloCompensationFactor =
                ((uint32_t)trimCnt2Val << CY_CAPSENSE_ILO_FACTOR_SHIFT) /
                CY_CAPSENSE_1M_DIVIDER;

        /* Calculate and store active and wake-on-touch timer values */
        context->ptrInternalContext->activeWakeupTimerCycles =
            Cy_CapSense_MsclpTimerCalcCycles(context->ptrInternalContext->activeWakeupTimer, context);
        context->ptrInternalContext->wotScanIntervalCycles =
            Cy_CapSense_MsclpTimerCalcCycles(context->ptrInternalContext->wotScanInterval, context);

        /* Select correct timer value */
        dummyVar = context->ptrInternalContext->activeWakeupTimerCycles;
        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
            if (0u != (context->ptrCommonContext->status & CY_CAPSENSE_MW_STATE_LP_WD_SCAN_MASK))
            {
                dummyVar = context->ptrInternalContext->wotScanIntervalCycles;
            }
        #endif

        /* Update AOS_CTL register with selected value */
        context->ptrCommonConfig->ptrChConfig->ptrHwBase->AOS_CTL &= ~MSCLP_AOS_CTL_WAKEUP_TIMER_Msk;
        context->ptrCommonConfig->ptrChConfig->ptrHwBase->AOS_CTL |= (uint32_t)(dummyVar << MSCLP_AOS_CTL_WAKEUP_TIMER_Pos);

        result = CY_CAPSENSE_STATUS_SUCCESS;
    }

    return result;
}


/*******************************************************************************
* Function Name: Cy_CapSense_MsclpTimerCalcCycles
****************************************************************************//**
*
* Calculates the value of MSCLP wakeup timer in number of ILO clocks based on
* compensation factor, measured by Cy_CapSense_IloCompensate() function.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param wakeupTimer
* The desired wakeup timer value in microseconds.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* The wakeupTimer value in ILO cycles.
*
*******************************************************************************/
uint32_t Cy_CapSense_MsclpTimerCalcCycles(uint32_t wakeupTimer, cy_stc_capsense_context_t * context)
{
    /* Calculate actual number of ILO clocks, based on iloCompensationFactor.
    *  Number of ILO cycles equal to wakeupTimer * actual ILO Frequency (Hz) / 1000000 or
    *  wakeupTimer * iloCompensationFactor / 2^14.
    */
    uint32_t numIloClocks = ((wakeupTimer * context->ptrInternalContext->iloCompensationFactor) >>
                            CY_CAPSENSE_ILO_COMPENSATE_SHIFT);

    /* Check wakeup timer value ranges */
    if (0u < numIloClocks)
    {
        numIloClocks--;
    }
    if (((uint32_t)MSCLP_AOS_CTL_WAKEUP_TIMER_Msk >> MSCLP_AOS_CTL_WAKEUP_TIMER_Pos) < numIloClocks)
    {
        numIloClocks = (uint32_t)MSCLP_AOS_CTL_WAKEUP_TIMER_Msk >> MSCLP_AOS_CTL_WAKEUP_TIMER_Pos;
    }

    return numIloClocks;
}


#if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CALIBRATION_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CALIBRATION_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CALIBRATION_EN))
/*******************************************************************************
* Function Name: Cy_CapSense_CalibrateWidget_V3Lp
****************************************************************************//**
*
* Executes the CapDAC calibration for all the sensors in the specified widget
* to the default target value.
*
* This function performs exactly the same tasks as
* Cy_CapSense_CalibrateAllWidgets(), but only for a specified widget.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
* This function is available in single-channel solution.
*
* \param widgetId
* Specifies the ID number of the widget. A macro for the widget ID can be found
* in the cycfg_capsense.h file defined as CY_CAPSENSE_<WIDGET_NAME>_WDGT_ID.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS   - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM - The input parameter is invalid.
* - CY_CAPSENSE_STATUS_CALIBRATION_FAIL - The calibration is failed due to
*                                  the issues with scanning (either
*                                  watchdog timer, interrupt breaking, etc.).
* - CY_CAPSENSE_STATUS_CALIBRATION_REF_CHECK_FAIL - The reference/fine CapDAC
*                                  calibration stage is failed as the raw count
*                                  minimum across widget is out of range.
* - CY_CAPSENSE_STATUS_CALIBRATION_CHECK_FAIL - The resulting rawcounts across
*                                  all sensors in widget are out of defined range.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_CalibrateWidget_V3Lp(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t calibrationStatus = CY_CAPSENSE_STATUS_SUCCESS;
    const cy_stc_capsense_widget_config_t * ptrWdCfg;
    cy_stc_capsense_widget_context_t * ptrWdCxt;
    uint32_t cdacConfig;
    uint32_t snsIndex;

    if ((NULL != context) && (CY_CAPSENSE_TOTAL_WIDGET_COUNT > widgetId) &&
        (0u != Cy_CapSense_IsWidgetEnabled(widgetId, context)))
    {
        ptrWdCfg = &context->ptrWdConfig[widgetId];

        if (((uint8_t)CY_CAPSENSE_WD_LIQUID_LEVEL_E != ptrWdCfg->wdType) ||
            (((uint8_t)CY_CAPSENSE_WD_LIQUID_LEVEL_E == ptrWdCfg->wdType) &&
            (0u == (ptrWdCfg->centroidConfig & CY_CAPSENSE_LLW_TUNING_COMPLETED_MASK))))
        {
            ptrWdCxt = ptrWdCfg->ptrWdContext;
            cdacConfig = ptrWdCfg->cdacConfig;

            context->ptrCommonContext->status |= CY_CAPSENSE_MW_STATE_CALIBRATION_MASK;

            /* Reference CapDac configuration */
            if (CY_CAPSENSE_CDAC_REF_MODE_MANUAL_MASK != (cdacConfig & CY_CAPSENSE_CDAC_REF_MODE_MASK))
            {
                ptrWdCxt->cdacRef = 0u;
                ptrWdCxt->rowCdacRef = 0u;
            }

            /* Fine CapDac configuration */
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_FINE_AUTO_EN)
                if (CY_CAPSENSE_CDAC_FINE_MODE_MANUAL_MASK != (cdacConfig & CY_CAPSENSE_CDAC_FINE_MODE_MASK))
                {
                    ptrWdCxt->cdacFine = 0u;
                    ptrWdCxt->rowCdacFine = 0u;
                }
            #endif

            /* Compensation CapDac configuration */
            if (CY_CAPSENSE_CDAC_COMP_MODE_MANUAL_MASK != (cdacConfig & CY_CAPSENSE_CDAC_COMP_MODE_MASK))
            {
                for (snsIndex = 0u; snsIndex < (uint32_t)ptrWdCfg->numSns; snsIndex++)
                {
                    ptrWdCfg->ptrSnsContext[snsIndex].cdacComp = 0u;
                }
            }

            Cy_CapSense_SetWidgetFrameCompCdacCode(widgetId, CY_CAPSENSE_CAL_MODE_COMP_CDAC_CODE_VAL, context);
            Cy_CapSense_SetWidgetFrameRefCdacCodes(widgetId, context);

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_REF_AUTO_EN)
                if (0u != (cdacConfig & CY_CAPSENSE_CDAC_REF_MODE_AUTO_MASK))
                {
                    calibrationStatus |= Cy_CapSense_CalibrateRefCdac(widgetId, context);
                    Cy_CapSense_SetWidgetFrameRefCdacCodes(widgetId, context);
                }
            #endif

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_FINE_AUTO_EN)
                if (0u != (cdacConfig & CY_CAPSENSE_CDAC_FINE_MODE_AUTO_MASK))
                {
                    calibrationStatus |= Cy_CapSense_CalibrateFineCdac(widgetId, context);
                    Cy_CapSense_SetWidgetFrameRefCdacCodes(widgetId, context);
                }
            #endif

            #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_REF_AUTO_EN)      || \
                (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_FINE_AUTO_EN))
                if (0u != (cdacConfig & (CY_CAPSENSE_CDAC_REF_MODE_AUTO_MASK  |
                                        CY_CAPSENSE_CDAC_FINE_MODE_AUTO_MASK)))
                {
                    if (CY_CAPSENSE_ISX_GROUP != ptrWdCfg->senseMethod)
                    {
                        /* Check reference CapDac calibration result */
                        calibrationStatus |= Cy_CapSense_VerifyReferenceCdac(widgetId, context);
                    }
                }
            #endif

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_REF_AUTO_EN)
                #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
                    /* Skip boost for MPSC */
                    if (CY_CAPSENSE_MPSC_MIN_ORDER > context->ptrWdConfig[widgetId].mpOrder)
                #endif
                    {
                        ptrWdCxt->cdacRef /= (uint8_t)((cdacConfig & CY_CAPSENSE_CDAC_BOOST_VAL_MASK) >> CY_CAPSENSE_CDAC_BOOST_VAL_POS);
                        ptrWdCxt->rowCdacRef /= (uint8_t)((cdacConfig & CY_CAPSENSE_CDAC_BOOST_VAL_MASK) >> CY_CAPSENSE_CDAC_BOOST_VAL_POS);
                        Cy_CapSense_SetWidgetFrameRefCdacCodes(widgetId, context);
                    }
            #endif

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_COMP_AUTO_EN)
                #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_COMP_DIV_AUTO_EN)
                    if (0u != (cdacConfig & CY_CAPSENSE_CDAC_COMP_DIV_MODE_AUTO_MASK))
                    {
                        calibrationStatus |= Cy_CapSense_CalibrateCompDivider(widgetId, context);
                    }
                #endif
                if (0u != (cdacConfig & CY_CAPSENSE_CDAC_COMP_MODE_AUTO_MASK))
                {
                    calibrationStatus |= Cy_CapSense_CalibrateCompCdac(widgetId, context);
                }
                Cy_CapSense_SetWidgetFrameCompCdacCode(widgetId, CY_CAPSENSE_CAL_MODE_COMP_CDAC_CODE_VAL, context);
            #endif

            #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_REF_AUTO_EN)      || \
                (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_FINE_AUTO_EN)     || \
                (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_COMP_AUTO_EN))
                if (0u != (cdacConfig & (CY_CAPSENSE_CDAC_REF_MODE_AUTO_MASK   |
                                        CY_CAPSENSE_CDAC_FINE_MODE_AUTO_MASK  |
                                        CY_CAPSENSE_CDAC_COMP_MODE_AUTO_MASK  |
                                        CY_CAPSENSE_CDAC_COMP_DIV_MODE_AUTO_MASK)))
                {
                    /* Check final calibration result */
                    calibrationStatus |= Cy_CapSense_VerifyCalibration(widgetId, context);
                }
            #endif

            /* Update CRC if BIST is enabled */
            #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_BIST_EN) &&\
                (CY_CAPSENSE_ENABLE == CY_CAPSENSE_TST_WDGT_CRC_EN))
                Cy_CapSense_UpdateCrcWidget(widgetId, context);
            #endif

            if (CY_CAPSENSE_STATUS_SUCCESS != calibrationStatus)
            {
                calibrationStatus |= CY_CAPSENSE_STATUS_CALIBRATION_FAIL;
            }

            context->ptrCommonContext->status &= ~(uint32_t)CY_CAPSENSE_MW_STATE_CALIBRATION_MASK;

            (void)Cy_CapSense_SwitchHwConfiguration(CY_CAPSENSE_HW_CONFIG_UNDEFINED, context);
        }
    }
    else
    {
        calibrationStatus = CY_CAPSENSE_STATUS_BAD_PARAM;
    }

    return calibrationStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_SetWidgetFrameRefCdacCodes
****************************************************************************//**
*
* This function updates reference and fine CDACs codes in sensor
* frame to match values in widget structure.
*
* \note
* This function is available only
* for the fifth-generation low power CAPSENSE&trade;.
*
* \param widgetId
* Specifies the ID number of the widget.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_SetWidgetFrameRefCdacCodes(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context)
{
    cy_stc_capsense_widget_config_t const * ptrWdCfg = &context->ptrWdConfig[widgetId];
    cy_stc_capsense_widget_context_t * ptrWdCxt = &context->ptrWdContext[widgetId];
    uint32_t snsIndex;
    uint32_t frameSize;
    uint32_t * ptrSnsFrmCdacCtlReg;

    frameSize = CY_CAPSENSE_SENSOR_FRAME_SIZE;
    ptrSnsFrmCdacCtlReg = &context->ptrSensorFrameContext[CY_CAPSENSE_SNS_CDAC_CTL_INDEX];
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        if ((ptrWdCfg->wdType == (uint8_t)CY_CAPSENSE_WD_LOW_POWER_E))
        {
            ptrSnsFrmCdacCtlReg = &context->ptrSensorFrameLpContext[CY_CAPSENSE_FRM_LP_SNS_CDAC_CTL_INDEX];
            frameSize = CY_MSCLP_11_SNS_REGS;
        }
    #endif

    ptrSnsFrmCdacCtlReg += (frameSize * ptrWdCfg->firstSlotId);

    for (snsIndex = 0u; snsIndex < ptrWdCfg->numSns; snsIndex++)
    {
        *ptrSnsFrmCdacCtlReg &= (uint32_t)~(MSCLP_SNS_SNS_CDAC_CTL_SEL_RE_Msk |
                                            MSCLP_SNS_SNS_CDAC_CTL_SEL_CF_Msk);

        #if ((CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_MATRIX_EN) || (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_TOUCHPAD_EN))
            if ((CY_CAPSENSE_CSD_GROUP == context->ptrWdConfig[widgetId].senseMethod) &&
                (ptrWdCfg->numCols <= snsIndex) &&
                (((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == ptrWdCfg->wdType) ||
                ((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == ptrWdCfg->wdType)))
            {
                *ptrSnsFrmCdacCtlReg |= ((((uint32_t)ptrWdCxt->rowCdacRef)) << MSCLP_SNS_SNS_CDAC_CTL_SEL_RE_Pos);
                #if (CY_CAPSENSE_CDAC_FINE_USAGE)
                    *ptrSnsFrmCdacCtlReg |= (((uint32_t)ptrWdCxt->rowCdacFine) << MSCLP_SNS_SNS_CDAC_CTL_SEL_CF_Pos);
                #endif
            }
            else
        #endif
        {
            *ptrSnsFrmCdacCtlReg |= (((uint32_t)ptrWdCxt->cdacRef) << MSCLP_SNS_SNS_CDAC_CTL_SEL_RE_Pos);
            #if (CY_CAPSENSE_CDAC_FINE_USAGE)
                *ptrSnsFrmCdacCtlReg |= (((uint32_t)ptrWdCxt->cdacFine) << MSCLP_SNS_SNS_CDAC_CTL_SEL_CF_Pos);
            #endif
        }

        ptrSnsFrmCdacCtlReg += frameSize;
    }
}


/*******************************************************************************
* Function Name: Cy_CapSense_SetWidgetFrameCompCdacCode
****************************************************************************//**
*
* Sets the Compensation CDAC code into sensor frames.
*
* This function applies Compensation CDAC code for all
* sensors within specified widget in sensor frame structures.
*
* \param widgetId
* Specifies widget ID.
*
* \param mode
* Specifies the Compensation CDAC code:
* 
* * CY_CAPSENSE_CAL_MODE_COMP_CDAC_CODE_MIN - Sets the minimum CDAC code.
* * CY_CAPSENSE_CAL_MODE_COMP_CDAC_CODE_MAX - Sets the maximum CDAC code.
* * CY_CAPSENSE_CAL_MODE_COMP_CDAC_CODE_VAL - Sets the CDAC code specified in the sensor configuration.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_SetWidgetFrameCompCdacCode(
                uint32_t widgetId,
                uint32_t mode,
                cy_stc_capsense_context_t * context)
{
    const cy_stc_capsense_widget_config_t * ptrWdCfg = &context->ptrWdConfig[widgetId];
    cy_stc_capsense_sensor_context_t * ptrSnsCxt = ptrWdCfg->ptrSnsContext;

    uint32_t snsCount = ptrWdCfg->numSns;
    uint32_t frameSize;
    uint32_t * ptrSnsFrmCdacCtlReg;

    frameSize = CY_CAPSENSE_SENSOR_FRAME_SIZE;
    ptrSnsFrmCdacCtlReg = &context->ptrSensorFrameContext[CY_CAPSENSE_SNS_CDAC_CTL_INDEX];
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        if ((ptrWdCfg->wdType == (uint8_t)CY_CAPSENSE_WD_LOW_POWER_E))
        {
            frameSize = CY_MSCLP_11_SNS_REGS;
            ptrSnsFrmCdacCtlReg = &context->ptrSensorFrameLpContext[CY_CAPSENSE_FRM_LP_SNS_CDAC_CTL_INDEX];
        }
    #endif

    ptrSnsFrmCdacCtlReg += (frameSize * ptrWdCfg->firstSlotId);
    for (;snsCount-- > 0u;)
    {
        *ptrSnsFrmCdacCtlReg &= (uint32_t)~(MSCLP_SNS_SNS_CDAC_CTL_SEL_CO_Msk);
        switch (mode)
        {
            case CY_CAPSENSE_CAL_MODE_COMP_CDAC_CODE_MAX:
                *ptrSnsFrmCdacCtlReg |= ((uint32_t)MSCLP_SNS_SNS_CDAC_CTL_SEL_CO_Msk);
                break;

            case CY_CAPSENSE_CAL_MODE_COMP_CDAC_CODE_VAL:
                *ptrSnsFrmCdacCtlReg |= (((uint32_t)ptrSnsCxt->cdacComp) << MSCLP_SNS_SNS_CDAC_CTL_SEL_CO_Pos);
                break;

            default:
                /* No action for other modes */
                break;
        }
        ptrSnsFrmCdacCtlReg += frameSize;
        ptrSnsCxt++;
    }
}


/*******************************************************************************
* Function Name: Cy_CapSense_MinRawSearch
****************************************************************************//**
*
* This function seeks for a minimal raw count across the widget.
*
* \note
* This function is available only
* for the fifth-generation low power CAPSENSE&trade;.
*
* \param widgetId
* The widget ID scans will be done for.
*
* \param rowFlag
* The flag for a row/column sensors seek.
* CY_CAPSENSE_ROW_SNS_CALIBRATION - seek performed for rows.
* CY_CAPSENSE_COL_SNS_CALIBRATION - seek performed for columns.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* The minimal raw count.
*
*******************************************************************************/
uint32_t Cy_CapSense_MinRawSearch(
                uint32_t widgetId,
                uint32_t rowFlag,
                cy_stc_capsense_context_t * context)
{
    cy_stc_capsense_widget_config_t const * ptrWdCfg = &context->ptrWdConfig[widgetId];
    cy_stc_capsense_sensor_context_t * ptrSnsCxt = ptrWdCfg->ptrSnsContext;
    uint32_t snsCount;
    uint32_t minRaw = CY_CAPSENSE_32_BIT_MASK;

    snsCount = ptrWdCfg->numSns;
    #if ((CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_MATRIX_EN) || (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_TOUCHPAD_EN))
        if ((CY_CAPSENSE_CSD_GROUP == context->ptrWdConfig[widgetId].senseMethod) &&
            (((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == context->ptrWdConfig[widgetId].wdType) ||
             ((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == context->ptrWdConfig[widgetId].wdType)))
        {
            snsCount = ptrWdCfg->numCols;
            if (CY_CAPSENSE_ROW_SNS_CALIBRATION != rowFlag)
            {
                ptrSnsCxt += snsCount;
                snsCount = ptrWdCfg->numRows;
            }
        }
    #else
        (void)rowFlag;
    #endif

    for (;snsCount-- > 0u;)
    {
        if (ptrSnsCxt->raw < minRaw)
        {
            minRaw = ptrSnsCxt->raw;
        }
        ptrSnsCxt++;
    }

    return minRaw;
}


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
/*******************************************************************************
* Function Name: Cy_CapSense_MaxRawSearch
****************************************************************************//**
*
* This function seeks for a maximum raw count across the widget.
*
* \note
* This function is available only
* for the fifth-generation low power CAPSENSE&trade;.
*
* \param widgetId
* The widget ID scans will be done for.
*
* \param rowFlag
* The flag for a row/column sensors seek.
* CY_CAPSENSE_ROW_SNS_CALIBRATION - seek performed for rows.
* CY_CAPSENSE_COL_SNS_CALIBRATION - seek performed for columns.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* The maximum raw count.
*
*******************************************************************************/
uint32_t Cy_CapSense_MaxRawSearch(
                uint32_t widgetId,
                uint32_t rowFlag,
                cy_stc_capsense_context_t * context)
{
    cy_stc_capsense_widget_config_t const * ptrWdCfg = &context->ptrWdConfig[widgetId];
    cy_stc_capsense_sensor_context_t * ptrSnsCxt = ptrWdCfg->ptrSnsContext;
    uint32_t snsCount;
    uint32_t maxRaw = 0u;

    snsCount = ptrWdCfg->numSns;
    #if ((CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_MATRIX_EN) || (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_TOUCHPAD_EN))
        if ((CY_CAPSENSE_CSD_GROUP == context->ptrWdConfig[widgetId].senseMethod) &&
            (((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == context->ptrWdConfig[widgetId].wdType) ||
             ((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == context->ptrWdConfig[widgetId].wdType)))
        {
            snsCount = ptrWdCfg->numCols;
            if (CY_CAPSENSE_ROW_SNS_CALIBRATION != rowFlag)
            {
                ptrSnsCxt += snsCount;
                snsCount = ptrWdCfg->numRows;
            }
        }
    #else
        (void)rowFlag;
    #endif

    for (;snsCount-- > 0u;)
    {
        if (ptrSnsCxt->raw > maxRaw)
        {
            maxRaw = ptrSnsCxt->raw;
        }
        ptrSnsCxt++;
    }

    return maxRaw;
}
#endif


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_REF_AUTO_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_CalculateAbsDiff
****************************************************************************//**
*
* The internal function that returns absolute difference of two integers.
*
* \note
* This function is available only
* for the fifth-generation low power CAPSENSE&trade;.
*
* \param a
* The first argument to calculate difference.
*
* \param b
* The second argument to calculate difference.
*
* \return
* Returns the absolute difference of arguments.
*
*******************************************************************************/
uint32_t Cy_CapSense_CalculateAbsDiff(
                uint32_t a,
                uint32_t b)
{
    uint32_t result;

    if (a > b)
    {
        result = a - b;
    }
    else
    {
        result = b - a;
    }
    return result;
}
#endif


/*******************************************************************************
* Function Name: Cy_CapSense_CdacSuccessAppr
****************************************************************************//**
*
* The internal function that performs the specified CDAC successive
* approximation seek for the specified widget.
*
* The function performs some scans of the slots in specified widget in the CPU
* driven scan mode to seek a CDAC value which produce raw counts greater than
* the configured target.
* The function usage is limited by the CapDAC auto-calibration.
*
* \note
* This function is available only
* for the fifth-generation low power CAPSENSE&trade;.
*
* \param widgetId
* The widget ID scans will be done for.
*
* \param rowFlag
* The flag for a row/column sensors calibration.
* CY_CAPSENSE_ROW_SNS_CALIBRATION - perform calibration for rows.
* CY_CAPSENSE_COL_SNS_CALIBRATION - perform calibration for columns.
*
* \param calibrMask
* The mask for further calibration.
*
* \param cdacPtr
* The pointer to the CDAC field in data structure.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS   - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_CALIBRATION_FAIL - The calibration is failed due to
*                                  the issues with scanning (either
*                                  watchdog timer, interrupt breaking, etc.).
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_CdacSuccessAppr(
                uint32_t widgetId,
                uint32_t rowFlag,
                uint8_t calibrMask,
                uint8_t * cdacPtr,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t calibrationStatus = CY_CAPSENSE_STATUS_SUCCESS;
    uint32_t rawTarget;
    uint32_t minRaw  = 0u;
    uint32_t csdScanEn = CY_CAPSENSE_DISABLE;
    uint32_t cdacMask = calibrMask;
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_REF_AUTO_EN)
        uint32_t advancedSearchFlag = CY_CAPSENSE_DISABLE;
        uint32_t minRawAbs = CY_CAPSENSE_16_BIT_MASK;
        uint8_t minRawCode = 0u;
        uint32_t tmpRaw;

        if (CY_CAPSENSE_DISABLE == (context->ptrWdConfig[widgetId].cdacConfig & CY_CAPSENSE_CDAC_FINE_MODE_AUTO_MASK))
        {
            advancedSearchFlag = CY_CAPSENSE_ENABLE;
        }
    #endif

    /* Dummy scan */
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
        if (CY_CAPSENSE_CSX_GROUP == context->ptrWdConfig[widgetId].senseMethod)
        {
            calibrationStatus |= Cy_CapSense_ScanWidgetInternalCPU(widgetId, context);
        }
    #endif

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN)
        if (CY_CAPSENSE_CSD_GROUP == context->ptrWdConfig[widgetId].senseMethod)
        {
            /* Set CSD scan flag */
            csdScanEn = CY_CAPSENSE_ENABLE;
        }
    #endif

    rawTarget = Cy_CapSense_CalculateRawTarget(widgetId, rowFlag, context);
    *cdacPtr = 0u;

    while (cdacMask != 0u)
    {
        *cdacPtr |= (uint8_t)cdacMask;
        Cy_CapSense_SetWidgetFrameRefCdacCodes(widgetId, context);

        calibrationStatus |= Cy_CapSense_ScanWidgetInternalCPU(widgetId, context);
        Cy_CapSense_PreProcessWidget(widgetId, context);

        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
            if (CY_CAPSENSE_MPSC_MIN_ORDER <= context->ptrWdConfig[widgetId].mpOrder)
            {
                /* Find maximum capacitance across sensors in widget */
                minRaw = Cy_CapSense_MaxRawSearch(widgetId, rowFlag, context);
            }
            else
            {
                /* Find minimal capacitance across sensors in widget */
                minRaw = Cy_CapSense_MinRawSearch(widgetId, rowFlag, context);
            }
        #else
            /* Find minimal capacitance across sensors in widget */
            minRaw = Cy_CapSense_MinRawSearch(widgetId, rowFlag, context);
        #endif

        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_REF_AUTO_EN)
            if (CY_CAPSENSE_DISABLE != advancedSearchFlag)
            {
                tmpRaw = Cy_CapSense_CalculateAbsDiff(minRaw, rawTarget);
                if (tmpRaw <= minRawAbs)
                {
                    minRawAbs = tmpRaw;
                    minRawCode = *cdacPtr;
                }
            }
        #endif

        if (((csdScanEn == CY_CAPSENSE_ENABLE) && (minRaw < rawTarget)) ||
            ((csdScanEn == CY_CAPSENSE_DISABLE) && (minRaw >= rawTarget)))
        {
            *cdacPtr  &= (uint8_t)~cdacMask;
        }
        cdacMask >>= 1u;
    }

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_REF_AUTO_EN)
        if (CY_CAPSENSE_DISABLE != advancedSearchFlag)
        {
            *cdacPtr = minRawCode;
        }
    #endif

    return calibrationStatus;
}


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_REF_AUTO_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_CalibrateRefCdac
****************************************************************************//**
*
* The internal function that performs the reference CDAC successive
* approximation seek for the specified widget with compensation CDAC disabled.
*
* The function performs up to 9 scans of the slots in specified widget in the CPU
* driven scan mode to seek for a minimal reference CDAC value needed to match
* count target.
*
* The function usage is limited by the CapDAC auto-calibration.
*
* \note
* This function is available only
* for the fifth-generation low power CAPSENSE&trade;.
*
* \param widgetId
* The widget ID scans will be done for.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS   - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_CALIBRATION_FAIL - The calibration is failed due to
*                                  the issues with scanning (either
*                                  watchdog timer, interrupt breaking, etc.).
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_CalibrateRefCdac(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t calibrationStatus = CY_CAPSENSE_STATUS_SUCCESS;
    cy_stc_capsense_widget_context_t * ptrWdCxt = &context->ptrWdContext[widgetId];

    calibrationStatus |= Cy_CapSense_CdacSuccessAppr(widgetId, CY_CAPSENSE_ROW_SNS_CALIBRATION, CY_CAPSENSE_CAL_REF_CDAC_MIDDLE_CODE, &ptrWdCxt->cdacRef, context);

    #if ((CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_MATRIX_EN) || (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_TOUCHPAD_EN))
        if ((CY_CAPSENSE_CSD_GROUP == context->ptrWdConfig[widgetId].senseMethod) &&
            (((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == context->ptrWdConfig[widgetId].wdType) ||
             ((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == context->ptrWdConfig[widgetId].wdType)))
        {
            calibrationStatus |= Cy_CapSense_CdacSuccessAppr(widgetId, CY_CAPSENSE_COL_SNS_CALIBRATION, CY_CAPSENSE_CAL_REF_CDAC_MIDDLE_CODE, &ptrWdCxt->rowCdacRef, context);

            /* Align Reference CDAC rows and cols if enabled */
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_ROW_COL_ALIGN_EN)
                if (ptrWdCxt->cdacRef < ptrWdCxt->rowCdacRef)
                {
                    ptrWdCxt->cdacRef = ptrWdCxt->rowCdacRef;
                }
                ptrWdCxt->rowCdacRef = ptrWdCxt->cdacRef;
            #endif
        }
    #endif

    return calibrationStatus;
}
#endif


#if (CY_CAPSENSE_CDAC_FINE_USAGE)
/*******************************************************************************
* Function Name: Cy_CapSense_CalibrateFineCdac
****************************************************************************//**
*
* The internal function that performs the fine CDAC successive
* approximation seek for the specified widget with compensation CDAC disabled and
* fixed reference CDAC.
*
* The function performs up to 6 scans of the slots in specified widget in the CPU
* driven scan mode to seek for a minimal fine CDAC value needed to match
* count target.
*
* The function usage is limited by the CapDAC auto-calibration.
*
* \note
* This function is available only
* for the fifth-generation low power CAPSENSE&trade;.
*
* \param widgetId
* The widget ID scans will be done for.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS   - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_CALIBRATION_FAIL - The calibration is failed due to
*                                  the issues with scanning (either
*                                  watchdog timer, interrupt breaking, etc.).
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_CalibrateFineCdac(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t calibrationStatus = CY_CAPSENSE_STATUS_SUCCESS;
    cy_stc_capsense_widget_context_t * ptrWdCxt = &context->ptrWdContext[widgetId];

    calibrationStatus |= Cy_CapSense_CdacSuccessAppr(widgetId, CY_CAPSENSE_ROW_SNS_CALIBRATION, CY_CAPSENSE_CAL_FINE_CDAC_MIDDLE_CODE, &ptrWdCxt->cdacFine, context);

    #if ((CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_MATRIX_EN) || (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_TOUCHPAD_EN))
        if ((CY_CAPSENSE_CSD_GROUP == context->ptrWdConfig[widgetId].senseMethod) &&
            (((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == context->ptrWdConfig[widgetId].wdType) ||
             ((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == context->ptrWdConfig[widgetId].wdType)))
        {
            calibrationStatus |= Cy_CapSense_CdacSuccessAppr(widgetId, CY_CAPSENSE_COL_SNS_CALIBRATION, CY_CAPSENSE_CAL_FINE_CDAC_MIDDLE_CODE, &ptrWdCxt->rowCdacFine, context);

            /* Align Fine CDAC rows and cols if enabled */
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_ROW_COL_ALIGN_EN)
                if (ptrWdCxt->cdacFine < ptrWdCxt->rowCdacFine)
                {
                    ptrWdCxt->cdacFine = ptrWdCxt->rowCdacFine;
                }
                ptrWdCxt->rowCdacFine = ptrWdCxt->cdacFine;
            #endif
        }
    #endif

    return calibrationStatus;
}
#endif


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_COMP_DIV_AUTO_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_CalibrateCompDivider
****************************************************************************//**
*
* This function adjusts the compensation CDAC divider for the specified widget.
*
* The function scans all widget sensors with fixed reference CDAC and maximum
* compensation CDAC values starting from the compensation CDAC divider value
* equal to the snsClk divider (Kcomp = snsClkDiv / CompDiv = 1). If raw counts
* are over the raw target, the function decreases compensation CDAC divider
* value providing Kcomp as integer until raw counts are less than the raw
* target.
*
* The function does not consider multi-frequency feature. I.e. only the first
* (base) frequency channel is used.
*
* \param widgetId
* Specifies the desired widget ID.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS       - The operation is performed successfully.
*                                      The compensation CDAC divider is adjusted
*                                      for the specified widget.
* - CY_CAPSENSE_STATUS_CALIBRATION_FAIL - The compensation CDAC divider can not be
*                                         adjusted for the specified widget.
* - CY_CAPSENSE_STATUS_BAD_PARAM     - Invalid parameter(s).
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_CalibrateCompDivider(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t calibStatus = CY_CAPSENSE_STATUS_SUCCESS;
    uint32_t curSlotIndex;
    uint32_t numSlots;
    uint32_t snsOverflow = 0u;
    uint32_t snsIndex;
    uint32_t rawTemp;
    uint32_t frameType;
    uint32_t rawTarget;
    uint32_t j;

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
        uint32_t dummyScanFlagEn = 1u;
    #endif

    const cy_stc_capsense_widget_config_t * ptrWdCfg = &context->ptrWdConfig[widgetId];
    uint32_t compDivDefault = ptrWdCfg->ptrWdContext->snsClk;
    const cy_stc_capsense_scan_slot_t * ptrScanSlots;

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        if ((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E == ptrWdCfg->wdType)
        {
            numSlots = CY_CAPSENSE_SLOT_LP_COUNT;
            frameType = CY_CAPSENSE_SNS_FRAME_LOW_POWER;
            ptrScanSlots = context->ptrLpScanSlots;
        }
        else
    #endif
    {
        numSlots = CY_CAPSENSE_SLOT_COUNT;
        frameType = CY_CAPSENSE_SNS_FRAME_ACTIVE;
        ptrScanSlots = context->ptrScanSlots;
    }

    /* Sets Max CompCDAC Code within specified widget */
    for (j = 0u; j < ptrWdCfg->numSns; j++)
    {
        ptrWdCfg->ptrSnsContext[j].cdacComp = CY_CAPSENSE_CDAC_MAX_CODE;
    }
    Cy_CapSense_SetWidgetFrameCompCdacCode(widgetId, CY_CAPSENSE_CAL_MODE_COMP_CDAC_CODE_MAX, context);

    /* Defines initial value for Compensation Divider including rows and cols */
    #if ((CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_MATRIX_EN) ||\
         (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_TOUCHPAD_EN))
        if ((CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod) &&
            (((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == ptrWdCfg->wdType) ||
             ((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == ptrWdCfg->wdType)))
        {
            if (compDivDefault > ptrWdCfg->ptrWdContext->rowSnsClk)
            {
                compDivDefault = ptrWdCfg->ptrWdContext->rowSnsClk;
            }
        }
        else
        {
            /* Initializes unused rowSnsClk for further optimization */
            ptrWdCfg->ptrWdContext->rowSnsClk = ptrWdCfg->ptrWdContext->snsClk;
        }
    #else
        /* Initializes unused rowSnsClk for further optimization */
        ptrWdCfg->ptrWdContext->rowSnsClk = ptrWdCfg->ptrWdContext->snsClk;
    #endif

    rawTarget = Cy_CapSense_CalculateRawTarget(widgetId, CY_CAPSENSE_ROW_SNS_CALIBRATION, context);

    compDivDefault++;

    /*
     * Loop through all Compensation Divider values in descending order.
     *
     * Loop ends when CompDiv value equal 1 or Calibration fails.
     * Switches to the next iteration is done when kComp is not an integer
     * or calibration overflows.
     */
    do
    {
        /* Switches to the next possible divider */
        compDivDefault--;
        /* Checks if divider is valid */
        if (((ptrWdCfg->ptrWdContext->snsClk % compDivDefault) != 0u) ||
            ((ptrWdCfg->ptrWdContext->rowSnsClk % compDivDefault) != 0u))
        {
            continue;
        }

        ptrWdCfg->ptrWdContext->cdacCompDivider = (uint16_t)compDivDefault;
        Cy_CapSense_SetCompDivider(widgetId, context);

        snsOverflow = 0u;
        for (curSlotIndex = 0u; curSlotIndex < numSlots; curSlotIndex++)
        {
            /* Checks only the specified widget in the current slot */
            if (widgetId == ptrScanSlots[curSlotIndex].wdId)
            {
                #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
                    /* Dummy scan */
                    if ((0u != dummyScanFlagEn) && (CY_CAPSENSE_CSX_GROUP == ptrWdCfg->senseMethod))
                    {
                        calibStatus |= Cy_CapSense_ScanSlotInternalCPU(frameType, curSlotIndex, context);
                        dummyScanFlagEn = 0u;
                    }
                #endif

                calibStatus |= Cy_CapSense_ScanSlotInternalCPU(frameType, curSlotIndex, context);

                snsIndex = ptrScanSlots[curSlotIndex].snsId;
                Cy_CapSense_PreProcessSensor(widgetId, snsIndex, context);
                rawTemp = ptrWdCfg->ptrSnsContext[snsIndex].raw;

                if ((CY_CAPSENSE_CSX_GROUP == ptrWdCfg->senseMethod) ||
                    (CY_CAPSENSE_ISX_GROUP == ptrWdCfg->senseMethod) ||
                    ((CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod) && (!(CY_CAPSENSE_MPSC_MIN_ORDER > ptrWdCfg->mpOrder))))
                {
                    if (rawTemp <= rawTarget)
                    {
                        snsOverflow = 1u;
                    }
                }
                else
                {
                    if (rawTemp > rawTarget)
                    {
                        snsOverflow = 1u;
                    }
                }

                if (0u != snsOverflow)
                {
                    /* If at least one sensor of the specified widget has
                     * Raw Count too high (no enough compensation level)
                     * then switch to the next compensation divider value.
                     */
                    break;
                }
            }
        }
        /* Finish the searching if no overflow across all sensors of the specified widget */
        if (0u == snsOverflow)
        {
            break;
        }
    } while ((compDivDefault > CY_CAPSENSE_CDAC_COMP_DIV_MIN_MSCLP) &&
             (CY_CAPSENSE_STATUS_SUCCESS == calibStatus));

    return calibStatus;
}
#endif


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_COMP_AUTO_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_CalibrateCompCdac
****************************************************************************//**
*
* The internal function that performs the compensation CDAC successive
* approximation seek for the specified widget with fixed reference CDAC and
* fixed compensation divider.
*
* The function performs up to 9 scans of the slots in specified widget in the CPU
* driven scan mode to seek for a minimal compensation CDAC value needed to match
* count target.
*
* The function usage is limited by the CapDAC auto-calibration.
*
* \note
* This function is available only
* for the fifth-generation low power CAPSENSE&trade;.
*
* \param widgetId
* The widget ID scans will be done for.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS   - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_CALIBRATION_FAIL - The calibration is failed due to
*                                  the issues with scanning (either
*                                  watchdog timer, interrupt breaking, etc.).
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_CalibrateCompCdac(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t calibStatus = CY_CAPSENSE_STATUS_SUCCESS;
    cy_stc_capsense_widget_config_t const * ptrWdCfg = &context->ptrWdConfig[widgetId];
    cy_stc_capsense_sensor_context_t * ptrSnsCxt;
    uint8_t cdacMask;
    uint32_t rawTarget;
    uint32_t snsIndex;
    uint32_t sensingGroup = context->ptrWdConfig[widgetId].senseMethod;
    uint32_t csdScanEn = CY_CAPSENSE_DISABLE;

    /* Calculate raw target for current sensing method */
    rawTarget = Cy_CapSense_CalculateRawTarget(widgetId, CY_CAPSENSE_ROW_SNS_CALIBRATION, context);

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
        /* Dummy scan */
        if (CY_CAPSENSE_CSX_GROUP == sensingGroup)
        {
            calibStatus |= Cy_CapSense_ScanWidgetInternalCPU(widgetId, context);
        }
    #endif

    for (snsIndex = 0u; snsIndex < (uint32_t)ptrWdCfg->numSns; snsIndex++)
    {
        #if ((CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_MATRIX_EN) || (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_TOUCHPAD_EN))
            if ((CY_CAPSENSE_CSD_GROUP == sensingGroup) &&
                (ptrWdCfg->numCols <= snsIndex) &&
                (((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == ptrWdCfg->wdType) ||
                ((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == ptrWdCfg->wdType)))
            {
                rawTarget = Cy_CapSense_CalculateRawTarget(widgetId, CY_CAPSENSE_COL_SNS_CALIBRATION, context);
            }
        #endif

        if (CY_CAPSENSE_CSD_GROUP == sensingGroup)
        {
            /* Set CSD scan flag */
            csdScanEn = CY_CAPSENSE_ENABLE;
            /* Clear flag as compensation CapDAC code for MPSC widgets should be increased unlike reference CapDAC */
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
                if (CY_CAPSENSE_MPSC_MIN_ORDER <= ptrWdCfg->mpOrder)
                {
                    csdScanEn = CY_CAPSENSE_DISABLE;
                }
            #endif
        }

        cdacMask = (uint8_t)CY_CAPSENSE_CAL_COMP_CDAC_MIDDLE_CODE;
        ptrSnsCxt = &ptrWdCfg->ptrSnsContext[snsIndex];
        ptrSnsCxt->cdacComp = 0u;
        Cy_CapSense_SetWidgetFrameCompCdacCode(widgetId, CY_CAPSENSE_CAL_MODE_COMP_CDAC_CODE_MIN, context);

        while (0u != cdacMask)
        {
            ptrSnsCxt->cdacComp |= cdacMask;
            Cy_CapSense_SetWidgetFrameCompCdacCode(widgetId, CY_CAPSENSE_CAL_MODE_COMP_CDAC_CODE_VAL, context);

            calibStatus |= Cy_CapSense_ScanWidgetInternalCPU(widgetId, context);
            Cy_CapSense_PreProcessWidget(widgetId, context);

            if (calibStatus == CY_CAPSENSE_STATUS_SUCCESS)
            {
                if (((csdScanEn == CY_CAPSENSE_ENABLE) && ((uint32_t)ptrSnsCxt->raw < rawTarget)) ||
                    ((csdScanEn == CY_CAPSENSE_DISABLE) && ((uint32_t)ptrSnsCxt->raw >= rawTarget)))
                {
                    ptrSnsCxt->cdacComp &= ~cdacMask;
                }

                cdacMask >>= 1u;
            }
            else
            {
                break;
            }
        }
    }

    return calibStatus;
}
#endif


#if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_REF_AUTO_EN)      || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_FINE_AUTO_EN)     || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_COMP_DIV_AUTO_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_COMP_AUTO_EN))
/*******************************************************************************
* Function Name: Cy_CapSense_CalculateRawTarget
****************************************************************************//**
*
* The internal function that calculates the auto-calibration target in
* raw counts.
*
* \note
* This function is available only
* for the fifth-generation low power CAPSENSE&trade;.
*
* \param widgetId
* The widget ID calculation will be done for.
*
* \param rowFlag
* The flag for a row/column raw target calculation.
* CY_CAPSENSE_ROW_SNS_CALIBRATION - target calculation performed for rows.
* CY_CAPSENSE_COL_SNS_CALIBRATION - target calculation performed for columns.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the raw count target for widget sensing method.
*
*******************************************************************************/
uint32_t Cy_CapSense_CalculateRawTarget(
                uint32_t widgetId,
                uint32_t rowFlag,
                cy_stc_capsense_context_t * context)
{
    uint32_t rawTarget;

    /* Calculate raw target for current sensing method */
    switch (context->ptrWdConfig[widgetId].senseMethod)
    {
        #if (CY_CAPSENSE_CSD_CDAC_CALIBRATION_USAGE)
            case CY_CAPSENSE_CSD_GROUP:
                rawTarget = context->ptrInternalContext->intrCsdRawTarget;
                break;
        #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN) */

        #if (CY_CAPSENSE_CSX_CDAC_CALIBRATION_USAGE)
            case CY_CAPSENSE_CSX_GROUP:
                rawTarget = context->ptrInternalContext->intrCsxRawTarget;
                break;
        #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN) */

        #if (CY_CAPSENSE_ISX_CDAC_CALIBRATION_USAGE)
            case CY_CAPSENSE_ISX_GROUP:
                rawTarget = context->ptrInternalContext->intrIsxRawTarget;
                break;
        #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN) */

        default:
            /* Widget type is not valid */
            rawTarget = 0u;
            break;
    }

    if (CY_CAPSENSE_ROW_SNS_CALIBRATION == rowFlag)
    {
        rawTarget *= context->ptrWdContext[widgetId].maxRawCount;
    }
    #if ((CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_MATRIX_EN) || (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_TOUCHPAD_EN))
        else
        {
            rawTarget *= context->ptrWdContext[widgetId].maxRawCountRow;
        }
    #endif

    rawTarget /= CY_CAPSENSE_PERCENTAGE_100;

    return rawTarget;
}
#endif


/*******************************************************************************
* Function Name: Cy_CapSense_ScanSlotInternalCPU
****************************************************************************//**
*
* Initiates the blocking scan of specified slot in CPU mode.
*
* This function initiates a scan of specified slot in the CPU driven scan
* mode, waits for operation completion and then exits.
* Use of this function is limited to the CapDAC auto-calibration.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param snsFrameType
* The Sensor Frame type:
* * CY_CAPSENSE_SNS_FRAME_ACTIVE     - Sensor frame for Active slot
* * CY_CAPSENSE_SNS_FRAME_LOW_POWER  - Sensor frame for Low Power slot
*
* \param scanSlotId
* The slot ID scans will be done for.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS   - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM - The input parameter is invalid.
* - CY_CAPSENSE_STATUS_CALIBRATION_FAIL - The calibration is failed due to
*                                  the issues with scanning (either
*                                  watchdog timer, interrupt breaking, etc.).
*
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ScanSlotInternalCPU(
                uint32_t snsFrameType,
                uint32_t scanSlotId,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t result = CY_CAPSENSE_STATUS_SUCCESS;
    cy_stc_capsense_internal_context_t * ptrIntrCxt = context->ptrInternalContext;
    const cy_stc_capsense_scan_slot_t * ptrScanSlots;
    MSCLP_Type * ptrHwBase = context->ptrCommonConfig->ptrChConfig->ptrHwBase;
    cy_stc_capsense_sensor_context_t * ptrSnsCxt;
    uint32_t * ptrSensorFrame;
    uint32_t tmpRawCount;
    uint32_t wdIndex;
    uint32_t snsIndex;
    uint32_t watchdog;
    const cy_stc_capsense_widget_config_t * ptrWdCfg;

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        if (snsFrameType == CY_CAPSENSE_SNS_FRAME_LOW_POWER)
        {
            ptrSensorFrame = &context->ptrSensorFrameLpContext[(scanSlotId * CY_MSCLP_11_SNS_REGS) + CY_CAPSENSE_FRM_LP_SNS_SW_SEL_CSW_LO_MASK2_INDEX];
            ptrScanSlots = context->ptrLpScanSlots;
        }
        else
        {
            ptrSensorFrame = &context->ptrSensorFrameContext[scanSlotId * CY_CAPSENSE_SENSOR_FRAME_SIZE];
            ptrScanSlots = context->ptrScanSlots;
        }
    #else
        ptrSensorFrame = &context->ptrSensorFrameContext[scanSlotId * CY_CAPSENSE_SENSOR_FRAME_SIZE];
        ptrScanSlots = context->ptrScanSlots;
        (void) snsFrameType;
    #endif

    wdIndex = ptrScanSlots[scanSlotId].wdId;
    snsIndex = ptrScanSlots[scanSlotId].snsId;
    ptrWdCfg = &context->ptrWdConfig[wdIndex];

    if ((CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod) &&
        (CY_CAPSENSE_MPSC_MIN_ORDER <= ptrWdCfg->mpOrder))
    {
        result = Cy_CapSense_SwitchHwConfiguration(CY_CAPSENSE_HW_CONFIG_MPSC_SCANNING, context);
    }
    else
    {
        result = Cy_CapSense_SwitchHwConfiguration(CY_CAPSENSE_HW_CONFIG_REGULAR_SCANNING, context);
    }

    Cy_CapSense_SetupCpuOperatingMode(context);

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LIQUID_LEVEL_FOAM_REJECTION_EN)
        if (0u != (ptrWdCfg->centroidConfig & CY_CAPSENSE_LLW_FOAM_EN_MASK))
        {
        /* Configures Foam rejection scan */
        context->ptrCommonConfig->ptrChConfig->ptrHwBase->SENSE_DUTY_CTL = 
                ((CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_WIDTH_SEL_FOAM << MSCLP_SENSE_DUTY_CTL_PHASE_WIDTH_SEL_Pos) | 
                 (CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_CYCLES_FOAM << MSCLP_SENSE_DUTY_CTL_PHASE_SHIFT_CYCLES_Pos) | 
                 ((uint32_t)ptrWdCfg->ptrWdContext->sigPFC << MSCLP_SENSE_DUTY_CTL_PHASE_WIDTH_Pos));
        }
    #endif

    /* Initialize internal context */
    ptrIntrCxt->currentSlotIndex = (uint16_t)scanSlotId;
    ptrIntrCxt->endSlotIndex = (uint16_t)scanSlotId;

    /* Set sensor config registers (frame) */
    Cy_CapSense_StartCpuScan(ptrSensorFrame, context);
    watchdog = Cy_CapSense_GetScanWatchdogTime(wdIndex, scanSlotId, context);
    watchdog = Cy_CapSense_WaitEndOfCpuScan(watchdog, context);

    /* Check if the watchdog timeout happened */
    if (0u == watchdog)
    {
        result = CY_CAPSENSE_STATUS_CALIBRATION_FAIL;
    }

    if (result == CY_CAPSENSE_STATUS_SUCCESS)
    {
        /* Read raw counts */
        tmpRawCount = ptrHwBase->SNS.RESULT_FIFO_RD;

        ptrSnsCxt = &context->ptrWdConfig[wdIndex].ptrSnsContext[snsIndex];
        ptrSnsCxt->status &= (uint8_t)~CY_CAPSENSE_SNS_OVERFLOW_MASK;

        if (MSCLP_SNS_RESULT_FIFO_RD_OVERFLOW_Msk == (tmpRawCount & MSCLP_SNS_RESULT_FIFO_RD_OVERFLOW_Msk))
        {
            ptrSnsCxt->status |= CY_CAPSENSE_SNS_OVERFLOW_MASK;
        }
        tmpRawCount &= MSCLP_SNS_RESULT_FIFO_RD_RAW_COUNT_Msk;

        #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN) && \
             ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) || (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN)))

            if (0u == (context->ptrCommonContext->status & CY_CAPSENSE_MW_STATE_SMARTSENSE_MASK))
            {
                if ((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E == ptrWdCfg->wdType)
                {
                    if ((CY_CAPSENSE_CSX_GROUP == ptrWdCfg->senseMethod) ||
                        (CY_CAPSENSE_ISX_GROUP == ptrWdCfg->senseMethod))
                    {
                        /* Limit raw counts */
                        if (tmpRawCount < ptrWdCfg->ptrWdContext->maxRawCount)
                        {
                            /* Invert raw counts for CSX/ISX widgets */
                            tmpRawCount = (ptrWdCfg->ptrWdContext->maxRawCount - tmpRawCount);
                        }
                        else
                        {
                            tmpRawCount = 0u;
                        }
                    }
                }
            }
        #endif
        ptrSnsCxt->raw = (uint16_t)tmpRawCount;
    }

    /* Disable HW IP */
    ptrHwBase->CTL &= (~MSCLP_CTL_ENABLED_Msk);

    return result;
}
#endif /* ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CALIBRATION_EN) || \
           (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CALIBRATION_EN) || \
           (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CALIBRATION_EN)) */


#if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CALIBRATION_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CALIBRATION_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CALIBRATION_EN))
/*******************************************************************************
* Function Name: Cy_CapSense_ScanWidgetInternalCPU
****************************************************************************//**
*
* Initiates the blocking scan of specified widget in CPU mode.
*
* This function initiates a scan of specified widget in the CPU driven scan
* mode, waits for operation completion and then exits.
* Use of this function is limited to the CapDAC auto-calibration.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param widgetId
* The widget ID scans will be done for.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS   - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM - The input parameter is invalid.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ScanWidgetInternalCPU(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t result = CY_CAPSENSE_STATUS_SUCCESS;
    cy_stc_capsense_widget_config_t const * ptrWdCfg = &context->ptrWdConfig[widgetId];
    uint32_t currSlot;
    uint32_t snsFrameType = CY_CAPSENSE_SNS_FRAME_ACTIVE;

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        if ((ptrWdCfg->wdType == (uint8_t)CY_CAPSENSE_WD_LOW_POWER_E))
        {
            snsFrameType = CY_CAPSENSE_SNS_FRAME_LOW_POWER;
        }
    #endif

    for (currSlot = ptrWdCfg->firstSlotId; currSlot < ((uint32_t)ptrWdCfg->firstSlotId + ptrWdCfg->numSlots); currSlot++)
    {
        result |= Cy_CapSense_ScanSlotInternalCPU(snsFrameType, currSlot, context);
    }

    return result;
}
#endif /* ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CALIBRATION_EN) || \
           (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CALIBRATION_EN) || \
           (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CALIBRATION_EN)) */


/*******************************************************************************
* Function Name: Cy_CapSense_WatchdogCyclesNum
****************************************************************************//**
*
* Converts the specified time into number of CPU cycles.
*
* \param desiredTimeUs
* The time (delay) specified in us.
*
* \param cpuFreqMHz
* The CPU frequency in MHz.
*
* \param cyclesPerLoop
* The number of cycles per a loop.
*
*******************************************************************************/
uint32_t Cy_CapSense_WatchdogCyclesNum(
                uint32_t desiredTimeUs,
                uint32_t cpuFreqMHz,
                uint32_t cyclesPerLoop)
{
    uint32_t retVal;

    if (0uL != cyclesPerLoop)
    {
        retVal = (desiredTimeUs * cpuFreqMHz) / cyclesPerLoop;
    }
    else
    {
        retVal = 0xFFFFFFFFuL;
    }

    return retVal;
}


/*******************************************************************************
* Function Name: Cy_CapSense_SsInitialize
****************************************************************************//**
*
* Performs the hardware and firmware initialization required for proper operation
* of the CAPSENSE&trade; middleware. This function is called from
* the Cy_CapSense_Init() prior to calling any other function of the middleware.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return status
* Returns the status of the operation (different statuses can be combined):
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed
*                                         successfully.
* - CY_CAPSENSE_STATUS_BAD_CLOCK_CONFIG - Sense Clock Divider is out
*                                         of the valid range
*                                         for the specified Clock source
*                                         configuration.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - At least one of input parameters is
*                                         not valid.
* - CY_CAPSENSE_STATUS_HW_BUSY          - The MSCLP HW block is busy and cannot be
*                                         configured.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_SsInitialize(cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_SUCCESS;
    const cy_stc_capsense_common_config_t * ptrCommonCfg = context->ptrCommonConfig;
    uint32_t i;

    capStatus |= Cy_CapSense_InitializeSourceSenseClk(context);

    /* Initialize the MSCLP channel for scan */
    /* Reset the sense method */
    context->ptrActiveScanSns->currentSenseMethod = CY_CAPSENSE_UNDEFINED_GROUP;
    context->ptrInternalContext->scanSingleSlot = CY_CAPSENSE_SCAN_MULTIPLE_SLOT;

    /* Configure inactive sensor states */
    context->ptrInternalContext->intrCsdInactSnsConn = ptrCommonCfg->csdInactiveSnsConnection;
    context->ptrInternalContext->intrCsxInactSnsConn = ptrCommonCfg->csxInactiveSnsConnection;
    context->ptrInternalContext->intrIsxInactSnsConn = ptrCommonCfg->isxInactiveSnsConnection;

    /* Generate base frame configurations for all enabled MSCLP channels */
    capStatus |= Cy_CapSense_GenerateBaseConfig(context);

    /* Generates sensor frame configuration */
    Cy_CapSense_GenerateAllSensorConfig(CY_CAPSENSE_SNS_FRAME_ACTIVE, context);

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        Cy_CapSense_GenerateAllSensorConfig(CY_CAPSENSE_SNS_FRAME_LOW_POWER, context);
    #endif /* CY_CAPSENSE_LP_EN */

    /* Assign the ISR for scan */
    context->ptrInternalContext->ptrISRCallback = &Cy_CapSense_ScanISR;

    /* Calculate and store wake-on-touch timer value */
    context->ptrInternalContext->wotScanIntervalCycles =
        Cy_CapSense_MsclpTimerCalcCycles(context->ptrInternalContext->wotScanInterval, context);

    /* Check if an external start is enabled */
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_EXT_FRM_START_EN)
        Cy_GPIO_Pin_FastInit(CY_MSCLP0_EXT_FRM_START_PORT, CY_MSCLP0_EXT_FRM_START_PIN,
                             CY_GPIO_DM_HIGHZ, 0u, HSIOM_SEL_DS_1);
    #endif /* (CY_CAPSENSE_DISABLE != CY_CAPSENSE_EXT_FRM_START_EN) */

    /* Call user's callback function if it is registered */
    if (NULL != context->ptrInternalContext->ptrEODsInitCallback)
    {
        context->ptrInternalContext->ptrEODsInitCallback(context);
    }

    /* Resetting the HW configuration in order to trigger the base frame initialization in scope of the
     * next  Cy_CapSense_SwitchHwConfiguration() function call with the desired HW configuration.
     */
    if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
    {
        capStatus |= Cy_CapSense_SwitchHwConfiguration(CY_CAPSENSE_HW_CONFIG_CAPTURED_DEFAULT, context);
    }

    if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
    {
        capStatus |= Cy_CapSense_SwitchHwConfiguration(CY_CAPSENSE_HW_CONFIG_REGULAR_SCANNING, context);
    }

    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN) && \
         (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC_RATE_MODE_AUTO_EN))
        capStatus |= Cy_CapSense_InitializeCic2Rate(context);
    #endif

    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN) && \
         (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_AUTO_EN))
        capStatus |= Cy_CapSense_InitializeCic2Shift(context);
    #endif

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_AUTO_DITHER_EN)
        if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
        {
            capStatus = Cy_CapSense_CdacDitherScaleCalc(context);
        }
    #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_AUTO_DITHER_EN) */

    /* Find maximum raw count for each widget */
    for (i = 0u; i < CY_CAPSENSE_TOTAL_WIDGET_COUNT; i++)
    {
        if (0u != Cy_CapSense_IsWidgetEnabled(i, context))
        {
            capStatus |= Cy_CapSense_InitializeMaxRaw(i, context);

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LIQUID_LEVEL_FOAM_REJECTION_EN)
                context->ptrWdConfig[i].ptrWdContext->sigPFC = context->ptrWdConfig[i].foamCoefficient;
            #endif
        }
    }

    return capStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_InterruptHandler_V3Lp
****************************************************************************//**
*
* Implements the interrupt service routine (ISR) for the Fifth generation low power
* CAPSENSE&trade;.
*
* At the end of the whole frame scan, the MSCLP HW block generates interrupts
* (for the frame while regular widget scanning and for the time-out number of frames
* or for signal detection while low power widget scanning). The ISR distinguishes
* these interrupts and reads raw counts into the Data structure respectively, and
* then exits if no other slots to scan left,
* Otherwise - starts a scan for the next set of regular sensors. The HW MRSS is turned
* off after the last regular widget scan.
*
* The CAPSENSE&trade; middleware uses this interrupt to implement the
* non-blocking sensor scan method, in which only the first frame scan is
* initiated in the interrupt service routine as soon as the current frame scan
* completes. The interrupt service routine is implemented
* as a part of the CAPSENSE&trade; middleware.
*
* The CAPSENSE&trade; middleware does not initialize or modify the priority
* of interrupts - instead, the application program
* configures an MSCLP interrupt and assigns the interrupt vector to
* the Cy_CapSense_InterruptHandler() function. For details, refer to the function
* usage example.
*
* \note
* This function is available only for the fifth-generation low power
* CAPSENSE&trade;.
*
* The call of the End Of Scan callback (for details, see the \ref group_capsense_callbacks
* section) is the part of the Cy_CapSense_InterruptHandler() routine
* and that call lengthens its execution. Such a callback lengthens the MSCLP ISR execution
* in the case of a direct call of the Cy_CapSense_InterruptHandler() function
* from a MSCLP ISR.
*
* \param base
* The pointer to the base register address of the MSCLP HW block.
* This argument is kept for uniformity and backward compatibility
* and is not used. The function can be called with value NULL.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \funcusage
*
* An example of the ISR initialization:
*
* The CapSense_ISR_cfg variable should be declared by the application
* program according to the examples below:<br>
* For Core CM0+:
* \snippet capsense/snippet/main.c snippet_m0p_capsense_interrupt_source_declaration
*
* The CAPSENSE&trade; interrupt handler should be defined by the application program
* according to the example below:
* \snippet capsense/snippet/main.c snippet_Cy_CapSense_IntHandler
*
* Then, the application program configures and enables the interrupt
* for each MSCLP HW block between calls of the Cy_CapSense_Init() and
* Cy_CapSense_Enable() functions:
* \snippet capsense/snippet/main.c snippet_Cy_CapSense_Initialization
*
*******************************************************************************/
void Cy_CapSense_InterruptHandler_V3Lp(const MSCLP_Type * base, cy_stc_capsense_context_t * context)
{
    (void)base;
    context->ptrInternalContext->ptrISRCallback((void *)context);
}


/*******************************************************************************
* Function Name: Cy_CapSense_ScanISR
****************************************************************************//**
*
* This is an internal ISR function to handle the MSCLP sensing
* in AS_MS and LP_AoS operating modes.
*
* \param capsenseContext
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_ScanISR(void * capsenseContext)
{
    cy_stc_capsense_context_t * cxt = (cy_stc_capsense_context_t *)capsenseContext;
    MSCLP_Type * ptrHwBase = cxt->ptrCommonConfig->ptrChConfig->ptrHwBase;
    cy_stc_capsense_internal_context_t * ptrIntrCxt = cxt->ptrInternalContext;
    uint32_t numScanSlots;

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        /* Check for interrupt source: MSCLP_INTR_LP_FRAME_Msk for ACTIVE widget scan */
        if (MSCLP_INTR_LP_FRAME_Msk != (ptrHwBase->INTR_LP & ptrHwBase->INTR_LP_MASK & MSCLP_INTR_LP_FRAME_Msk))
        {
            /* It was the low power scan - check if a signal detection had occurred */
            if (MSCLP_INTR_LP_SIG_DET_Msk == (ptrHwBase->INTR_LP & MSCLP_INTR_LP_SIG_DET_Msk))
            {
                cxt->ptrCommonContext->status |= (uint32_t)CY_CAPSENSE_MW_STATE_LP_ACTIVE_MASK;
            }

            /* Read the last low power frame raw counts */
            if ((cxt->ptrCommonContext->lpDataSt & CY_CAPSENSE_LP_PROCESS_ENABLED_MASK) != 0u)
            {
                Cy_CapSense_TransferLpRawCounts(ptrIntrCxt->currentSlotIndex, ptrIntrCxt->numSlots, cxt);

                /* Mark completion of low power scan cycle */
                cxt->ptrCommonContext->lpScanCounter++;
            }

            /* Disable HW IP */
            ptrHwBase->CTL &= (~MSCLP_CTL_ENABLED_Msk);

            /* Clear all pending interrupts of the MSCLP HW block */
            ptrHwBase->INTR_LP = CY_CAPSENSE_MSCLP_INTR_LP_ALL_MSK;
            (void)ptrHwBase->INTR_LP;

            /* Stop the MRSS to save power */
            ptrHwBase->MRSS_CMD = MSCLP_MRSS_CMD_MRSS_STOP_Msk;

            Cy_CapSense_ClrBusyFlags(cxt);
        }
        else
    #endif
    {
        /* Clear all pending interrupts of the MSCLP HW block */
        ptrHwBase->INTR_LP = CY_CAPSENSE_MSCLP_INTR_LP_ALL_MSK;
        (void)ptrHwBase->INTR_LP;

        /* Read the last ACTIVE frame raw counts */
        Cy_CapSense_TransferRawCounts(ptrIntrCxt->currentSlotIndex, ptrIntrCxt->numSlots, cxt);

        ptrIntrCxt->currentSlotIndex += ptrIntrCxt->numSlots;

        /* Check for the last slot with multiple slot scan, if not - start the next slot scan */
        if (ptrIntrCxt->currentSlotIndex <= ptrIntrCxt->endSlotIndex)
        {
            numScanSlots = (uint32_t)ptrIntrCxt->endSlotIndex - (uint32_t)ptrIntrCxt->currentSlotIndex + 1uL;

            /* Disable delay before next scan */
            ptrHwBase->AOS_CTL &= ~MSCLP_AOS_CTL_WAKEUP_TIMER_Msk;

            /* Clear the first sub-frame flag */
            ptrIntrCxt->firstActSubFrame = CY_CAPSENSE_DISABLE;

            Cy_CapSense_ScanSlotsInternal(ptrIntrCxt->currentSlotIndex, numScanSlots, cxt);
        }
        else
        {
            /* Disable HW IP to allow MRSS operations */
            ptrHwBase->CTL &= (~MSCLP_CTL_ENABLED_Msk);

            /* Stop the MRSS to save power */
            ptrHwBase->MRSS_CMD = MSCLP_MRSS_CMD_MRSS_STOP_Msk;

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LIQUID_LEVEL_FOAM_REJECTION_EN)
                /* Restores config for regular scan */
                cxt->ptrCommonConfig->ptrChConfig->ptrHwBase->SENSE_DUTY_CTL = 
                    ((CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_WIDTH_SEL << MSCLP_SENSE_DUTY_CTL_PHASE_WIDTH_SEL_Pos) | 
                     (CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_CYCLES << MSCLP_SENSE_DUTY_CTL_PHASE_SHIFT_CYCLES_Pos) | 
                     (CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_WIDTH << MSCLP_SENSE_DUTY_CTL_PHASE_WIDTH_Pos));
            #endif

            /* Mark completion of active scan cycle */
            cxt->ptrCommonContext->scanCounter++;

            Cy_CapSense_ClrBusyFlags(cxt);
        }
    }
}


/*******************************************************************************
* Function Name: Cy_CapSense_SetCmodInDesiredState
****************************************************************************//**
*
* Sets all available MSCLP Cmod pins into a desired state.
*
The default state to provide the fifth generation low power CAPSENSE&trade; operation is:
* - HSIOM   - Disconnected, the GPIO mode.
* - DM      - High-Z Analog, Input off drive mode.
* - MSC_ANA - Enabled.
*
* Do not call this function directly from the application program.
*
* \param desiredDriveMode
* Specifies the desired pin control port (PC) configuration.
*
* \param desiredHsiom
* Specifies the desired pin HSIOM state.
*
* \param desiredMscCtrl
* Specifies the desired (MSC_ANA) control status of the IO port analog signaling by the MSC.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_SetCmodInDesiredState(
                uint32_t desiredDriveMode,
                en_hsiom_sel_t desiredHsiom,
                uint32_t desiredMscCtrl,
                const cy_stc_capsense_context_t * context)
{
    Cy_CapSense_SsConfigPinRegisters(
    context->ptrCommonConfig->ptrChConfig->portCmod1,
    (uint32_t)context->ptrCommonConfig->ptrChConfig->pinCmod1,
    desiredDriveMode, desiredHsiom, desiredMscCtrl);

    Cy_CapSense_SsConfigPinRegisters(
    context->ptrCommonConfig->ptrChConfig->portCmod2,
    (uint32_t)context->ptrCommonConfig->ptrChConfig->pinCmod2,
    desiredDriveMode, desiredHsiom, desiredMscCtrl);
}


/*******************************************************************************
* Function Name: Cy_CapSense_SetIOsInDesiredState
****************************************************************************//**
*
* Sets all CAPSENSE&trade; pins into a desired state.
*
* The default state to provide the fifth generation low power CAPSENSE&trade; operation is:
* - HSIOM   - Disconnected, the GPIO mode.
* - DM      - Strong drive.
* - MSC_ANA - Enabled.
* - State   - Zero.
*
* Do not call this function directly from the application program.
*
* \param desiredDriveMode
* Specifies the desired pin control port (PC) configuration.
*
* \param desiredHsiom
* Specifies the desired pin HSIOM state.
*
* \param desiredPinOutput
* Specifies the desired pin output data register (DR) state.
*
* \param desiredMscCtrl
* Specifies the desired (MSC_ANA) control status of the IO port analog signaling by the MSC.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_SetIOsInDesiredState(
                uint32_t desiredDriveMode,
                en_hsiom_sel_t desiredHsiom,
                uint32_t desiredPinOutput,
                uint32_t desiredMscCtrl,
                const cy_stc_capsense_context_t * context)
{
    uint32_t loopIndex;
    const cy_stc_capsense_pin_config_t * ptrPinCfg = context->ptrPinConfig;

    /* Loop through all electrodes */
    for (loopIndex = 0u; loopIndex < context->ptrCommonConfig->numPin; loopIndex++)
    {
        Cy_CapSense_SsConfigPinRegisters(ptrPinCfg->pcPtr, (uint32_t)ptrPinCfg->pinNumber,
            desiredDriveMode, desiredHsiom, desiredMscCtrl);

        if (0u != desiredPinOutput)
        {
            Cy_GPIO_Set(ptrPinCfg->pcPtr, (uint32_t)ptrPinCfg->pinNumber);
        }
        else
        {
            Cy_GPIO_Clr(ptrPinCfg->pcPtr, (uint32_t)ptrPinCfg->pinNumber);
        }

        /* Get next electrode */
        ptrPinCfg++;
    }
}


/*******************************************************************************
* Function Name: Cy_CapSense_SetShieldPinsInDesiredState
****************************************************************************//**
*
* Sets all shield pins into a default state.
*
* Do not call this function directly from the application program.
*
* \param desiredDriveMode
* Specifies the desired pin control port (PC) configuration.
*
* \param desiredHsiom
* Specifies the desired pin HSIOM state.
*
* \param desiredMscCtrl
* Specifies the desired (MSC_ANA) control status of the IO port analog signaling by the MSC.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_SetShieldPinsInDesiredState(
                uint32_t desiredDriveMode,
                en_hsiom_sel_t desiredHsiom,
                uint32_t desiredMscCtrl,
                const cy_stc_capsense_context_t * context)
{
    uint32_t loopIndex;
    const cy_stc_capsense_pin_config_t * ptrPinCfg = context->ptrShieldPinConfig;

    /* Loop through all shield electrodes */
    for (loopIndex = 0u; loopIndex < context->ptrCommonConfig->csdShieldNumPin; loopIndex++)
    {
        Cy_CapSense_SsConfigPinRegisters(ptrPinCfg->pcPtr, (uint32_t)ptrPinCfg->pinNumber,
            desiredDriveMode, desiredHsiom, desiredMscCtrl);

        Cy_GPIO_Clr(ptrPinCfg->pcPtr, (uint32_t)ptrPinCfg->pinNumber);
        ptrPinCfg++;
    }
}



/*******************************************************************************
* Function Name: Cy_CapSense_InitActivePtr
****************************************************************************//**
*
* Initializes active scan sensor structure with all available
* pointers for further faster access to widget/sensor parameters.
*
* \param widgetId
* Specifies the ID number of the widget. A macro for the widget ID can be found
* in the cycfg_capsense.h file defined as CY_CAPSENSE_<WIDGET_NAME>_WDGT_ID.
*
* \param sensorId
* Specifies the ID number of the sensor within the widget. A macro for the
* sensor ID within a specified widget can be found in the cycfg_capsense.h
* file defined as CY_CAPSENSE_<WIDGET_NAME>_SNS<SENSOR_NUMBER>_ID.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_InitActivePtr(
                uint32_t widgetId,
                uint32_t sensorId,
                cy_stc_capsense_context_t * context)
{
    Cy_CapSense_InitActivePtrWd(widgetId, context);
    Cy_CapSense_InitActivePtrSns(sensorId, context);
}


/*******************************************************************************
* Function Name: Cy_CapSense_InitActivePtrSns
****************************************************************************//**
*
* Initializes active scan sensor structure with pointers to sensor
* for further faster access to widget/sensor parameters.
*
* This function supposes that the Cy_CapSense_InitActivePtrWd() function
* is called before.
*
* \param sensorId
* Specifies the ID number of the sensor within the widget. A macro for the
* sensor ID within a specified widget can be found in the cycfg_capsense.h
* file defined as CY_CAPSENSE_<WIDGET_NAME>_SNS<SENSOR_NUMBER>_ID.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void  Cy_CapSense_InitActivePtrSns(
                uint32_t sensorId,
                cy_stc_capsense_context_t * context)
{
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_TST_MEASUREMENT_GROUP_EN)
        cy_stc_capsense_active_scan_sns_t * ptrActive = context->ptrActiveScanSns;
    #endif

    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_TST_MEASUREMENT_GROUP_EN))
        uint32_t widgetSenseGroup = ptrActive->currentSenseMethod;
        ptrActive->connectedSnsState = CY_CAPSENSE_SNS_DISCONNECTED;
        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
            uint32_t numberRows;
            uint32_t numberCols;
        #endif
        #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN) || \
             (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN))
            const cy_stc_capsense_widget_config_t * ptrWdCfg = &context->ptrWdConfig[ptrActive->widgetIndex];
        #endif
    #endif

    #if !(CY_CAPSENSE_ENABLE == CY_CAPSENSE_TST_MEASUREMENT_GROUP_EN)
        (void)context;
    #endif

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_TST_MEASUREMENT_GROUP_EN)
        ptrActive->ptrSnsContext = &context->ptrWdConfig[ptrActive->widgetIndex].ptrSnsContext[sensorId];
    #else
        (void)sensorId;
    #endif

    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_TST_MEASUREMENT_GROUP_EN))
        switch (widgetSenseGroup)
        {
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN)
                case (uint8_t)CY_CAPSENSE_CSD_GROUP:
                    ptrActive->ptrEltdConfig = &ptrWdCfg->ptrEltdConfig[sensorId];
                    break;
            #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN) */

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
                case (uint8_t)CY_CAPSENSE_CSX_GROUP:
                    numberRows = ptrWdCfg->numRows;
                    numberCols = ptrWdCfg->numCols;
                    ptrActive->ptrRxConfig = &ptrWdCfg->ptrEltdConfig[sensorId / numberRows];
                    ptrActive->ptrTxConfig = &ptrWdCfg->ptrEltdConfig[numberCols + (sensorId % numberRows)];
                    break;
            #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) */

            default:
                /* Widget type is not valid so nothing to do */
                break;
        }
    #endif
}

/*******************************************************************************
* Function Name: Cy_CapSense_InitActivePtrWd
****************************************************************************//**
*
* Initializes active scan sensor structure with pointers to current widget
* for further faster access to widget/sensor parameters.
*
* This function does not update pointers to current sensor and the
* Cy_CapSense_InitActivePtrSns() function should be called after current one.
*
* \param widgetId
* Specifies the ID number of the widget. A macro for the widget ID can be found
* in the cycfg_capsense.h file defined as CY_CAPSENSE_<WIDGET_NAME>_WDGT_ID.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_InitActivePtrWd(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context)
{
    cy_stc_capsense_active_scan_sns_t * ptrActive = context->ptrActiveScanSns;

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_TST_MEASUREMENT_GROUP_EN)
        ptrActive->widgetIndex = (uint8_t)widgetId;
    #endif

    ptrActive->currentSenseMethod = context->ptrWdConfig[widgetId].senseMethod;
}


/*******************************************************************************
* Function Name: Cy_CapSense_SsConfigPinRegisters
****************************************************************************//**
*
* Configures drive mode and HSIOM state of a desired pin. The action
* is performed inside the critical section.
*
* \param base
* The pointer to the pin's port register base address.
*
* \param pinNum
* Position of the pin bit-field within the port register.
*
* \param dm
* Specifies drive mode of the pin.
*
* \param hsiom
* Specifies HSIOM state of the pin.
* *
* \param mscCtrl
* Specifies MSC_ANA control state of the IO port analog signaling by the MSC.
*
*******************************************************************************/
void Cy_CapSense_SsConfigPinRegisters(
                GPIO_PRT_Type * base,
                uint32_t pinNum,
                uint32_t dm,
                en_hsiom_sel_t hsiom,
                uint32_t mscCtrl)
{
    uint32_t interruptState = Cy_SysLib_EnterCriticalSection();
    if (CY_CAPSENSE_HSIOM_SEL_GPIO == hsiom)
    {
        Cy_GPIO_SetHSIOM(base, pinNum, hsiom);
        Cy_GPIO_SetDrivemode(base, pinNum, dm);
    }
    else
    {
        Cy_GPIO_SetDrivemode(base, pinNum, dm);
        Cy_GPIO_SetHSIOM(base, pinNum, hsiom);
    }

    if (CY_CAPSENSE_MSCLP_GPIO_MSC_ANA_DIS != mscCtrl)
    {
        Cy_GPIO_MscControlEnable(base, pinNum);
    }
    else
    {
        Cy_GPIO_MscControlDisable(base, pinNum);
    }
    Cy_SysLib_ExitCriticalSection(interruptState);
}


/*******************************************************************************
* Function Name: Cy_CapSense_ScanAbort_V3Lp
****************************************************************************//**
*
* This function sets the sequencer to the idle state by resetting the hardware,
* it can be used to abort current active or low power scan.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \note
* If this function is called from ISR during initialization or
* auto-calibration the operation of these functions will be corrupted.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation \ref cy_capsense_status_t.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ScanAbort_V3Lp(cy_stc_capsense_context_t * context)
{
    uint32_t interruptState;
    const cy_stc_capsense_common_config_t * ptrCommonCfg = context->ptrCommonConfig;
    const cy_stc_capsense_channel_config_t * ptrChannelCfg = ptrCommonCfg->ptrChConfig;

    interruptState = Cy_SysLib_EnterCriticalSection();

    /* Disable HW IP to allow MRSS operations */
    ptrChannelCfg->ptrHwBase->CTL &= ~MSCLP_CTL_ENABLED_Msk;

    /* Wait until ENABLE bit is cleared */
    while (0uL != (MSCLP_CTL_ENABLED_Msk & ptrChannelCfg->ptrHwBase->CTL)) {}

    /* Clear all pending interrupts of the MSCLP HW block */
    ptrChannelCfg->ptrHwBase->INTR_LP = CY_CAPSENSE_MSCLP_INTR_ALL_MSK;
    (void)ptrChannelCfg->ptrHwBase->INTR_LP;

    Cy_SysLib_ExitCriticalSection(interruptState);

    /* Wait for possible MRSS status change */
    Cy_SysLib_DelayUs(CY_MSCLP_CLK_LF_PERIOD_MAX * CY_MSCLP_MRSS_TIMEOUT_FULL);

    /* Set required MRSS state */
    if (CY_CAPSENSE_MRSS_TURN_ON == context->ptrInternalContext->mrssStateAfterScan)
    {
        if (0u == (ptrCommonCfg->ptrChConfig->ptrHwBase->MRSS_STATUS & MSCLP_MRSS_STATUS_MRSS_UP_Msk))
        {
            ptrCommonCfg->ptrChConfig->ptrHwBase->MRSS_CMD = MSCLP_MRSS_CMD_MRSS_START_Msk;
            (void)Cy_CapSense_WaitMrssStatusChange(CY_MSCLP_CLK_LF_PERIOD_MAX * CY_MSCLP_MRSS_TIMEOUT_SMALL, CY_CAPSENSE_MRSS_TURN_ON, context);
        }
    }
    else
    {
        if (0u != (ptrCommonCfg->ptrChConfig->ptrHwBase->MRSS_STATUS & MSCLP_MRSS_STATUS_MRSS_UP_Msk))
        {
            ptrCommonCfg->ptrChConfig->ptrHwBase->MRSS_CMD = MSCLP_MRSS_CMD_MRSS_STOP_Msk;
            (void)Cy_CapSense_WaitMrssStatusChange((CY_MSCLP_CLK_LF_PERIOD_MAX * CY_CAPSENSE_MULTIPLIER_TWO), CY_CAPSENSE_MRSS_TURN_OFF, context);
        }
    }

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LIQUID_LEVEL_FOAM_REJECTION_EN)
        /* Restores config for regular scan */
        context->ptrCommonConfig->ptrChConfig->ptrHwBase->SENSE_DUTY_CTL = 
            ((CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_WIDTH_SEL << MSCLP_SENSE_DUTY_CTL_PHASE_WIDTH_SEL_Pos) | 
             (CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_CYCLES << MSCLP_SENSE_DUTY_CTL_PHASE_SHIFT_CYCLES_Pos) | 
             (CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_WIDTH << MSCLP_SENSE_DUTY_CTL_PHASE_WIDTH_Pos));
    #endif

    context->ptrCommonContext->status = CY_CAPSENSE_NOT_BUSY;

    return CY_CAPSENSE_STATUS_SUCCESS;
}


/*******************************************************************************
* Function Name: Cy_CapSense_MwState_V3Lp
****************************************************************************//**
*
* This function returns a detailed state of the CAPSENSE&trade; middleware and MSC
* hardware in Single- or Multi-channel mode. This feature is useful in
* multi-thread applications or in ISR.
*
* If the middleware is busy, do not initiate a new scan or set up widgets.
* Use the Cy_CapSense_IsBusy() function to check HW busyness at a particular moment.
* Use the Cy_CapSense_MwState() function to verify if MW executes any firmware 
* tasks related to initialization, scanning, and processing at a particular moment.
* If the middleware is busy, a new scan, setup widgets, any kind of reconfiguration, 
* or parameter change should not be initiated.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the state of the middleware as a sum of the state and status masks:
*
* - CY_CAPSENSE_BUSY_CH_MASK                     - The set [x] bit of the result
*                                                  means that the previously initiated
*                                                  scan for the [x] channel is in progress.
*                                                  The next scan frame cannot be started.
* - CY_CAPSENSE_MW_STATE_ACTIVE_WD_SCAN_MASK     - The last or currently scanned widget
*                                                  type is Active widget.
* - CY_CAPSENSE_MW_STATE_LP_WD_SCAN_MASK         - The last or currently scanned widget
*                                                  type is Low Power widget
* - CY_CAPSENSE_BUSY                             - The previously initiated scan is
*                                                  in progress.
* - CY_CAPSENSE_MW_STATE_BIST_MASK               - The BIST is in progress.
*                                                  The next scan frame cannot be started.
* - CY_CAPSENSE_MW_STATE_CALIBRATION_MASK        - The auto-calibration is in progress.
*                                                  The next scan frame cannot be started.
* - CY_CAPSENSE_MW_STATE_SMARTSENSE_MASK         - The smart sensing algorithm is
*                                                  in progress.
*                                                  The next scan frame cannot be started.
* - CY_CAPSENSE_MW_STATE_INITIALIZATION_MASK     - Middleware initialization is
*                                                  in progress and the next scan frame
*                                                  cannot be initiated.
* - CY_CAPSENSE_MW_STATE_SCAN_SLOT_MASK[x]       - The set [x] number of the result
*                                                  means that the previously initiated
*                                                  scan for the [x] slot is completed
*                                                  or in progress.
*
*******************************************************************************/
cy_capsense_mw_state_t Cy_CapSense_MwState_V3Lp(const cy_stc_capsense_context_t * context)
{
    return ((context->ptrCommonContext->status & ~CY_CAPSENSE_MW_STATE_SCAN_SLOT_MASK) |
            ((uint32_t)context->ptrInternalContext->currentSlotIndex << CY_CAPSENSE_MW_STATE_SCAN_SLOT_POS));
}


/*******************************************************************************
* Function Name: Cy_CapSense_SetBusyFlags
****************************************************************************//**
*
* Sets BUSY flags of the cy_capsense_context.status register specified
* by the flags parameter.
*
* This is an internal function. Do not call this function directly from
* the application program.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_SetBusyFlags(cy_stc_capsense_context_t * context)
{
    context->ptrCommonContext->status |= (((uint32_t)CY_CAPSENSE_BUSY_CH_MASK) | CY_CAPSENSE_BUSY);
}


/*******************************************************************************
* Function Name: Cy_CapSense_ClrBusyFlags
****************************************************************************//**
*
* Clears BUSY flags of the cy_capsense_context.status register specified
* by the flags parameter.
*
* This is an internal function. Do not call this function directly from
* the application program.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_ClrBusyFlags(cy_stc_capsense_context_t * context)
{
    /* Clear busy flag for the current channel */
    context->ptrCommonContext->status &= (uint32_t)(~((uint32_t)CY_CAPSENSE_BUSY_CH_MASK));
    context->ptrCommonContext->status &= ~CY_CAPSENSE_BUSY;

    /* Check for EndOfScan callback */
    if (NULL != context->ptrInternalContext->ptrEOSCallback)
    {
        context->ptrInternalContext->ptrEOSCallback(NULL);
    }
}


#if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CALIBRATION_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CALIBRATION_EN) || \
     (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CALIBRATION_EN))
/*******************************************************************************
* Function Name: Cy_CapSense_VerifyCalibration
****************************************************************************//**
*
* Verifies that the calibrated widgets meets the configured conditions.
*
* This function checks whether raw count of each sensor of the specified widgets
* is within the raw count range defined by raw count target and +/- calibration
* error.
*
* \param widgetId
* Specifies the desired widget ID.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS       - The operation is performed successfully.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_VerifyCalibration(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context)
{
    uint32_t snsIndex;
    uint32_t temp;
    uint32_t lowerLimit;
    uint32_t upperLimit;
    uint32_t target;
    uint32_t calibrationError;
    uint32_t currSlot;
    uint32_t frameType;
    cy_capsense_status_t calibStatus = CY_CAPSENSE_STATUS_SUCCESS;
    const cy_stc_capsense_widget_config_t * ptrWdCfg = &context->ptrWdConfig[widgetId];
    const cy_stc_capsense_sensor_context_t * ptrSnsCxt = ptrWdCfg->ptrSnsContext;

    frameType = ((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E == ptrWdCfg->wdType) ?
                    (CY_CAPSENSE_SNS_FRAME_LOW_POWER) : (CY_CAPSENSE_SNS_FRAME_ACTIVE);

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
        /* Dummy scan */
        if (CY_CAPSENSE_CSX_GROUP == ptrWdCfg->senseMethod)
        {
            calibStatus |= Cy_CapSense_ScanSlotInternalCPU(frameType, ptrWdCfg->firstSlotId, context);
        }
    #endif

    for (currSlot = ptrWdCfg->firstSlotId; currSlot < ((uint32_t)ptrWdCfg->firstSlotId + ptrWdCfg->numSlots); currSlot++)
    {
        calibStatus |= Cy_CapSense_ScanSlotInternalCPU(frameType, currSlot, context);
    }

    Cy_CapSense_PreProcessWidget(widgetId, context);

    if (CY_CAPSENSE_STATUS_SUCCESS == calibStatus)
    {
        /* Calculate acceptable raw count range based on the resolution, target and error */
        lowerLimit = 0u;

        /* Gets target in percentage */
        switch (ptrWdCfg->senseMethod)
        {
            #if (CY_CAPSENSE_CSD_CDAC_CALIBRATION_USAGE)
                case (uint8_t)CY_CAPSENSE_CSD_GROUP:
                    target = context->ptrInternalContext->intrCsdRawTarget;
                    calibrationError = context->ptrCommonConfig->csdCalibrationError;
                    break;
            #endif

            #if (CY_CAPSENSE_CSX_CDAC_CALIBRATION_USAGE)
                case (uint8_t)CY_CAPSENSE_CSX_GROUP:
                    target = context->ptrInternalContext->intrCsxRawTarget;
                    calibrationError = context->ptrCommonConfig->csxCalibrationError;
                    break;
            #endif

            #if (CY_CAPSENSE_ISX_CDAC_CALIBRATION_USAGE)
                case (uint8_t)CY_CAPSENSE_ISX_GROUP:
                    target = context->ptrInternalContext->intrIsxRawTarget;
                    calibrationError = context->ptrCommonConfig->isxCalibrationError;
                    break;
            #endif

            default:
                /* Widget type is not valid */
                target = 0u;
                calibrationError = 0u;
                calibStatus = CY_CAPSENSE_STATUS_BAD_PARAM;
                break;
        }

        if (target > calibrationError)
        {
            lowerLimit = target - calibrationError;
        }
        upperLimit = target + calibrationError;
        if (upperLimit > CY_CAPSENSE_PERCENTAGE_100)
        {
            upperLimit = CY_CAPSENSE_PERCENTAGE_100;
        }

        /* Finds max raw count value */
        temp = context->ptrWdContext[widgetId].maxRawCount;

        /* Checks raw count of each sensor */
        ptrSnsCxt = &ptrWdCfg->ptrSnsContext[0u];
        switch (ptrWdCfg->senseMethod)
        {
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN)
                case CY_CAPSENSE_CSD_GROUP:
                    for (snsIndex = 0u; snsIndex < ptrWdCfg->numCols; snsIndex++)
                    {
                        if ((ptrSnsCxt->raw < ((temp * lowerLimit) / CY_CAPSENSE_PERCENTAGE_100)) ||
                            (ptrSnsCxt->raw > ((temp * upperLimit) / CY_CAPSENSE_PERCENTAGE_100)))
                        {
                            calibStatus |= CY_CAPSENSE_STATUS_CALIBRATION_CHECK_FAIL;
                            break;
                        }
                        ptrSnsCxt++;
                    }
                    temp = context->ptrWdContext[widgetId].maxRawCountRow;

                    for (snsIndex = ptrWdCfg->numCols; snsIndex < ptrWdCfg->numSns; snsIndex++)
                    {
                        if ((ptrSnsCxt->raw < ((temp * lowerLimit) / CY_CAPSENSE_PERCENTAGE_100)) ||
                            (ptrSnsCxt->raw > ((temp * upperLimit) / CY_CAPSENSE_PERCENTAGE_100)))
                        {
                            calibStatus |= CY_CAPSENSE_STATUS_CALIBRATION_CHECK_FAIL;
                            break;
                        }
                        ptrSnsCxt++;
                    }
                    break;
            #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN) */

            #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) || \
                 (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN))
                case CY_CAPSENSE_CSX_GROUP:
                case CY_CAPSENSE_ISX_GROUP:
                    for (snsIndex = 0u; snsIndex < ptrWdCfg->numSns; snsIndex++)
                    {
                        if ((ptrSnsCxt->raw < ((temp * lowerLimit) / CY_CAPSENSE_PERCENTAGE_100)) ||
                            (ptrSnsCxt->raw > ((temp * upperLimit) / CY_CAPSENSE_PERCENTAGE_100)))
                        {
                            calibStatus |= CY_CAPSENSE_STATUS_CALIBRATION_CHECK_FAIL;
                            break;
                        }
                        ptrSnsCxt++;
                    }
                    break;
            #endif /* ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) || \
                       (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN)) */

            default:
                calibStatus |= CY_CAPSENSE_STATUS_BAD_PARAM;
                /* No action */
                break;
        }
    }

    return calibStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_VerifyReferenceCdac
****************************************************************************//**
*
* Verifies the result of reference/fine CapDac calibration.
*
* This function checks whether the minimum raw count of the specified widget
* is within the raw count range defined by raw count target and +/- calibration
* error.
*
* \param widgetId
* Specifies the desired widget ID.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS     - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM   - The input parameter is invalid
* - CY_CAPSENSE_STATUS_CALIBRATION_FAIL - The calibration is failed due to
*                                  the issues with scanning (either
*                                  watchdog timer, interrupt breaking, etc.).
* - CY_CAPSENSE_STATUS_CALIBRATION_REF_CHECK_FAIL - The resulting rawcounts across
*                                  all sensors in widget are out of defined range.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_VerifyReferenceCdac(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t calibrationStatus = CY_CAPSENSE_STATUS_SUCCESS;
    uint32_t target;
    uint32_t minRaw;
    uint32_t calibrationError;
    uint32_t lowerLimit;
    uint32_t upperLimit;

    /* Dummy scan */
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
        if (CY_CAPSENSE_CSX_GROUP == context->ptrWdConfig[widgetId].senseMethod)
        {
            calibrationStatus |= Cy_CapSense_ScanWidgetInternalCPU(widgetId, context);
        }
    #endif
    calibrationStatus |= Cy_CapSense_ScanWidgetInternalCPU(widgetId, context);
    Cy_CapSense_PreProcessWidget(widgetId, context);

    /* Gets target in percentage */
    switch (context->ptrWdConfig[widgetId].senseMethod)
    {
        #if (CY_CAPSENSE_CSD_CDAC_CALIBRATION_USAGE)
            case (uint8_t)CY_CAPSENSE_CSD_GROUP:
                calibrationError = (uint32_t)context->ptrCommonConfig->csdCalibrationError;
                target = (uint32_t)context->ptrInternalContext->intrCsdRawTarget;
                break;
        #endif

        #if (CY_CAPSENSE_CSX_CDAC_CALIBRATION_USAGE)
            case (uint8_t)CY_CAPSENSE_CSX_GROUP:
                calibrationError = (uint32_t)context->ptrCommonConfig->csxCalibrationError;
                target = (uint32_t)context->ptrInternalContext->intrCsxRawTarget;
                break;
        #endif

        #if (CY_CAPSENSE_ISX_CDAC_CALIBRATION_USAGE)
            case (uint8_t)CY_CAPSENSE_ISX_GROUP:
                calibrationError = (uint32_t)context->ptrCommonConfig->isxCalibrationError;
                target = (uint32_t)context->ptrInternalContext->intrIsxRawTarget;
                break;
        #endif

        default:
            /* Widget type is not valid */
            target = 0u;
            calibrationError = 0u;
            calibrationStatus = CY_CAPSENSE_STATUS_BAD_PARAM;
            break;
    }

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
        if (CY_CAPSENSE_MPSC_MIN_ORDER <= context->ptrWdConfig[widgetId].mpOrder)
        {
            /* Find maximum capacitance across sensors in widget */
            minRaw = Cy_CapSense_MaxRawSearch(widgetId, CY_CAPSENSE_ROW_SNS_CALIBRATION, context);
        }
        else
        {
            /* Find minimal capacitance across sensors in widget */
            minRaw = Cy_CapSense_MinRawSearch(widgetId, CY_CAPSENSE_ROW_SNS_CALIBRATION, context);
        }
    #else
        /* Find minimal capacitance across sensors in widget */
        minRaw = Cy_CapSense_MinRawSearch(widgetId, CY_CAPSENSE_ROW_SNS_CALIBRATION, context);
    #endif

    lowerLimit = 0u;
    if (target > calibrationError)
    {
        lowerLimit = target - calibrationError;
    }
    upperLimit = target + calibrationError;
    if (upperLimit > CY_CAPSENSE_PERCENTAGE_100)
    {
        upperLimit = CY_CAPSENSE_PERCENTAGE_100;
    }

    if ((minRaw < ((context->ptrWdContext[widgetId].maxRawCount * lowerLimit) / CY_CAPSENSE_PERCENTAGE_100)) ||
        (minRaw > ((context->ptrWdContext[widgetId].maxRawCount * upperLimit) / CY_CAPSENSE_PERCENTAGE_100)))
    {
        calibrationStatus |= CY_CAPSENSE_STATUS_CALIBRATION_REF_CHECK_FAIL;
    }

    #if ((CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_MATRIX_EN) || (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_TOUCHPAD_EN))
        if ((CY_CAPSENSE_CSD_GROUP == context->ptrWdConfig[widgetId].senseMethod) &&
            (((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == context->ptrWdConfig[widgetId].wdType) ||
             ((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == context->ptrWdConfig[widgetId].wdType)))
        {
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
                if (CY_CAPSENSE_MPSC_MIN_ORDER <= context->ptrWdConfig[widgetId].mpOrder)
                {
                    /* Find maximum capacitance across sensors in widget */
                    minRaw = Cy_CapSense_MaxRawSearch(widgetId, CY_CAPSENSE_COL_SNS_CALIBRATION, context);
                }
                else
                {
                    /* Find minimal capacitance across sensors in widget */
                    minRaw = Cy_CapSense_MinRawSearch(widgetId, CY_CAPSENSE_COL_SNS_CALIBRATION, context);
                }
            #else
                /* Find minimal capacitance across sensors in widget */
                minRaw = Cy_CapSense_MinRawSearch(widgetId, CY_CAPSENSE_COL_SNS_CALIBRATION, context);
            #endif

            if ((minRaw < ((context->ptrWdContext[widgetId].maxRawCountRow * lowerLimit) / CY_CAPSENSE_PERCENTAGE_100)) ||
                (minRaw > ((context->ptrWdContext[widgetId].maxRawCountRow * upperLimit) / CY_CAPSENSE_PERCENTAGE_100)))
            {
                calibrationStatus |= CY_CAPSENSE_STATUS_CALIBRATION_REF_CHECK_FAIL;
            }
        }
    #endif

    return calibrationStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_SetCompDivider
****************************************************************************//**
*
* Sets the desired Compensation divider into sensor frames.
*
* This function takes Compensation Divider value from widget structure and
* applies it to all widget's sensors in sensor frame structures.
* This function must not be called when AMUX mode is configured.
*
* \param widgetId
* Specifies widget ID.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_SetCompDivider(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context)
{
    uint32_t i;
    uint32_t * currentFramePtr;
    const cy_stc_capsense_scan_slot_t * ptrScanSlots;
    uint32_t compensationCdacDivider = context->ptrWdContext[widgetId].cdacCompDivider;

    if (0uL != compensationCdacDivider)
    {
        compensationCdacDivider--;
    }

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        if (((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E == context->ptrWdConfig[widgetId].wdType))
        {
            ptrScanSlots = context->ptrLpScanSlots;
            currentFramePtr = &context->ptrSensorFrameLpContext[CY_CAPSENSE_FRM_LP_SNS_SCAN_CTL_INDEX];

            for (i = 0u; i < CY_CAPSENSE_SLOT_LP_COUNT; i++)
            {
                if (ptrScanSlots->wdId == widgetId)
                {
                    *currentFramePtr &= ~MSCLP_SNS_SNS_SCAN_CTL_COMP_DIV_Msk;
                    *currentFramePtr |= (uint32_t)(compensationCdacDivider << MSCLP_SNS_SNS_SCAN_CTL_COMP_DIV_Pos);
                }
                ptrScanSlots++;
                currentFramePtr = &currentFramePtr[CY_MSCLP_11_SNS_REGS];
            }
        }
        else
    #endif
    {
        ptrScanSlots = context->ptrScanSlots;
        currentFramePtr = &context->ptrSensorFrameContext[CY_CAPSENSE_SNS_SCAN_CTL_INDEX];

        for (i = 0u; i < CY_CAPSENSE_SLOT_COUNT; i++)
        {
            if (ptrScanSlots->wdId == widgetId)
            {
                *currentFramePtr &= ~MSCLP_SNS_SNS_SCAN_CTL_COMP_DIV_Msk;
                *currentFramePtr |= (uint32_t)(compensationCdacDivider << MSCLP_SNS_SNS_SCAN_CTL_COMP_DIV_Pos);
            }
            ptrScanSlots++;
            currentFramePtr = &currentFramePtr[CY_CAPSENSE_SENSOR_FRAME_SIZE];
        }
    }
}
#endif


/*******************************************************************************
* Function Name: Cy_CapSense_WaitEndScan
****************************************************************************//**
*
* Waits till end of scan or till the provided timeout.
*
* \param timeout
* Watchdog timeout in microseconds.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS       - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_TIMEOUT       - The software watchdog timeout occurred
*                                      during the scan, the scan was not completed.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_WaitEndScan(
                uint32_t timeout,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t status = CY_CAPSENSE_STATUS_BAD_PARAM;

    /* Approximate duration of Wait For Scan */
    uint32_t isBusyLoopDuration = CY_CAPSENSE_APPROX_LOOP_DURATION;

    uint32_t cpuFreqMHz;
    uint32_t watchdogCounter;

    if (NULL != context)
    {
        status = CY_CAPSENSE_STATUS_SUCCESS;
        cpuFreqMHz = context->ptrCommonConfig->cpuClkHz / CY_CAPSENSE_CONVERSION_MEGA;

        /* Init Watchdog Counter to prevent a hang */
        watchdogCounter = Cy_CapSense_WatchdogCyclesNum(timeout, cpuFreqMHz, isBusyLoopDuration);
        while (CY_CAPSENSE_NOT_BUSY != Cy_CapSense_IsBusy(context))
        {
            if (0uL == watchdogCounter)
            {
                status = CY_CAPSENSE_STATUS_TIMEOUT;
                break;
            }
            watchdogCounter--;
        }
    }

    return status;
}


/*******************************************************************************
* Function Name: Cy_CapSense_SlotPinStateInternal
****************************************************************************//**
*
* Configures the desired electrode to the specified state by
* updating the CAPSENSE&trade; configuration.
*
* See detailed descriptions for the  Cy_CapSense_SlotPinState() and
* Cy_CapSense_LpSlotPinState() functions.
*
* \note
* This function does not check correctness of input arguments. Therefore, 
* wrong values might lead to unpredictable behavior. pinState parameter 
* describes all supported options.
* Some electrodes have specific elements outside a device (for example 
* resistance, capacitance, inductance, connection to GND). Therefore,
* we recommend configuring an electrode to its original type and not use it differently.
*
* \param ptrSnsFrm
* The pointer for sensor frame (Active or Low Power) context structure.
*
* \param ptrEltdCfg
* The pointer to an electrode the all pins states of which will be configured
* as pinState parameter.
*
* \param pinState
* The desired pins state for CSX widget electrodes:
* * CY_CAPSENSE_PIN_STATE_IDX_CSX_RX     - Rx electrode.
* * CY_CAPSENSE_PIN_STATE_IDX_CSX_TX     - Tx electrode.
* * CY_CAPSENSE_PIN_STATE_IDX_GND        - Grounded.
* * CY_CAPSENSE_PIN_STATE_IDX_CSX_NEG_TX - Negative Tx electrode
*     (for multi-phase TX method).
* * CY_CAPSENSE_PIN_STATE_IDX_HIGH_Z     - Unconnected (high-z).
* * CY_CAPSENSE_PIN_STATE_IDX_CSX_VDDA2  - Connected to VDDA/2.
*
* The desired pins state for CSD widget electrodes:
* * CY_CAPSENSE_PIN_STATE_IDX_CSD_SNS    - Self-cap sensor.
* * CY_CAPSENSE_PIN_STATE_IDX_HIGH_Z     - Unconnected (high-z).
* * CY_CAPSENSE_PIN_STATE_IDX_GND        - Grounded.
* * CY_CAPSENSE_PIN_STATE_IDX_ACT_SHIELD - Active shield is routed to the pin.
* * CY_CAPSENSE_PIN_STATE_IDX_PAS_SHIELD - Passive shield is routed to the pin.
*
* The desired pins state for ISX widget electrodes:
* * CY_CAPSENSE_PIN_STATE_IDX_ISX_LX     - Lx electrode.
* * CY_CAPSENSE_PIN_STATE_IDX_ISX_RX     - Rx electrode.
* * CY_CAPSENSE_PIN_STATE_IDX_HIGH_Z     - Unconnected (high-z).
* * CY_CAPSENSE_PIN_STATE_IDX_GND        - Grounded.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_CONFIG       - The function does not suppose to be
*                                         called with the current CAPSENSE&trade;
*                                         configuration.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_SlotPinStateInternal(
                uint32_t * ptrSnsFrm,
                const cy_stc_capsense_electrode_config_t * ptrEltdCfg,
                uint32_t pinState,
                cy_stc_capsense_context_t * context)
{
    uint32_t i;
    uint32_t mask = 0u;
    uint32_t * ptrCswFunc = &context->ptrBaseFrameContext->swSelCswFunc[0u];
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_BAD_CONFIG;
    const uint32_t pinStates[CY_CAPSENSE_CTRLMUX_PIN_STATE_NUMBER] = CY_CAPSENSE_PIN_STATES_ARR;

    /* Check if the desired pin state is assigned already */
    if ((context->ptrInternalContext->mapPinState[pinState] == CY_CAPSENSE_SCW_FUNC_PIN_STATE_IDX_UNDEFINED) &&
        (MSCLP_CSW_GLOBAL_FUNC_NR > context->ptrInternalContext->numFunc))
    {
        context->ptrInternalContext->mapPinState[pinState] = context->ptrInternalContext->numFunc;
        ptrCswFunc[context->ptrInternalContext->numFunc] = pinStates[pinState];
        context->ptrCommonConfig->ptrChConfig->ptrHwBase->SW_SEL_CSW_FUNC[context->ptrInternalContext->numFunc] =
                                                           pinStates[pinState];
        context->ptrInternalContext->numFunc += 1u;
        capStatus = CY_CAPSENSE_STATUS_SUCCESS;

        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
            if (CY_CAPSENSE_PIN_STATE_IDX_CSX_VDDA2 == pinState)
            {
                /* Close the reference to filter switch */
                context->ptrBaseFrameContext->mode[CY_CAPSENSE_REG_MODE_CSX].swSelSh |= MSCLP_MODE_SW_SEL_SH_SOMB_Msk;
            }
        #endif
    }
    else if (context->ptrInternalContext->mapPinState[pinState] != CY_CAPSENSE_SCW_FUNC_PIN_STATE_IDX_UNDEFINED)
    {
        capStatus = CY_CAPSENSE_STATUS_SUCCESS;
    }
    else
    {
        /* Do nothing */
    }

    if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
    {
        /* Update SNS_SW_SEL_CSW_LO_MASK0 - SNS_SW_SEL_CSW_LO_MASK2 in the sensor frame */
        for (i = 0u; i < ptrEltdCfg->numPins; i++)
        {
            mask |= 0x01uL << ptrEltdCfg->ptrPin[i].padNumber;
        }

        for (i = 0u; i < CY_CAPSENSE_CTRLMUX_PIN_STATE_MASK_NUMBER; i++)
        {
            ptrSnsFrm[i] &= ~mask;
            if (0u != (context->ptrInternalContext->mapPinState[pinState] &
                       ((uint8_t)(1u << (CY_CAPSENSE_CTRLMUX_PIN_STATE_MASK_NUMBER - 1u - i)))))
            {
                ptrSnsFrm[i] |= mask;
            }
        }

        /* Force HW configuration update on the next scan */
        capStatus = Cy_CapSense_SwitchHwConfiguration(CY_CAPSENSE_HW_CONFIG_CAPTURED_DEFAULT, context);
    }

    return capStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_SlotPinState_V3Lp
****************************************************************************//**
*
* The internal function that configures the specified electrode to the desired state
* in the specified Active slot by updating the CAPSENSE&trade; configuration.
*
* See the Cy_CapSense_SlotPinState() description for details.
*
* \note
* This function is available for the fifth-generation (only
* for CY_CAPSENSE_CTRLMUX_SENSOR_CONNECTION_METHOD) and the fifth-generation
* low power CAPSENSE&trade;. For the fourth-generation CAPSENSE&trade; and
* the fifth-generation CAPSENSE&trade; with
* CY_CAPSENSE_AMUX_SENSOR_CONNECTION_METHOD use Cy_CapSense_SetPinState().
* For Low Power slots for the fifth-generation low power CAPSENSE&trade;
* use Cy_CapSense_LpSlotPinState().
*
* \param slotId
* The slot ID to change the pin state for (Active slot ID for
* the fifth-generation low power CAPSENSE&trade;).
*
* \param ptrEltdCfg
* The pointer to an electrode the all pins states of which will be configured
* as pinState parameter.
*
* \param pinState
* The parameter have different values for the fifth- and the fifth-generation
* low power CAPSENSE&trade;.
*
* The desired pins state for CSX widget electrodes can be:
* * CY_CAPSENSE_PIN_STATE_IDX_CSX_RX     - Rx electrode.
* * CY_CAPSENSE_PIN_STATE_IDX_CSX_TX     - Tx electrode.
* * CY_CAPSENSE_PIN_STATE_IDX_GND        - Grounded.
* * CY_CAPSENSE_PIN_STATE_IDX_CSX_NEG_TX - Negative Tx electrode
*     (for multi-phase TX method).
* * CY_CAPSENSE_PIN_STATE_IDX_HIGH_Z     - Unconnected (high-z).
* * CY_CAPSENSE_PIN_STATE_IDX_CSX_VDDA2  - Connected to VDDA/2.
*
* The desired pins state for CSD widget electrodes can be:
* * CY_CAPSENSE_PIN_STATE_IDX_CSD_SNS    - Self-cap sensor.
* * CY_CAPSENSE_PIN_STATE_IDX_HIGH_Z     - Unconnected (high-z).
* * CY_CAPSENSE_PIN_STATE_IDX_GND        - Grounded.
* * CY_CAPSENSE_PIN_STATE_IDX_ACT_SHIELD - Active shield is routed to the pin.
* * CY_CAPSENSE_PIN_STATE_IDX_PAS_SHIELD - Passive shield is routed to the pin.
*
* The desired pins state for ISX widget electrodes can be:
* * CY_CAPSENSE_PIN_STATE_IDX_ISX_LX     - Lx electrode.
* * CY_CAPSENSE_PIN_STATE_IDX_ISX_RX     - Rx electrode.
* * CY_CAPSENSE_PIN_STATE_IDX_HIGH_Z     - Unconnected (high-z).
* * CY_CAPSENSE_PIN_STATE_IDX_GND        - Grounded.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_CONFIG       - The function does not suppose to be
*                                         called with the current CAPSENSE&trade;
*                                         configuration.
*
* \funcusage
* \snippet capsense/snippet/main.c snippet_Cy_CapSense_SlotPinState
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_SlotPinState_V3Lp(
                uint32_t slotId,
                const cy_stc_capsense_electrode_config_t * ptrEltdCfg,
                uint32_t pinState,
                cy_stc_capsense_context_t * context)
{
    uint32_t * ptrSnsFrm = &context->ptrSensorFrameContext[slotId * CY_CAPSENSE_SENSOR_FRAME_SIZE];

    return (Cy_CapSense_SlotPinStateInternal(ptrSnsFrm, ptrEltdCfg, pinState, context));
}


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_LpSlotPinState
****************************************************************************//**
*
* Configures the specified electrode to the desired state in the specified Low Power
* slot by updating the CAPSENSE&trade; configuration.
*
* This function changes / overwrites configuration of an electrode (several
* pins in case the electrode is ganged to more pins) with a state specified
* by the pinState parameter. The function does this only for the specified Low Power
* slot ID. If the electrode should have the desired state during scans in another Low
* Power slots, the function should be called multiple times for each desired Low Power
* slot.
*
* The function call changes the pin states permanently and all further scans of
* the slot will have the electrode state as specified by the pinState parameter.
* Call the function again to change the electrode state to a new desired one or
* reinitialize CAPSENSE&trade; middleware by using the Cy_CapSense_Enable() function.
*
* The function changes the configuration of an electrode without storing
* the previous state. A user is responsible to keep the previous state to
* revert to the default settings if needed. Also, the default settings
* can be configured again by calling Cy_CapSense_Enable() function that
* leads to repeating CAPSENSE&trade; Data Structure initialization,
* DAC auto-calibration, and baseline initialization.
*
* Using the function is recommended only for advanced users for specific use cases.
* For instance, to change the CAPSENSE&trade; default electrode configuration,
* the function could be called by using a CAPSENSE&trade; Data Structure
* Initialization callback ptrEODsInitCallback. For details of how to register
* the callback see the \ref group_capsense_callbacks section. That avoids repeating of
* DAC auto-calibration and baseline initialization since the callback is called after
* CAPSENSE&trade; Data Structure initialization but before the first initialization
* scan.
*
* The function is a low-level function and does not perform an input parameter
* verification (like Low Power slot ID, pointers, etc.). For example, the
* CY_CAPSENSE_CTRLMUX_PIN_STATE_SHIELD pin state is not available if a shield is not
* configured in the project, but the function will set the pin state and the HW block
* behavior is unpredictable.
*
* \note
* This function is available only for the fifth-generation low power
* CAPSENSE&trade;. For the fifth-generation (only for
* CY_CAPSENSE_CTRLMUX_SENSOR_CONNECTION_METHOD) and fifth-generation low power
* CAPSENSE&trade; Active slots use Cy_CapSense_SlotPinState(). For fourth-generation
* CAPSENSE&trade and fifth-generation CAPSENSE&trade with
* CY_CAPSENSE_AMUX_SENSOR_CONNECTION_METHOD use Cy_CapSense_SetPinState().
*
* \param lpSlotId
* The desired Low Power slot ID.
*
* \param ptrEltdCfg
* The pointer to an electrode the all pins states of which will be configured
* as pinState parameter.
*
* \param pinState
* The desired pins state for CSX widget electrodes could be:
* * CY_CAPSENSE_RX_PIN - Rx electrode
* * CY_CAPSENSE_TX_PIN - Tx electrode
* * CY_CAPSENSE_GROUND - Grounded
* * CY_CAPSENSE_NEGATIVE_TX_PIN - Negative Tx electrode
*     (for multi-phase TX method)
* * CY_CAPSENSE_HIGHZ - Unconnected (High-Z)
* * CY_CAPSENSE_VDDA2 - Connected to VDDA/2.
*
* The desired pins state for CSD widget electrodes could be:
* * CY_CAPSENSE_SENSOR - Self-cap sensor
* * CY_CAPSENSE_HIGHZ - Unconnected (High-Z)
* * CY_CAPSENSE_GROUND - Grounded
* * CY_CAPSENSE_SHIELD - Shield is routed to the pin.
*
* The desired pins state for ISX widget electrodes could be:
* * CY_CAPSENSE_ISX_RX_PIN - ISX Rx electrode
* * CY_CAPSENSE_ISX_LX_PIN - ISX Lx electrode
* * CY_CAPSENSE_HIGHZ - Unconnected (High-Z).
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_CONFIG       - The function does not suppose to be
*                                         called with the current CAPSENSE&trade;
*                                         configuration.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - 1) lpSlotId, sensorElement or pinState
*                                            are not valid;
*                      2) the CSD sensing method is disabled for desired
*                         CY_CAPSENSE_SHIELD or CY_CAPSENSE_SENSOR states;
*                      3) the CSX sensing method is disabled for desired
*                         CY_CAPSENSE_TX_PIN, CY_CAPSENSE_NEGATIVE_TX_PIN or
*                         CY_CAPSENSE_RX_PIN states.
*                      4) the ISX sensing method is disabled for desired
*                         CY_CAPSENSE_ISX_RX_PIN or CY_CAPSENSE_ISX_LX_PIN
*                         states.
*
* \funcusage
* \snippet capsense/snippet/main.c snippet_Cy_CapSense_LpSlotPinState
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_LpSlotPinState(
                uint32_t lpSlotId,
                const cy_stc_capsense_electrode_config_t * ptrEltdCfg,
                uint32_t pinState,
                cy_stc_capsense_context_t * context)
{
    uint32_t * ptrSnsFrm;
    uint32_t localPinState;
    cy_capsense_status_t result = CY_CAPSENSE_STATUS_BAD_PARAM;

    if ((NULL != context) && (NULL != ptrEltdCfg) && (CY_CAPSENSE_SLOT_LP_COUNT > lpSlotId))
    {
        result = Cy_CapSense_ConvertPinState(pinState, &localPinState);

        if ((uint32_t)CY_CAPSENSE_SUCCESS_E == result)
        {
            ptrSnsFrm = &context->ptrSensorFrameLpContext[(lpSlotId * CY_MSCLP_11_SNS_REGS) + CY_MSCLP_5_SNS_REGS];
            result = Cy_CapSense_SlotPinStateInternal(ptrSnsFrm, ptrEltdCfg, localPinState, context);
        }
    }
    return (result);
}
#endif /* CY_CAPSENSE_LP_EN */


/*******************************************************************************
* Function Name: Cy_CapSense_SwitchHwConfiguration
****************************************************************************//**
*
* Configures CAPSENSE&trade;-related hardware to the specified state.
*
* \param configuration
* The state of CAPSENSE&trade;-related hardware:
* * CY_CAPSENSE_HW_CONFIG_UNDEFINED.
* * CY_CAPSENSE_HW_CONFIG_CAPTURED_DEFAULT.
* * CY_CAPSENSE_HW_CONFIG_REGULAR_SCANNING.
* * CY_CAPSENSE_HW_CONFIG_MPSC_SCANNING.
* * CY_CAPSENSE_HW_CONFIG_CHANNEL_SATURATION
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS      - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM    - At least one of input parameters is
*                                     not valid.
* - CY_CAPSENSE_STATUS_HW_BUSY      - The MSCLP HW block is busy and cannot be
*                                     configured.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_SwitchHwConfiguration(
                uint32_t configuration,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_SUCCESS;
    cy_en_msclp_status_t msclpStatus;
    const cy_stc_capsense_common_config_t * ptrCommonCfg = context->ptrCommonConfig;
    MSCLP_Type * ptrHwBase = ptrCommonCfg->ptrChConfig->ptrHwBase;

    if (context->ptrInternalContext->hwConfigState != configuration)
    {
        /* Turn off the previous HW configuration */
        switch (context->ptrInternalContext->hwConfigState)
        {
            case CY_CAPSENSE_HW_CONFIG_UNDEFINED:
                break;
            case CY_CAPSENSE_HW_CONFIG_CAPTURED_DEFAULT:
                break;
            case CY_CAPSENSE_HW_CONFIG_REGULAR_SCANNING:
                break;
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_TST_HW_GROUP_EN)
                case CY_CAPSENSE_HW_CONFIG_BIST_FUNCTIONALITY:
                    Cy_CapSense_BistDisableMode(context);
                    break;
            #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_TST_HW_GROUP_EN) */
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
                case CY_CAPSENSE_HW_CONFIG_MPSC_SCANNING:
                    break;
            #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED) */
                case CY_CAPSENSE_HW_CONFIG_CHANNEL_SATURATION:
                    break;
                case CY_CAPSENSE_HW_CONFIG_SMARTSENSE:
                    break;
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_AUTO_DITHER_EN)
                case CY_CAPSENSE_HW_CONFIG_AUTO_DITHERING:
                    break;
            #endif
            default:
                capStatus = CY_CAPSENSE_STATUS_BAD_PARAM;
                break;
        }

        /* Clear the repeat scan flag as the HW configuration is changed */
        context->ptrInternalContext->repeatScanEn = CY_CAPSENSE_DISABLE;

        if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
        {
            /* Turn on the desired HW configuration */
            switch (configuration)
            {
                case CY_CAPSENSE_HW_CONFIG_UNDEFINED:
                    break;
                case CY_CAPSENSE_HW_CONFIG_CAPTURED_DEFAULT:
                    break;

                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
                        case CY_CAPSENSE_HW_CONFIG_MPSC_SCANNING: /* fall through */
                    #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED) */

                case CY_CAPSENSE_HW_CONFIG_REGULAR_SCANNING:
                    Cy_CapSense_SetIOsInDesiredState(CY_CAPSENSE_DM_GPIO_ANALOG, CY_CAPSENSE_HSIOM_SEL_GPIO, 0u,
                                                     CY_CAPSENSE_MSCLP_GPIO_MSC_ANA_EN, context);

                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_SHIELD_EN)
                        Cy_CapSense_SetShieldPinsInDesiredState(CY_CAPSENSE_DM_GPIO_ANALOG, CY_CAPSENSE_HSIOM_SEL_GPIO,
                                                                CY_CAPSENSE_MSCLP_GPIO_MSC_ANA_EN, context);
                    #endif

                    /* Reset last scanned widget type */
                    context->ptrCommonContext->status &= (uint32_t)~((uint32_t)CY_CAPSENSE_MW_STATE_WD_SCAN_MASK);
                    context->ptrActiveScanSns->currentSenseMethod = CY_CAPSENSE_UNDEFINED_GROUP;

                    Cy_CapSense_SetCmodInDesiredState(CY_CAPSENSE_DM_GPIO_ANALOG, CY_CAPSENSE_HSIOM_SEL_GPIO,
                                                      CY_CAPSENSE_MSCLP_GPIO_MSC_ANA_EN, context);

                    msclpStatus = Cy_MSCLP_Configure(ptrHwBase,
                                                     context->ptrBaseFrameContext,
                                                     CY_MSCLP_CAPSENSE_KEY,
                                                     ptrCommonCfg->ptrChConfig->ptrHwContext);
                    if (CY_MSCLP_SUCCESS != msclpStatus)
                    {
                        capStatus = CY_CAPSENSE_STATUS_HW_BUSY;
                        break;
                    }

                    /* Disable ACTIVE domain interrupts  */
                    ptrHwBase->INTR_MASK = 0x00u;
                    (void)ptrHwBase->INTR_MASK;

                    /* Clear all pending interrupts */
                    ptrHwBase->INTR_LP = CY_CAPSENSE_MSCLP_INTR_LP_ALL_MSK;
                    (void)ptrHwBase->INTR_LP;

                    /* Update Comp CDAC switch ctrl and replace CSD mode struct with the MPSC configuration */
                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
                        if (CY_CAPSENSE_HW_CONFIG_MPSC_SCANNING == configuration)
                        {
                            ptrHwBase->SW_SEL_CDAC_CO = ((CY_CAPSENSE_SM_MPSC_REG_SW_SEL_CDAC_CO_FLD_SW_COTCA << MSCLP_SW_SEL_CDAC_CO_SW_COTCA_Pos) |
                                (CY_CAPSENSE_SM_MPSC_REG_SW_SEL_CDAC_CO_FLD_SW_COCB << MSCLP_SW_SEL_CDAC_CO_SW_COCB_Pos)   |
                                (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COTV << MSCLP_SW_SEL_CDAC_CO_SW_COTV_Pos)   |
                                (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COTG << MSCLP_SW_SEL_CDAC_CO_SW_COTG_Pos)   |
                                (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COBG << MSCLP_SW_SEL_CDAC_CO_SW_COBG_Pos)   |
                                (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COBV << MSCLP_SW_SEL_CDAC_CO_SW_COBV_Pos));

                            if (CY_CAPSENSE_ENABLE == context->ptrInternalContext->csdCdacDitherEn)
                            {
                                ptrHwBase->MODE[CY_CAPSENSE_REG_MODE_CSD].SENSE_DUTY_CTL = CY_CAPSENSE_MPSC_RM_DITHER_SENSE_DUTY_CTL;
                                ptrHwBase->MODE[CY_CAPSENSE_REG_MODE_CSD].SW_SEL_CDAC_FL = CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_CDAC_FL;
                                ptrHwBase->MODE[CY_CAPSENSE_REG_MODE_CSD].SW_SEL_TOP     = CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_TOP;
                                ptrHwBase->MODE[CY_CAPSENSE_REG_MODE_CSD].SW_SEL_COMP    = CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_COMP;
                                ptrHwBase->MODE[CY_CAPSENSE_REG_MODE_CSD].SW_SEL_SH      = CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_SH;
                                ptrHwBase->MODE[CY_CAPSENSE_REG_MODE_CSD].SW_SEL_CMOD1   = CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_CMOD1;
                                ptrHwBase->MODE[CY_CAPSENSE_REG_MODE_CSD].SW_SEL_CMOD2   = CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_CMOD2;
                            }
                            else
                            {
                                ptrHwBase->MODE[CY_CAPSENSE_REG_MODE_CSD].SENSE_DUTY_CTL = CY_CAPSENSE_MPSC_RM_SENSE_DUTY_CTL;
                                ptrHwBase->MODE[CY_CAPSENSE_REG_MODE_CSD].SW_SEL_CDAC_FL = CY_CAPSENSE_MPSC_RM_SW_SEL_CDAC_FL;
                                ptrHwBase->MODE[CY_CAPSENSE_REG_MODE_CSD].SW_SEL_TOP     = CY_CAPSENSE_MPSC_RM_SW_SEL_TOP;
                                ptrHwBase->MODE[CY_CAPSENSE_REG_MODE_CSD].SW_SEL_COMP    = CY_CAPSENSE_MPSC_RM_SW_SEL_COMP;
                                ptrHwBase->MODE[CY_CAPSENSE_REG_MODE_CSD].SW_SEL_SH      = CY_CAPSENSE_MPSC_RM_SW_SEL_SH;
                                ptrHwBase->MODE[CY_CAPSENSE_REG_MODE_CSD].SW_SEL_CMOD1   = CY_CAPSENSE_MPSC_RM_SW_SEL_CMOD1;
                                ptrHwBase->MODE[CY_CAPSENSE_REG_MODE_CSD].SW_SEL_CMOD2   = CY_CAPSENSE_MPSC_RM_SW_SEL_CMOD2;
                            }
                        }
                    #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED) */
                    break;
                case CY_CAPSENSE_HW_CONFIG_BIST_FUNCTIONALITY:
                    Cy_CapSense_SetIOsInDesiredState(CY_CAPSENSE_DM_GPIO_ANALOG, CY_CAPSENSE_HSIOM_SEL_GPIO, 0u,
                                                     CY_CAPSENSE_MSCLP_GPIO_MSC_ANA_EN, context);

                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_SHIELD_EN)
                        Cy_CapSense_SetShieldPinsInDesiredState(CY_CAPSENSE_DM_GPIO_ANALOG, CY_CAPSENSE_HSIOM_SEL_GPIO,
                                                                CY_CAPSENSE_MSCLP_GPIO_MSC_ANA_EN, context);
                    #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_SHIELD_EN) */

                    context->ptrActiveScanSns->currentSenseMethod = CY_CAPSENSE_UNDEFINED_GROUP;
                    Cy_CapSense_SetCmodInDesiredState(CY_CAPSENSE_DM_GPIO_ANALOG, CY_CAPSENSE_HSIOM_SEL_GPIO,
                                                      CY_CAPSENSE_MSCLP_GPIO_MSC_ANA_EN, context);
                    break;
                case CY_CAPSENSE_HW_CONFIG_CHANNEL_SATURATION:
                    Cy_CapSense_ConfigureSaturationMode(context);
                    break;
                case CY_CAPSENSE_HW_CONFIG_SMARTSENSE:
                    Cy_CapSense_SetupCpuOperatingMode(context);
                    break;
                #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_AUTO_DITHER_EN)
                    case CY_CAPSENSE_HW_CONFIG_AUTO_DITHERING:
                        Cy_CapSense_ConfigureAutoDitherMode(context);
                        break;
                #endif
                default:
                    capStatus = CY_CAPSENSE_STATUS_BAD_PARAM;
                    break;
            }
        }
        if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
        {
            context->ptrInternalContext->hwConfigState = (uint8_t)configuration;
        }
    }

    return (capStatus);
}


/*******************************************************************************
* Function Name: Cy_CapSense_InitializeSourceSenseClk
****************************************************************************//**
*
* Performs the Sense Clock source and the LFSR auto-selection functionality.
* Validates the Sense Clock configuration.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_CLOCK_CONFIG - Sense Clock Divider is out of the valid
*                                         range for the specified Clock source
*                                         configuration.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_InitializeSourceSenseClk(const cy_stc_capsense_context_t * context)
{
    uint32_t wdIndex;
    uint32_t snsClkSrc;
    uint32_t snsClkDivMin = 0u;
    uint32_t lfsrRange;

    cy_capsense_status_t retVal = CY_CAPSENSE_STATUS_SUCCESS;

    cy_stc_capsense_widget_context_t * ptrWdCxt;
    const cy_stc_capsense_widget_config_t * ptrWdCfg = context->ptrWdConfig;

    for (wdIndex = 0u; wdIndex < CY_CAPSENSE_TOTAL_WIDGET_COUNT; wdIndex++)
    {
        ptrWdCxt = ptrWdCfg->ptrWdContext;
        snsClkSrc = ptrWdCxt->snsClkSource;

        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN)
            /* Handling CSD active widgets */
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_CSD_ACTIVE_HW_EN)
                if ((CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod) &&
                    ((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E != ptrWdCfg->wdType))
                {
                    snsClkSrc = 0u;
                }
            #endif
            /* Handling CSD low power widgets */
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_CSD_LP_HW_EN)
                if ((CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod) &&
                    ((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E == ptrWdCfg->wdType))
                {
                    snsClkSrc = 0u;
                }
            #endif
            /* Handling ISX active widgets */
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_ISX_ACTIVE_HW_EN)
                if ((CY_CAPSENSE_ISX_GROUP == ptrWdCfg->senseMethod) &&
                    ((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E != ptrWdCfg->wdType))
                {
                    snsClkSrc = 0u;
                }
            #endif
            /* Handling ISX low power widgets */
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_ISX_LP_HW_EN)
                if ((CY_CAPSENSE_ISX_GROUP == ptrWdCfg->senseMethod) &&
                    ((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E == ptrWdCfg->wdType))
                {
                    snsClkSrc = 0u;
                }
            #endif
        #endif

        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LIQUID_LEVEL_FOAM_REJECTION_EN)
            if ((((uint8_t)CY_CAPSENSE_WD_LIQUID_LEVEL_E == ptrWdCfg->wdType) &&
                (0u != ((ptrWdCfg + 1u)->centroidConfig & CY_CAPSENSE_LLW_FOAM_EN_MASK))) ||
                (0u != (ptrWdCfg->centroidConfig & CY_CAPSENSE_LLW_FOAM_EN_MASK)))
            {
                /* 
                * Set direct clock source for liquid level widget and
                * foam-rejection sub-widget when configured both. 
                */
                snsClkSrc = 0u;
            }
        #endif

        if ((0u != (snsClkSrc & CY_CAPSENSE_CLK_SOURCE_SSC_AUTO_MASK)) ||
           (CY_CAPSENSE_CLK_SOURCE_SSC == (snsClkSrc & CY_CAPSENSE_CLK_SOURCE_MASK)))
        {
            if (0u != (ptrWdCxt->lfsrBits & CY_CAPSENSE_LFSR_BITS_AUTO_MASK))
            {
                /*
                * Execute the LFSR range auto-selection functionality when the
                * Sense Clock source parameter is configured with the SSC or
                * SSC-auto option, and the LFSR range parameter is configured with
                * the auto option.
                */
                ptrWdCxt->lfsrBits = (uint8_t)Cy_CapSense_GetLfsrBitsAuto(ptrWdCfg, context);
            }

            if (0u != (snsClkSrc & CY_CAPSENSE_CLK_SOURCE_SSC_AUTO_MASK))
            {
                /*
                * Execute SSC auto-selection functionality when the
                * Sense Clock source parameter is configured with the SSC-Auto
                * option. This routine performs checking if the SSC clock source
                * is valid for the widget, specified by the input parameter.
                */
                ptrWdCxt->snsClkSource = (uint8_t)Cy_CapSense_GetClkSrcSSCAuto(ptrWdCfg, context);
            }
        }
        else if (0u != (snsClkSrc & CY_CAPSENSE_CLK_SOURCE_PRS_AUTO_MASK))
        {
            /*
            * Execute PRS auto-selection functionality when the
            * Sense Clock source parameter is configured with the PRS-Auto.
            * This routine performs checking if the PRS clock source is valid
            * for the widget, specified by the input parameter.
            */
            ptrWdCxt->snsClkSource = (uint8_t)Cy_CapSense_GetClkSrcPRSAuto(ptrWdCxt, context);
        }
        else
        {
            /*
            * No action required. The Sense Clock source and the LFSR range
            * parameter are configured with the fixed option (Direct, PRS or
            * SSC - for the Sense Clock source parameter and [-2; 1], [-4; 3],
            * [-8; 7] and [-16; 15] - for the LFSR range parameter.)
            */
        }

        /* Determine the MIN valid Sense Clock divider for the used sensing method. */
        switch (ptrWdCfg->senseMethod)
        {
            #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN) ||\
                 (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN))
                case CY_CAPSENSE_CSD_GROUP:
                case CY_CAPSENSE_ISX_GROUP:
                    snsClkDivMin = CY_CAPSENSE_4PH_DIRECT_SNS_CLOCK_DIVIDER_MIN;
                    break;
            #endif

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
                case CY_CAPSENSE_CSX_GROUP:
                    snsClkDivMin = CY_CAPSENSE_2PH_DIRECT_SNS_CLOCK_DIVIDER_MIN;
                    break;
            #endif

            default:
                retVal = CY_CAPSENSE_STATUS_BAD_PARAM;
                /* No action */
                break;
        }

        /*
        * Update the MIN valid Sense Clock divider with the used clock dithering
        * range if the Sense Clock source parameter is configured with the SSC
        * option.
        */
        if (CY_CAPSENSE_CLK_SOURCE_SSC == (snsClkSrc & CY_CAPSENSE_CLK_SOURCE_MASK))
        {
            lfsrRange = ptrWdCxt->lfsrBits;
            lfsrRange &= (uint32_t)(~((uint32_t)CY_CAPSENSE_LFSR_BITS_AUTO_MASK));
            snsClkDivMin += Cy_CapSense_GetLfsrDitherVal(lfsrRange, context->ptrInternalContext->lfsrScale);
        }

        /* Perform validation if the Sense Clock divider is within the valid range. */
        if ((ptrWdCxt->snsClk < snsClkDivMin) ||
           (ptrWdCxt->snsClk > CY_CAPSENSE_DIRECT_SNS_CLOCK_DIVIDER_MAX))
        {
            retVal = CY_CAPSENSE_STATUS_BAD_CLOCK_CONFIG;
        }

        #if ((CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_MATRIX_EN) ||\
            (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_TOUCHPAD_EN))
            if ((CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod) &&
                (((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == ptrWdCfg->wdType) ||
                ((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == ptrWdCfg->wdType)))
            {
                if ((ptrWdCxt->rowSnsClk < snsClkDivMin) ||
                   (ptrWdCxt->rowSnsClk > CY_CAPSENSE_DIRECT_SNS_CLOCK_DIVIDER_MAX))

                {
                    retVal = CY_CAPSENSE_STATUS_BAD_CLOCK_CONFIG;
                }
            }
        #endif

        if (CY_CAPSENSE_STATUS_BAD_CLOCK_CONFIG == retVal)
        {
            break;
        }

        ptrWdCfg++;
    }

    return retVal;
}


/*******************************************************************************
* Function Name: Cy_CapSense_GetLfsrBitsAuto
****************************************************************************//**
*
* Selects the number of LSB bits to use from the LSFR to provide the clock
* dithering variation on the base period if the snsClkSource member of the
* cy_stc_capsense_widget_context_t is configured with the
* CY_CAPSENSE_CLK_SOURCE_SSC_AUTO_MASK mask or with the or the
* CY_CAPSENSE_CLK_SOURCE_SSC value.
*
* \param ptrWdConfig
* Specifies the pointer to a widget configuration structure.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetLfsrBitsAuto(
                const cy_stc_capsense_widget_config_t * ptrWdConfig,
                const cy_stc_capsense_context_t * context)
{
    uint32_t lfsrScale;
    uint32_t lfsrRange;
    uint32_t ditherLimitPercents;
    uint32_t snsClkDividerMin;
    uint32_t snsClkDividerTmp;

    const cy_stc_capsense_widget_context_t * ptrWdCxt;

    ptrWdCxt = ptrWdConfig->ptrWdContext;
    snsClkDividerTmp = ptrWdCxt->snsClk;
    lfsrScale = context->ptrInternalContext->lfsrScale;
    ditherLimitPercents = ptrWdConfig->lfsrDitherLimit;

    #if ((CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_MATRIX_EN) ||\
         (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_TOUCHPAD_EN))
        if ((CY_CAPSENSE_CSD_GROUP == ptrWdConfig->senseMethod) &&
            (((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == ptrWdConfig->wdType) ||
             ((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == ptrWdConfig->wdType)))
        {
            /*
            * Obtain the MIN Sense Clock divider within the two-dimension CSD widget.
            * The LFSR range should be determined, basing on the MIN Sense Clock
            * divider in order to be sufficient for rows and columns.
            */
            if (snsClkDividerTmp > ptrWdCxt->rowSnsClk)
            {
                snsClkDividerTmp = ptrWdCxt->rowSnsClk;
            }
        }
    #endif

    /* Determine the MIN valid Sense Clock divider for the used sensing method. */
    switch (ptrWdConfig->senseMethod)
    {
        #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN) || \
             (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN))
            case CY_CAPSENSE_CSD_GROUP:
            case CY_CAPSENSE_ISX_GROUP:
                snsClkDividerMin = CY_CAPSENSE_4PH_DIRECT_SNS_CLOCK_DIVIDER_MIN;
                break;
        #endif

        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
            case CY_CAPSENSE_CSX_GROUP:
                snsClkDividerMin = CY_CAPSENSE_2PH_DIRECT_SNS_CLOCK_DIVIDER_MIN;
                break;
        #endif

        default:
            snsClkDividerMin = 0u;
            break;
    }

    /*
    * Execute the LFSR range selection routine. This routine determines
    * the LFSR_BITS option, required to provide the max clock dithering variation
    * for the specified sense Clock divider, LFSR dither (in percents) and
    * LFSR scale values.
    */
    lfsrRange = Cy_CapSense_GetLfsrBitsNumber(snsClkDividerTmp, snsClkDividerMin,
                                              ditherLimitPercents, lfsrScale);

    return (lfsrRange | CY_CAPSENSE_LFSR_BITS_AUTO_MASK);
}


/*******************************************************************************
* Function Name: Cy_CapSense_GetClkSrcSSCAuto
****************************************************************************//**
*
* Performs checking if the SSC clock source is valid for the widget, specified
* by the input parameter.
*
* \param ptrWdConfig
* Specifies the pointer to a widget configuration structure.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the valid clock source:
* - SSC    -if SSC is valid for the specified widget configuration.
* - Direct -if SSC is not valid for the specified widget configuration.
* The CY_CAPSENSE_CLK_SOURCE_SSC_AUTO_MASK bit is always set in the return
* value.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetClkSrcSSCAuto(
                const cy_stc_capsense_widget_config_t * ptrWdConfig,
                const cy_stc_capsense_context_t * context)
{
    uint32_t lfsrRange;
    uint32_t lfsrScale;
    uint32_t snsClkSrc;
    uint32_t autoSelMode;
    uint32_t ditherLimitPercents;
    uint32_t lfsrDitherCycles;
    uint32_t ditherLimitCycles;
    uint32_t lfsrPolySize;
    uint32_t snsClkDivMin;
    uint32_t subConvNumber;
    const cy_stc_capsense_widget_context_t * ptrWdCxt;
    #if ((CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_MATRIX_EN) ||\
         (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_TOUCHPAD_EN))
        uint32_t snsClkSrcRow;
    #endif

    ptrWdCxt = ptrWdConfig->ptrWdContext;

    /*
    * Determine the whole number of sub-conversion per scan (includes Dummy and
    * Measurement conversions).
    */
    subConvNumber = ptrWdCxt->numSubConversions;
    subConvNumber += context->ptrInternalContext->numFineInitCycles;
    if (CY_CAPSENSE_16_BIT_MASK < subConvNumber)
    {
        subConvNumber = CY_CAPSENSE_16_BIT_MASK;
    }
    lfsrRange = ((uint32_t)ptrWdCxt->lfsrBits & (uint32_t)(~((uint32_t)CY_CAPSENSE_LFSR_BITS_AUTO_MASK)));
    lfsrScale = context->ptrInternalContext->lfsrScale;
    autoSelMode = ptrWdConfig->snsClkSourceAutoSelMode;
    ditherLimitPercents = ptrWdConfig->lfsrDitherLimit;

    /*
    * Determine the polynomial duration in clock cycles, e.g. the duration of 8-bit
    * polynomial is 255 clock cycles.
    */
    lfsrPolySize = Cy_CapSense_GetPolySize(context->ptrInternalContext->lfsrPoly);

    /*
    * Determine the clock dithering variation for the specifies LFSR range,
    * e.g for the [-2; 1] range the clock variation will be 2 cycles.
    */
    lfsrDitherCycles = Cy_CapSense_GetLfsrDitherVal(lfsrRange, lfsrScale);

    /* Determine the MIN valid Sense Clock divider for the used sensing method. */
    if ((CY_CAPSENSE_CSD_GROUP == ptrWdConfig->senseMethod) ||
        (CY_CAPSENSE_ISX_GROUP == ptrWdConfig->senseMethod))
    {
        snsClkDivMin = CY_CAPSENSE_4PH_DIRECT_SNS_CLOCK_DIVIDER_MIN;
    }
    else
    {
        snsClkDivMin = CY_CAPSENSE_2PH_DIRECT_SNS_CLOCK_DIVIDER_MIN;
    }

    /*
    * Determines the max allowed clock dithering variation for the specified
    * Sense Clock divider, LFSR dither (in percents) and LFSR scale values.
    */
    ditherLimitCycles = Cy_CapSense_GetLfsrDitherLimit(ptrWdCxt->snsClk,
                                    snsClkDivMin, ditherLimitPercents, lfsrScale);

    /*
    * Execute the SSC-auto selection routine. This routine validates all the
    * criteria, that are required for good SSC performance are met.
    * The CY_CAPSENSE_CLK_SOURCE_SSC will be returned if all the criteria are met,
    * the CY_CAPSENSE_CLK_SOURCE_DIRECT will be returned if not.
    */
    snsClkSrc = Cy_CapSense_RunSSCAuto(autoSelMode, lfsrDitherCycles,
                                    ditherLimitCycles, lfsrPolySize, subConvNumber);

    #if ((CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_MATRIX_EN) ||\
         (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_TOUCHPAD_EN))
        /* Repeat the SSC-auto selection routine for the row of two-dimension CSD
         * widget.
         */
        if ((CY_CAPSENSE_CSD_GROUP == ptrWdConfig->senseMethod) &&
            (((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == ptrWdConfig->wdType) ||
             ((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == ptrWdConfig->wdType)))
        {
            if ((uint8_t)CY_CAPSENSE_CLK_SOURCE_DIRECT != snsClkSrc)
            {
                ditherLimitCycles = Cy_CapSense_GetLfsrDitherLimit(ptrWdCxt->rowSnsClk,
                                                snsClkDivMin, ditherLimitPercents, lfsrScale);
                snsClkSrcRow = Cy_CapSense_RunSSCAuto(autoSelMode, lfsrDitherCycles,
                                                ditherLimitCycles, lfsrPolySize, (uint16_t)subConvNumber);

                if (snsClkSrc != snsClkSrcRow)
                {
                    /*
                    * If the automatically determined Sense Clock sources for
                    * rows and columns are different, the widget Sense Clock
                    * source should be set to Direct.
                    */
                    snsClkSrc = CY_CAPSENSE_CLK_SOURCE_DIRECT;
                }
            }
        }
    #endif

    return (snsClkSrc | CY_CAPSENSE_CLK_SOURCE_SSC_AUTO_MASK);
}


/*******************************************************************************
* Function Name: Cy_CapSense_RunSSCAuto
****************************************************************************//**
*
* Implements checking the following rules:
* 1. An LFSR value should be selected so that the max clock dither in percents
*    is limited with the value, specified by the lfsrDitherLimit parameter.
* 2. At least one full spread spectrum polynomial should pass during the scan
*    time.
* 3. The value of the number of conversions should be an integer multiple of the
*    repeat period of the polynomial, that is specified by the
*    Sense Clock LFSR Polynomial parameter.
*
* \param autoSelMode
*  Defines set of rules, to be checked in order to decide if the SSC clock
*  source is applicable for the specified parameters.
*
* \param lfsrDitherCycles
*  Dintering variation in the number of Mod Clock cycles.
*
* \param ditherLimitCycles
*  Max dither in percentage, the actual clock dithering variation should
*  be limited with.
*
* \param lfsrPolySize
*  Number of Sense Clock cycles, required to fully pass the configured
*  polynomial.
*
* \param subConvNumber
*  Number of sub-conversions(including Dummy).
*
* \return
* Returns the valid clock source:
* - CY_CAPSENSE_CLK_SOURCE_SSC    -if SSC is valid for the specified widget
*                                  configuration.
* - CY_CAPSENSE_CLK_SOURCE_DIRECT -if SSC is not valid for the specified widget
*                                  configuration.
*
*******************************************************************************/
uint32_t Cy_CapSense_RunSSCAuto(
                uint32_t autoSelMode,
                uint32_t lfsrDitherCycles,
                uint32_t ditherLimitCycles,
                uint32_t lfsrPolySize,
                uint32_t subConvNumber)
{
    uint32_t snsClkSrc = CY_CAPSENSE_CLK_SOURCE_SSC;

    /* Check if the Sense Clock variation is lower than MAX allowed. */
    if (lfsrDitherCycles > ditherLimitCycles)
    {
        snsClkSrc = CY_CAPSENSE_CLK_SOURCE_DIRECT;
    }

    /*
    * Check if at least one whole polynomial period will be performed
    * during the scan. This part of code is executed if the Clock Source
    * auto selection mode is set to Medium or Strong.
    */
    if (autoSelMode != CY_CAPSENSE_SNS_CLK_SOURCE_AUTO_SEL_MODE_WEAK)
    {
        if (subConvNumber < lfsrPolySize)
        {
            snsClkSrc = CY_CAPSENSE_CLK_SOURCE_DIRECT;
        }
    }

    /*
    * Check if the integer number of the polynomial periods will be performed
    * during the scan. This part of code is executed if the Clock Source
    * auto selection mode is set to Strong.
    */
    if (autoSelMode == CY_CAPSENSE_SNS_CLK_SOURCE_AUTO_SEL_MODE_STRONG)
    {
        if (0u != (subConvNumber % lfsrPolySize))
        {
            snsClkSrc = CY_CAPSENSE_CLK_SOURCE_DIRECT;
        }
    }

    return snsClkSrc;
}


/*******************************************************************************
* Function Name: Cy_CapSense_GetClkSrcPRSAuto
****************************************************************************//**
*
* Performs checking if the PRS clock source is valid for the widget, specified
* by the input parameter.
*
* \param ptrWdContext
*  Specifies the pointer to a widget context structure.
*
* \param context
*  The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
*  Returns the valid clock source:
* - PRS    -if SSC is valid for the specified widget configuration.
* - Direct -if SSC is not valid for the specified widget configuration.
* The CY_CAPSENSE_CLK_SOURCE_PRS_AUTO_MASK bit is always set in the return
* value.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetClkSrcPRSAuto(
                const cy_stc_capsense_widget_context_t * ptrWdContext,
                const cy_stc_capsense_context_t * context)
{
    uint32_t lfsrPolySize;
    uint32_t risingEdgesNum;
    uint32_t subConvNumber;
    uint32_t snsClkSrc = CY_CAPSENSE_CLK_SOURCE_PRS;

    /*
    * Determine the whole number of sub-conversion per scan (includes Dummy and
    * Measurement conversions).
    */
    subConvNumber = ptrWdContext->numSubConversions;
    subConvNumber += context->ptrInternalContext->numFineInitCycles;

    /*
    * Determine the polynomial duration in clock cycles, e.g. the duration of 8-bit
    * polynomial is 255 clock cycles.
    */
    lfsrPolySize = Cy_CapSense_GetPolySize(context->ptrInternalContext->lfsrPoly);

    /*
    * The number of rising edges per one PRS period is (polyLength + 1) / 4.
    * polyLength = 2^N - 1, where N is size of the shift register (8BIT, 12BIT, etc).
    */
    risingEdgesNum = (lfsrPolySize + 1u) >> CY_CAPSENSE_4PH_PRS_SNS_CLOCK_DIVIDER_SHIFT;

    /*
    * Check if at least one whole polynomial period will be performed
    * during the scan.
    */
    if (subConvNumber < risingEdgesNum)
    {
        snsClkSrc = CY_CAPSENSE_CLK_SOURCE_DIRECT;
    }

    return (snsClkSrc | CY_CAPSENSE_CLK_SOURCE_PRS_AUTO_MASK);
}


/*******************************************************************************
* Function Name: Cy_CapSense_GetPolySize
****************************************************************************//**
*
* Calculates the number of Sense Clock cycles, required to fully pass the
* specified polynomial.
*
* \param lfsrPoly
*  Specifies the polynomial the calculation should be performed for.
*
* \return
*  Number of Sense Clock cycles, required to fully pass the specified
*  polynomial.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetPolySize(uint32_t lfsrPoly)
{
    /* Initialization the msbIndex variable with the MAX possible size of polynomial */
    uint32_t polySize = 0xFFFFu;
    uint32_t polyMsbMask = 0x8000u;

    while ((1u < polySize) && (0u == (lfsrPoly & polyMsbMask)))
    {
        polySize >>= 1u;
        polyMsbMask >>= 1u;
    }

    return polySize;
}


/*******************************************************************************
* Function Name: Cy_CapSense_GetLfsrBitsNumber
****************************************************************************//**
*
* Determines SNS_CTL.LFSR_BITS option, required to provide the max clock
* dithering variation for the specified parameters.
*
* \param snsClkDivider
* The divider value for the sense clock.
*
* \param snsClkDividerMin
* The minimal valid value of the sense clock divider.
*
* \param ditherLimitPercents
*  Max dither in percentage, the actual clock dither should be limited with.
*
* \param lfsrScale
*  Number of bits to shift the LFSR output left before adding to SENSE_DIV.
*
* \return
*  The SNS_CTL.LFSR_BITS option:
*   - CY_CAPSENSE_LFSR_BITS_RANGE_0 - Use 2 bits range: [-2,1]
*   - CY_CAPSENSE_LFSR_BITS_RANGE_1 - Use 3 bits range: [-4,3]
*   - CY_CAPSENSE_LFSR_BITS_RANGE_2 - Use 4 bits range: [-8,7]
*   - CY_CAPSENSE_LFSR_BITS_RANGE_3 - Use 5 bits range: [-16,15]
*
*******************************************************************************/
uint32_t Cy_CapSense_GetLfsrBitsNumber(
                uint32_t snsClkDivider,
                uint32_t snsClkDividerMin,
                uint32_t ditherLimitPercents,
                uint32_t lfsrScale)
{
    uint32_t retVal;
    uint32_t ditherLimitCycles;

    /*
    * Determine the max allowed clock dithering variation for the specified
    * Sense Clock divider, LFSR dither (in percents) and LFSR scale values.
    */
    ditherLimitCycles = Cy_CapSense_GetLfsrDitherLimit(snsClkDivider, snsClkDividerMin,
                                                       ditherLimitPercents, lfsrScale);

    /* Based in the MAX allowed clock dithering, Determines the LFSR_BITS option. */
    if (CY_CAPSENSE_LFSR_RANGE_3_DITHER_MAX <= ditherLimitCycles)
    {
        retVal = CY_CAPSENSE_LFSR_BITS_RANGE_3;
    }
    else if (CY_CAPSENSE_LFSR_RANGE_2_DITHER_MAX <= ditherLimitCycles)
    {
        retVal = CY_CAPSENSE_LFSR_BITS_RANGE_2;
    }
    else if (CY_CAPSENSE_LFSR_RANGE_1_DITHER_MAX <= ditherLimitCycles)
    {
        retVal = CY_CAPSENSE_LFSR_BITS_RANGE_1;
    }
    else
    {
        retVal = CY_CAPSENSE_LFSR_BITS_RANGE_0;
    }

    return retVal;
}


/*******************************************************************************
* Function Name: Cy_CapSense_GetLfsrDitherVal
****************************************************************************//**
*
* Determines the clock dithering variation for the specified parameters.
*
* \param lfsrBits
*  The supported SNS_CTL.LFSR_BITS option:
*   - CY_CAPSENSE_LFSR_BITS_RANGE_0 - Use 2 bits range: [-2,1]
*   - CY_CAPSENSE_LFSR_BITS_RANGE_1 - Use 3 bits range: [-4,3]
*   - CY_CAPSENSE_LFSR_BITS_RANGE_2 - Use 4 bits range: [-8,7]
*   - CY_CAPSENSE_LFSR_BITS_RANGE_3 - Use 5 bits range: [-16,15]
*
* \param lfsrScale
*  Number of bits to shift the LFSR output left before adding to SENSE_DIV.
*
* \return
*  Dintering variation in the number of Mod Clock cycles.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetLfsrDitherVal(
                uint32_t lfsrBits,
                uint32_t lfsrScale)
{
    return (uint32_t)(1uL << (((lfsrBits & CY_CAPSENSE_LFSR_BITS_RANGE_MASK) + 1u) + lfsrScale));
}


/*******************************************************************************
* Function Name: Cy_CapSense_GetLfsrDitherLimit
****************************************************************************//**
*
* Determines the max allowed clock dithering variation for the specified
* parameters.
*
* \param snsClkDivider
* The divider value for the sense clock.
*
* \param snsClkDividerMin
* The minimal valid value of the sense clock divider.
*
* \param ditherLimitPercents
* Max dither in percentage, the actual clock dither should be limited with.
*
* \param lfsrScale
*  Number of bits to shift the LFSR output left before adding to SENSE_DIV.
*
* \return
*  Dintering variation in the number of Mod Clock cycles.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetLfsrDitherLimit(
                uint32_t snsClkDivider,
                uint32_t snsClkDividerMin,
                uint32_t ditherLimitPercents,
                uint32_t lfsrScale)
{
    uint32_t ditherLimitCycles;
    uint32_t ditherLimitCyclesMax;

    /*
    * Determine the dither limit in clock cycles for the specified Dither limit
    * in percents.
    */
    ditherLimitCycles = ((ditherLimitPercents * snsClkDivider) / CY_CAPSENSE_PERCENTAGE_100);
    ditherLimitCycles >>= lfsrScale;

    /* Determine MAX allowed dither in cycles for the specified Sense Clock divider. */
    ditherLimitCyclesMax = (snsClkDivider - snsClkDividerMin) / (1u << lfsrScale);

    /*
    * Determine the minimal value to eliminate violation of allowed Sense Clock
    * divider range.
    */
    if (ditherLimitCycles > ditherLimitCyclesMax)
    {
        ditherLimitCycles = ditherLimitCyclesMax;
    }

    return ditherLimitCycles;
}


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_EN)

#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_SsSquareRoot16
****************************************************************************//**
*
* Calculates square root of the specified value.
*
* The specified value is unsigned 16-bit value. The square root is rounded up.
*
* \param value
* Specifies a value the square root should be taken from.
*
* \return
* Returns the square root of the specified value.
*
*******************************************************************************/
uint32_t Cy_CapSense_SsSquareRoot16(uint16_t value)
{
    uint32_t m = 0x4000u;
    uint32_t y = 0u;
    uint32_t b = 0u;
    uint32_t x = value;

    while (m != 0u)
    {
        b = y | m;
        y = y >> 1u;
        if (x >= b) {
            x = x - b;
            y = y | m;
        }
        m >>= 2u;
    }
    if (value > (y * y))
    {
        y++;
    }

    return y;
}
#endif


/*******************************************************************************
* Function Name: Cy_CapSense_SsSquareRoot16
****************************************************************************//**
*
* Checks if widget is configured for SmartSense and supported by SmartSense.
*
* The following configurations are verified:
* * CSX sensing method is not supported
* * Liquid Level widget is not applicable
* * Multi-phase technique is not supported.
*
* \param ptrWdConfig
* Specifies the pointer to a widget configuration structure.
*
* \return
* Returns CY_CAPSENSE_STATUS_SUCCESS if widget is valid for SmartSense operation.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_IsSmarSenseWidgetValid(
                const cy_stc_capsense_widget_config_t * ptrWdConfig)
{
    cy_capsense_status_t autoTuneStatus = CY_CAPSENSE_STATUS_SUCCESS;

    (void)ptrWdConfig;

    /* Skip auto-tuning for CSX widgets */
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
        if (CY_CAPSENSE_CSX_GROUP == ptrWdConfig->senseMethod)
        {
            autoTuneStatus = CY_CAPSENSE_STATUS_BAD_CONFIG;
        }
    #endif

    /* Skip auto-tuning for Liquid level widgets */
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LIQUID_LEVEL_EN)
        if ((uint8_t)CY_CAPSENSE_WD_LIQUID_LEVEL_E == ptrWdConfig->wdType)
        {
            autoTuneStatus = CY_CAPSENSE_STATUS_BAD_CONFIG;
        }
    #endif

    /* Skip auto-tuning for MPSC widgets*/
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
        if (1u != ptrWdConfig->mpOrder)
        {
            autoTuneStatus = CY_CAPSENSE_STATUS_BAD_CONFIG;
        }
    #endif

    return autoTuneStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_SsAutoTune
****************************************************************************//**
*
* Performs the parameters auto-tuning for the optimal CAPSENSE&trade; operation when
* smart sensing algorithm is enabled.
*
* This function performs the following tasks:
* - Tune the Sense Clock optimal value.
* - Calculate the number of sub-conversions for the optimal finger capacitance.
*
* \note
* The function supposes final auto-calibration is called right after this
* function.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - Zero     - All the SmartSense-configured widgets are auto-tuned successfully.
* - Non-zero - Auto-tuning failed for any widget.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_SsAutoTune(cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t autoTuneStatus = CY_CAPSENSE_STATUS_SUCCESS;

    uint32_t wdIndex;
    uint32_t snsIndex;
    uint32_t scanSlotId;
    uint32_t numberSubConv;
    uint32_t rawCountMax;
    cy_stc_capsense_hw_smartsense_config_t autoTuneConfig;
    const cy_stc_capsense_widget_config_t * ptrWdCfg;
    cy_stc_capsense_widget_context_t * ptrWdCxt;
    cy_stc_capsense_sensor_context_t * ptrSnsCxt;
    const cy_stc_capsense_common_config_t * ptrCommonCfg = context->ptrCommonConfig;
    cy_stc_capsense_common_context_t * ptrCommonCxt = context->ptrCommonContext;
    const cy_stc_capsense_scan_slot_t * ptrScanSlots;

    #if (CY_CAPSENSE_SMARTSENSE_ISX_EN)
        volatile uint32_t * ptrSnsCtl;
        uint32_t rawCount;
    #endif

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN)
        uint32_t cic2Decimation;
        uint32_t cic2Sample;

        MSCLP_Type * msclpBase = ptrCommonCfg->ptrChConfig->ptrHwBase;
    #endif

    ptrCommonCxt->status |= CY_CAPSENSE_MW_STATE_SMARTSENSE_MASK;

    /* Step #0: Checks if configuration is valid */
    if (ptrCommonCfg->counterMode != CY_CAPSENSE_COUNTER_MODE_SATURATE)
    {
        autoTuneStatus |= CY_CAPSENSE_STATUS_BAD_CONFIG;
    }
    else
    {

        /* Step #1: Sets the default parameters for preliminary scans */
        for (wdIndex = 0u; wdIndex < CY_CAPSENSE_TOTAL_WIDGET_COUNT; wdIndex++)
        {
            ptrWdCfg = &context->ptrWdConfig[wdIndex];
            ptrWdCxt = ptrWdCfg->ptrWdContext;
            ptrSnsCxt = ptrWdCfg->ptrSnsContext;

            /* Skip widgets not configured / not supported for SmartSense */
            if (CY_CAPSENSE_STATUS_SUCCESS != Cy_CapSense_IsSmarSenseWidgetValid(ptrWdCfg))
            {
                continue;
            }
            if (0u == Cy_CapSense_IsWidgetEnabled(wdIndex, context))
            {
                continue;
            }

            /* Handling CSD active widgets */
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_CSD_ACTIVE_HW_EN)
                if ((CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod) && ((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E != ptrWdCfg->wdType))
                {
                    /* Initializes SmartSense scan configuration */
                    ptrWdCxt->snsClkSource <<= CY_CAPSENSE_CLK_SOURCE_SMARTSENSE_POS;
                    ptrWdCxt->numSubConversions = CY_CAPSENSE_SMARTSENSE_CSD_PRELIMINARY_SCAN_NSUB;
                    ptrWdCxt->cdacRef = CY_CAPSENSE_SMARTSENSE_CSD_PRELIMINARY_SCAN_REF_CDAC;
                    ptrWdCxt->rowCdacRef = CY_CAPSENSE_SMARTSENSE_CSD_PRELIMINARY_SCAN_REF_CDAC;
                    ptrWdCxt->snsClk = CY_CAPSENSE_SMARTSENSE_CSD_PRELIMINARY_SCAN_SNS_CLK;
                    ptrWdCxt->rowSnsClk = CY_CAPSENSE_SMARTSENSE_CSD_PRELIMINARY_SCAN_SNS_CLK;

                    for (snsIndex = 0u; snsIndex < ptrWdCfg->numSns; snsIndex++)
                    {
                        ptrSnsCxt->cdacComp = 0u;
                        ptrSnsCxt++;
                    }
                }
            #endif

            /* Handling CSD low power widgets */
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_CSD_LP_HW_EN)
                if ((CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod) && ((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E == ptrWdCfg->wdType))
                {
                    /* Initializes SmartSense scan configuration */
                    ptrWdCxt->snsClkSource <<= CY_CAPSENSE_CLK_SOURCE_SMARTSENSE_POS;
                    ptrWdCxt->numSubConversions = CY_CAPSENSE_SMARTSENSE_CSD_PRELIMINARY_SCAN_NSUB;
                    ptrWdCxt->cdacRef = CY_CAPSENSE_SMARTSENSE_CSD_PRELIMINARY_SCAN_REF_CDAC;
                    ptrWdCxt->rowCdacRef = CY_CAPSENSE_SMARTSENSE_CSD_PRELIMINARY_SCAN_REF_CDAC;
                    ptrWdCxt->snsClk = CY_CAPSENSE_SMARTSENSE_CSD_PRELIMINARY_SCAN_SNS_CLK;
                    ptrWdCxt->rowSnsClk = CY_CAPSENSE_SMARTSENSE_CSD_PRELIMINARY_SCAN_SNS_CLK;

                    for (snsIndex = 0u; snsIndex < ptrWdCfg->numSns; snsIndex++)
                    {
                        ptrSnsCxt->cdacComp = 0u;
                        ptrSnsCxt++;
                    }
                }
            #endif

            /* Handling ISX active widgets */
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_ISX_ACTIVE_HW_EN)
                if ((CY_CAPSENSE_ISX_GROUP == ptrWdCfg->senseMethod) && ((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E != ptrWdCfg->wdType))
                {
                    /* Initializes SmartSense scan configuration */
                    ptrWdCxt->snsClkSource <<= CY_CAPSENSE_CLK_SOURCE_SMARTSENSE_POS;
                    ptrWdCxt->numSubConversions = CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_NSUB;
                    ptrWdCxt->cdacRef = CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_REF_CDAC;
                    ptrWdCxt->rowCdacRef = CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_REF_CDAC;
                    ptrWdCxt->snsClk = CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_SNS_CLK;
                    ptrWdCxt->rowSnsClk = CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_SNS_CLK;

                    for (snsIndex = 0u; snsIndex < ptrWdCfg->numSns; snsIndex++)
                    {
                        ptrSnsCxt->cdacComp = 0u;
                        ptrSnsCxt++;
                    }
                }
            #endif

            /* Handling ISX low power widgets */
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_ISX_LP_HW_EN)
                if ((CY_CAPSENSE_ISX_GROUP == ptrWdCfg->senseMethod) && ((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E == ptrWdCfg->wdType))
                {
                    /* Initializes SmartSense scan configuration */
                    ptrWdCxt->snsClkSource <<= CY_CAPSENSE_CLK_SOURCE_SMARTSENSE_POS;
                    ptrWdCxt->numSubConversions = CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_NSUB;
                    ptrWdCxt->cdacRef = CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_REF_CDAC;
                    ptrWdCxt->rowCdacRef = CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_REF_CDAC;
                    ptrWdCxt->snsClk = CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_SNS_CLK;
                    ptrWdCxt->rowSnsClk = CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_SNS_CLK;

                    for (snsIndex = 0u; snsIndex < ptrWdCfg->numSns; snsIndex++)
                    {
                        ptrSnsCxt->cdacComp = 0u;
                        ptrSnsCxt++;
                    }
                }
            #endif
        }

        autoTuneStatus |= Cy_CapSense_SsInitialize(context);
        autoTuneStatus |= Cy_CapSense_SwitchHwConfiguration(CY_CAPSENSE_HW_CONFIG_REGULAR_SCANNING, context);

        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN)
            /* Sets FILTER_MODE to CIC1 */
            msclpBase->FILTER_CTL &= ~MSCLP_FILTER_CTL_FILTER_MODE_Msk;
        #endif

        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_EXT_FRM_START_EN)
            /* Clear the external start scan mode */
            msclpBase->CTL &= ~MSCLP_CTL_EXT_FRAME_START_MODE_Msk;
        #endif

        /* Step #2: Executes preliminary scans for all active widgets:
         * For CSD sensors a single scan is enough to define a sensor capacitance.
         * For ISX sensors a multiple scans needed to find valid operation frequency.
         */
        #if (CY_CAPSENSE_SMARTSENSE_ACTIVE_HW_EN)
            ptrScanSlots = context->ptrScanSlots;
            for (scanSlotId = 0u; scanSlotId < CY_CAPSENSE_SLOT_COUNT; scanSlotId++)
            {
                wdIndex = ptrScanSlots[scanSlotId].wdId;
                ptrWdCfg = &context->ptrWdConfig[wdIndex];

                /* Skip widgets not configured / not supported for SmartSense */
                if (CY_CAPSENSE_STATUS_SUCCESS != Cy_CapSense_IsSmarSenseWidgetValid(ptrWdCfg))
                {
                    continue;
                }
                if (0u == Cy_CapSense_IsWidgetEnabled(wdIndex, context))
                {
                    continue;
                }

                switch (ptrWdCfg->senseMethod)
                {
                    #if (CY_CAPSENSE_SMARTSENSE_CSD_ACTIVE_HW_EN)
                        case CY_CAPSENSE_CSD_GROUP:
                            autoTuneStatus |= Cy_CapSense_ScanSlotInternalCPU(CY_CAPSENSE_SNS_FRAME_ACTIVE, scanSlotId, context);
                            break;
                    #endif
                    #if (CY_CAPSENSE_SMARTSENSE_ISX_ACTIVE_HW_EN)
                        case CY_CAPSENSE_ISX_GROUP:
                            autoTuneStatus |= Cy_CapSense_ScanSlotInternalCPU(CY_CAPSENSE_SNS_FRAME_ACTIVE, scanSlotId, context);

                            /* Step #2a: Executes series of scans for ISX to find valid frequency */
                            ptrWdCxt = ptrWdCfg->ptrWdContext;
                            snsIndex = ptrScanSlots[scanSlotId].snsId;
                            ptrSnsCtl = &context->ptrSensorFrameContext[scanSlotId * CY_CAPSENSE_SENSOR_FRAME_SIZE + CY_CAPSENSE_SNS_CTL_INDEX];

                            while (CY_CAPSENSE_SMARTSENSE_ISX_SNS_CLK_MIN < ptrWdCxt->snsClk)
                            {
                                ptrWdCxt->snsClk -= CY_CAPSENSE_SMARTSENSE_ISX_SNS_CLK_STEP;
                                *ptrSnsCtl &= ~MSCLP_SNS_SNS_CTL_SENSE_DIV_Msk;
                                *ptrSnsCtl |= (uint32_t)ptrWdCxt->snsClk << MSCLP_SNS_SNS_CTL_SENSE_DIV_Pos;

                                autoTuneStatus |= Cy_CapSense_ScanSlotInternalCPU(CY_CAPSENSE_SNS_FRAME_ACTIVE, scanSlotId, context);
                                rawCountMax = (uint32_t)ptrWdCxt->snsClk * ptrWdCxt->numSubConversions;
                                /* Stop scanning if 95% is reached */
                                rawCountMax *= CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_STOP;
                                rawCountMax /= CY_CAPSENSE_PERCENTAGE_100;
                                rawCount = ptrWdCfg->ptrSnsContext[snsIndex].raw;

                                if (rawCount >= rawCountMax)
                                {
                                    ptrWdCxt->snsClk += CY_CAPSENSE_SMARTSENSE_ISX_SNS_CLK_STEP;
                                    *ptrSnsCtl &= ~MSCLP_SNS_SNS_CTL_SENSE_DIV_Msk;
                                    *ptrSnsCtl |= (uint32_t)ptrWdCxt->snsClk << MSCLP_SNS_SNS_CTL_SENSE_DIV_Pos;
                                    autoTuneStatus |= Cy_CapSense_ScanSlotInternalCPU(CY_CAPSENSE_SNS_FRAME_ACTIVE, scanSlotId, context);
                                    break;
                                }
                            }

                            break;
                    #endif
                    default:
                        /* No action */
                        break;
                }
            }
        #endif

        /* Performs preliminary scans for all LP widgets if SmartSense is configured for them */
        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_LP_HW_EN)
            ptrScanSlots = context->ptrLpScanSlots;
            for (scanSlotId = 0u; scanSlotId < CY_CAPSENSE_SLOT_LP_COUNT; scanSlotId++)
            {
                wdIndex = ptrScanSlots[scanSlotId].wdId;
                ptrWdCfg = &context->ptrWdConfig[wdIndex];

                /* Skip widgets not configured / not supported for SmartSense */
                if (CY_CAPSENSE_STATUS_SUCCESS != Cy_CapSense_IsSmarSenseWidgetValid(ptrWdCfg))
                {
                    continue;
                }
                if (0u == Cy_CapSense_IsWidgetEnabled(wdIndex, context))
                {
                    continue;
                }

                switch (ptrWdCfg->senseMethod)
                {
                    #if (CY_CAPSENSE_SMARTSENSE_CSD_LP_HW_EN)
                        case CY_CAPSENSE_CSD_GROUP:
                            autoTuneStatus |= Cy_CapSense_ScanSlotInternalCPU(CY_CAPSENSE_SNS_FRAME_LOW_POWER, scanSlotId, context);
                            break;
                    #endif
                    #if (CY_CAPSENSE_SMARTSENSE_ISX_LP_HW_EN)
                        case CY_CAPSENSE_ISX_GROUP:
                            autoTuneStatus |= Cy_CapSense_ScanSlotInternalCPU(CY_CAPSENSE_SNS_FRAME_LOW_POWER, scanSlotId, context);

                            /* Step #2a: Executes series of scans for ISX to find valid frequency */
                            ptrWdCxt = ptrWdCfg->ptrWdContext;
                            snsIndex = ptrScanSlots[scanSlotId].snsId;
                            ptrSnsCtl = &context->ptrSensorFrameLpContext[scanSlotId * CY_MSCLP_11_SNS_REGS + CY_CAPSENSE_FRM_LP_SNS_CTL_INDEX];

                            while (CY_CAPSENSE_SMARTSENSE_ISX_SNS_CLK_MIN <= ptrWdCxt->snsClk)
                            {
                                ptrWdCxt->snsClk -= CY_CAPSENSE_SMARTSENSE_ISX_SNS_CLK_STEP;
                                *ptrSnsCtl &= ~MSCLP_SNS_SNS_CTL_SENSE_DIV_Msk;
                                *ptrSnsCtl |= (uint32_t)ptrWdCxt->snsClk << MSCLP_SNS_SNS_CTL_SENSE_DIV_Pos;
                                autoTuneStatus |= Cy_CapSense_ScanSlotInternalCPU(CY_CAPSENSE_SNS_FRAME_LOW_POWER, scanSlotId, context);
                                rawCountMax = (uint32_t)ptrWdCxt->snsClk * ptrWdCxt->numSubConversions;
                                /* Stop scanning if 95% is reached */
                                rawCountMax *= CY_CAPSENSE_SMARTSENSE_ISX_PRELIMINARY_SCAN_STOP;
                                rawCountMax /= CY_CAPSENSE_PERCENTAGE_100;
                                rawCount = ptrWdCfg->ptrSnsContext[snsIndex].raw;

                                if (rawCount >= rawCountMax)
                                {
                                    ptrWdCxt->snsClk += CY_CAPSENSE_SMARTSENSE_ISX_SNS_CLK_STEP;
                                    *ptrSnsCtl &= ~MSCLP_SNS_SNS_CTL_SENSE_DIV_Msk;
                                    *ptrSnsCtl |= (uint32_t)ptrWdCxt->snsClk << MSCLP_SNS_SNS_CTL_SENSE_DIV_Pos;
                                    autoTuneStatus |= Cy_CapSense_ScanSlotInternalCPU(CY_CAPSENSE_SNS_FRAME_LOW_POWER, scanSlotId, context);
                                    break;
                                }
                            }

                            break;
                    #endif
                    default:
                        /* No action */
                        break;
                }
            }
        #endif


        /*
         * Step #3: Calculates sensor capacitances, sense clock dividers, and sub-conversion numbers depending on the configured
         * serial resistances, and finger capacitances for each sensor. Sets the configured modClk value in Hz for calculations.
         */
        #if (CY_CAPSENSE_IMO_FREQUENCY == CY_CAPSENSE_IMO_25_MHZ)
            autoTuneConfig.modClock = CY_CAPSENSE_IMO_CLK_25_MHZ * CY_CAPSENSE_CONVERSION_MEGA / context->ptrInternalContext->modClk;
        #elif (CY_CAPSENSE_IMO_FREQUENCY == CY_CAPSENSE_IMO_38_MHZ)
            autoTuneConfig.modClock = CY_CAPSENSE_IMO_CLK_38_MHZ * CY_CAPSENSE_CONVERSION_MEGA / context->ptrInternalContext->modClk;
        #else
            autoTuneConfig.modClock = CY_CAPSENSE_IMO_CLK_46_MHZ * CY_CAPSENSE_CONVERSION_MEGA / context->ptrInternalContext->modClk;
        #endif

        for (wdIndex = 0u; wdIndex < CY_CAPSENSE_TOTAL_WIDGET_COUNT; wdIndex++)
        {
            ptrWdCfg = &context->ptrWdConfig[wdIndex];

            /* Skip widgets not configured / not supported for SmartSense */
            if (CY_CAPSENSE_STATUS_SUCCESS != Cy_CapSense_IsSmarSenseWidgetValid(ptrWdCfg))
            {
                continue;
            }
            if (0u == Cy_CapSense_IsWidgetEnabled(wdIndex, context))
            {
                continue;
            }


            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_CSD_EN)
                if ((CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod) &&
                    ((((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E != ptrWdCfg->wdType) &&
                    (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_CSD_ACTIVE_HW_EN)) ||
                    (((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E == ptrWdCfg->wdType) &&
                    (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_CSD_LP_HW_EN))))
                {
                    ptrWdCxt = ptrWdCfg->ptrWdContext;
                    autoTuneConfig.snsResistance = CY_CAPSENSE_SMARTSENSE_CSD_RESISTANCE_CONST;
                    autoTuneConfig.correctionCoeff = 0u;
                    autoTuneConfig.kRef0 = ptrWdCxt->snsClk;
                    autoTuneConfig.nSub0 = ptrWdCxt->numSubConversions;
                    autoTuneConfig.refCdac = ptrWdCxt->cdacRef;
                    autoTuneConfig.fingerCap = ptrWdCxt->fingerCap;

                    /* Find maximum rawcount to calculate max possible sensor clock frequency */
                    rawCountMax = 0u;
                    for (snsIndex = 0u; snsIndex < ptrWdCfg->numSns; snsIndex++)
                    {
                        if (rawCountMax < ptrWdCfg->ptrSnsContext[snsIndex].raw)
                        {
                            rawCountMax = ptrWdCfg->ptrSnsContext[snsIndex].raw;
                        }
                    }

                    autoTuneConfig.raw = (uint16_t)rawCountMax;
                    (void)Cy_CapSense_GetSmartSenseCapacitance(&autoTuneConfig);
                    autoTuneConfig.snsCapacitance /= ptrWdCfg->numChopCycles;
                    (void)Cy_CapSense_GetSmartSenseFrequencyDivider(&autoTuneConfig);

                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_FREQUENCY_WIDGET_EN)
                        /* Checks for sub-widget */
                        if (0u != (ptrWdCfg->mfsConfig & CY_CAPSENSE_MFS_EN_MASK))
                        {
                            if (0u != (ptrWdCfg->mfsConfig & CY_CAPSENSE_MFS_WIDGET_FREQ_CH_1_MASK))
                            {
                                autoTuneConfig.kRef1 += CY_CAPSENSE_CSD_MFS_DIVIDER_OFFSET_F1;
                            }

                            if (0u != (ptrWdCfg->mfsConfig & CY_CAPSENSE_MFS_WIDGET_FREQ_CH_2_MASK))
                            {
                                autoTuneConfig.kRef1 += CY_CAPSENSE_CSD_MFS_DIVIDER_OFFSET_F2;
                            }
                        }
                    #endif

                    /* Configures widget sense clock divider by the calculated value */
                    ptrWdCxt->snsClk = autoTuneConfig.kRef1;
                    ptrWdCxt->rowSnsClk = autoTuneConfig.kRef1;
                    autoTuneConfig.refCdac = context->ptrInternalContext->intrCsdRawTarget;

                    /* Finds minimum rawcount starting from the previously defined max raw to define sensitivity properly */
                    for (snsIndex = 0u; snsIndex < ptrWdCfg->numSns; snsIndex++)
                    {
                        if (rawCountMax > ptrWdCfg->ptrSnsContext[snsIndex].raw)
                        {
                            rawCountMax = ptrWdCfg->ptrSnsContext[snsIndex].raw;
                        }
                    }
                    autoTuneConfig.raw = (uint16_t)rawCountMax;
                    (void)Cy_CapSense_GetSmartSenseCapacitance(&autoTuneConfig);
                    autoTuneConfig.snsCapacitance /= ptrWdCfg->numChopCycles;

                    (void)Cy_CapSense_GetSmartSenseNumSubconversions(&autoTuneConfig);

                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN)

                        numberSubConv = autoTuneConfig.nSub1;

                        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_COMP_USAGE)
                            /* Decreases scan duration per boost configuration */
                            numberSubConv /= (uint8_t)((ptrWdCfg->cdacConfig & CY_CAPSENSE_CDAC_BOOST_VAL_MASK) >> CY_CAPSENSE_CDAC_BOOST_VAL_POS);
                        #endif

                        rawCountMax = numberSubConv * autoTuneConfig.kRef1;

                        /* Finds Decimation Rate */
                        cic2Decimation = CY_CAPSENSE_MAX_DECIMATION_RATE;
                        if ((CY_CAPSENSE_MAX_DECIMATION_RATE * CY_CAPSENSE_MAX_DECIMATION_RATE) > (rawCountMax / ptrWdCfg->numChopCycles))
                        {
                            cic2Decimation = Cy_CapSense_SsSquareRoot16((uint16_t)(rawCountMax / ptrWdCfg->numChopCycles));
                        }
                        cic2Decimation--;

                        do
                        {
                            cic2Decimation++;

                            /* Finds valid CIC2 sample number with rounding down */
                            cic2Sample = Cy_CapSense_GetCIC2HwDivider(cic2Decimation);
                            if (cic2Sample > cic2Decimation)
                            {
                                cic2Sample >>= 1u;
                            }

                            /* Switches to full sample numbers */
                            cic2Sample++;

                            /* Finds Nsub considering quantization we have with CIC2 sample number with rounding up */
                            numberSubConv = ((cic2Decimation * cic2Sample) + (autoTuneConfig.kRef1 - 1u)) / autoTuneConfig.kRef1;
                        }
                        /* Checks if back-calculated CIC2 sample number is unchanged */
                        while ((cic2Sample != ((numberSubConv * autoTuneConfig.kRef1) / cic2Decimation)) &&
                                (cic2Decimation < CY_CAPSENSE_MAX_DECIMATION_RATE));

                        /* Calculates 75% of signal per desired finger capacitance */
                        ptrWdCxt->sigPFC = (uint16_t)(((cic2Decimation * cic2Decimation) * autoTuneConfig.sigPFC) / rawCountMax);
                        ptrWdCxt->cicRate = (uint8_t)cic2Decimation;
                        ptrWdCxt->numSubConversions = (uint16_t)numberSubConv;

                    #else /* #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN) */

                        numberSubConv = autoTuneConfig.nSub1;
                        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_COMP_USAGE)
                            /* Decreases scan duration per boost configuration */
                            numberSubConv /= (uint8_t)((ptrWdCfg->cdacConfig & CY_CAPSENSE_CDAC_BOOST_VAL_MASK) >> CY_CAPSENSE_CDAC_BOOST_VAL_POS);
                        #endif

                        /* Limits Nsub to maximum possible value to avoid RawCount overflow */
                        rawCountMax = ((uint32_t)MSCLP_SNS_RESULT_FIFO_RD_RAW_COUNT_Msk >> MSCLP_SNS_RESULT_FIFO_RD_RAW_COUNT_Pos) / autoTuneConfig.kRef1;
                        if (numberSubConv > rawCountMax)
                        {
                            numberSubConv = rawCountMax;
                        }

                        /* Counts System Chopping */
                        numberSubConv /= ptrWdCfg->numChopCycles;

                        ptrWdCxt->numSubConversions = (uint16_t)numberSubConv;

                        numberSubConv *= ptrWdCfg->numChopCycles;
                        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_COMP_USAGE)
                            /* Decreases scan duration per boost configuration */
                            numberSubConv *= (uint8_t)((ptrWdCfg->cdacConfig & CY_CAPSENSE_CDAC_BOOST_VAL_MASK) >> CY_CAPSENSE_CDAC_BOOST_VAL_POS);
                        #endif

                        /*
                        * numberSubConv contains real value including chopping and compensation.
                        * autoTuneConfig.nSub1 contains initially calculated value.
                        * So, correcting the initially calculated sensitivity.
                        */
                        ptrWdCxt->sigPFC = (uint16_t)((numberSubConv * autoTuneConfig.sigPFC) / autoTuneConfig.nSub1);

                    #endif /* #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN) */
                }
            #endif

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_ISX_EN)
                if ((CY_CAPSENSE_ISX_GROUP == ptrWdCfg->senseMethod) &&
                    ((((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E != ptrWdCfg->wdType) &&
                    (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_ISX_ACTIVE_HW_EN)) ||
                    (((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E == ptrWdCfg->wdType) &&
                    (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_ISX_LP_HW_EN))))
                {
                    ptrWdCxt = ptrWdCfg->ptrWdContext;
                    autoTuneConfig.snsResistance = CY_CAPSENSE_SMARTSENSE_ISX_RESISTANCE_CONST;
                    autoTuneConfig.fingerCap = ptrWdCxt->fingerCap;

                    /* Find maximum rawcount to calculate max possible sensor clock frequency */
                    rawCountMax = 0u;
                    for (snsIndex = 0u; snsIndex < ptrWdCfg->numSns; snsIndex++)
                    {
                        if (rawCountMax < ptrWdCfg->ptrSnsContext[snsIndex].raw)
                        {
                            rawCountMax = ptrWdCfg->ptrSnsContext[snsIndex].raw;
                        }
                    }

                    autoTuneConfig.raw = (uint16_t)rawCountMax;

                    (void)Cy_CapSense_GetSmartSenseIsxInductance(&autoTuneConfig);
                    autoTuneConfig.snsCapacitance /= ptrWdCfg->numChopCycles;

                    (void)Cy_CapSense_GetSmartSenseIsxFrequencyDivider(&autoTuneConfig);

                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_FREQUENCY_WIDGET_EN)
                        /* Checks for sub-widget */
                        if (0u != (ptrWdCfg->mfsConfig & CY_CAPSENSE_MFS_EN_MASK))
                        {
                            if (0u != (ptrWdCfg->mfsConfig & CY_CAPSENSE_MFS_WIDGET_FREQ_CH_1_MASK))
                            {
                                autoTuneConfig.kRef1 += CY_CAPSENSE_CSD_MFS_DIVIDER_OFFSET_F1;
                            }

                            if (0u != (ptrWdCfg->mfsConfig & CY_CAPSENSE_MFS_WIDGET_FREQ_CH_2_MASK))
                            {
                                autoTuneConfig.kRef1 += CY_CAPSENSE_CSD_MFS_DIVIDER_OFFSET_F2;
                            }
                        }
                    #endif

                    /* Configures widget sense clock divider by the calculated value */
                    ptrWdCxt->snsClk = autoTuneConfig.kRef1;
                    ptrWdCxt->rowSnsClk = autoTuneConfig.kRef1;
                    autoTuneConfig.refCdac = context->ptrInternalContext->intrIsxRawTarget;

                    /* Finds minimum rawcount starting from the previously defined max raw to define sensitivity properly */
                    rawCountMax = CY_CAPSENSE_32_BIT_MASK;
                    for (snsIndex = 0u; snsIndex < ptrWdCfg->numSns; snsIndex++)
                    {
                        if (rawCountMax > ptrWdCfg->ptrSnsContext[snsIndex].raw)
                        {
                            rawCountMax = ptrWdCfg->ptrSnsContext[snsIndex].raw;
                        }
                    }
                    autoTuneConfig.raw = (uint16_t)rawCountMax;

                    (void)Cy_CapSense_GetSmartSenseIsxInductance(&autoTuneConfig);
                    autoTuneConfig.snsCapacitance /= ptrWdCfg->numChopCycles;

                    (void)Cy_CapSense_GetSmartSenseIsxNumSubconversions(&autoTuneConfig);

                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN)
                        /******************************************************************************/
                        /* ISX SmartSense to be fixed */
                        /******************************************************************************/

                        numberSubConv = autoTuneConfig.nSub1;

                        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_COMP_USAGE)
                            /* Decreases scan duration per boost configuration */
                            numberSubConv /= (uint8_t)((ptrWdCfg->cdacConfig & CY_CAPSENSE_CDAC_BOOST_VAL_MASK) >> CY_CAPSENSE_CDAC_BOOST_VAL_POS);
                        #endif

                        rawCountMax = numberSubConv * autoTuneConfig.kRef1;

                        /* Finds Decimation Rate */
                        cic2Decimation = CY_CAPSENSE_MAX_DECIMATION_RATE;
                        if ((CY_CAPSENSE_MAX_DECIMATION_RATE * CY_CAPSENSE_MAX_DECIMATION_RATE) > (rawCountMax / ptrWdCfg->numChopCycles))
                        {
                            cic2Decimation = Cy_CapSense_SsSquareRoot16((uint16_t)(rawCountMax / ptrWdCfg->numChopCycles));
                        }
                        cic2Decimation--;

                        do
                        {
                            cic2Decimation++;

                            /* Finds valid CIC2 sample number with rounding down */
                            cic2Sample = Cy_CapSense_GetCIC2HwDivider(cic2Decimation);
                            if (cic2Sample > cic2Decimation)
                            {
                                cic2Sample >>= 1u;
                            }

                            /* Switches to full sample numbers */
                            cic2Sample++;

                            /* Finds Nsub considering quantization we have with CIC2 sample number with rounding up */
                            numberSubConv = ((cic2Decimation * cic2Sample) + (autoTuneConfig.kRef1 - 1u)) / autoTuneConfig.kRef1;
                        }
                        /* Checks if back-calculated CIC2 sample number is unchanged */
                        while ((cic2Sample != ((numberSubConv * autoTuneConfig.kRef1) / cic2Decimation)) &&
                                (cic2Decimation < CY_CAPSENSE_MAX_DECIMATION_RATE));

                        /* Calculates 75% of signal per desired finger capacitance */
                        ptrWdCxt->sigPFC = (uint16_t)(((cic2Decimation * cic2Decimation) * autoTuneConfig.sigPFC) / rawCountMax);
                        ptrWdCxt->cicRate = (uint8_t)cic2Decimation;
                        ptrWdCxt->numSubConversions = (uint16_t)numberSubConv;

                    #else /* #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN) */

                        numberSubConv = autoTuneConfig.nSub1;
                        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_COMP_USAGE)
                            /* Decreases scan duration per boost configuration */
                            numberSubConv /= (uint8_t)((ptrWdCfg->cdacConfig & CY_CAPSENSE_CDAC_BOOST_VAL_MASK) >> CY_CAPSENSE_CDAC_BOOST_VAL_POS);
                        #endif

                        /* Limits Nsub to maximum possible value to avoid RawCount overflow */
                        rawCountMax = ((uint32_t)MSCLP_SNS_RESULT_FIFO_RD_RAW_COUNT_Msk >> MSCLP_SNS_RESULT_FIFO_RD_RAW_COUNT_Pos) / autoTuneConfig.kRef1;
                        if (numberSubConv > rawCountMax)
                        {
                            numberSubConv = rawCountMax;
                        }

                        /* Counts System Chopping */
                        numberSubConv /= ptrWdCfg->numChopCycles;

                        ptrWdCxt->numSubConversions = (uint16_t)numberSubConv;

                        numberSubConv *= ptrWdCfg->numChopCycles;
                        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_COMP_USAGE)
                            /* Decreases scan duration per boost configuration */
                            numberSubConv *= (uint8_t)((ptrWdCfg->cdacConfig & CY_CAPSENSE_CDAC_BOOST_VAL_MASK) >> CY_CAPSENSE_CDAC_BOOST_VAL_POS);
                        #endif

                        /*
                        * numberSubConv contains real value including chopping and compensation.
                        * autoTuneConfig.nSub1 contains initially calculated value.
                        * So, correcting the initially calculated sensitivity.
                        */
                        ptrWdCxt->sigPFC = (uint16_t)((numberSubConv * autoTuneConfig.sigPFC) / autoTuneConfig.nSub1);

                    #endif /* #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN) */
                }
            #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SMARTSENSE_ISX_EN) */
        }

        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN)
            /* Restores FILTER_MODE to CIC2 */
            msclpBase->FILTER_CTL |= MSCLP_FILTER_CTL_FILTER_MODE_Msk;
        #endif

        /* Step #4: Assigns clock sources and restores project parameters */
        for (wdIndex = 0u; wdIndex < CY_CAPSENSE_TOTAL_WIDGET_COUNT; wdIndex++)
        {
            ptrWdCfg = &context->ptrWdConfig[wdIndex];
            /* Skip widgets not configured / not supported for SmartSense */
            if (CY_CAPSENSE_STATUS_SUCCESS != Cy_CapSense_IsSmarSenseWidgetValid(ptrWdCfg))
            {
                continue;
            }
            if (0u == Cy_CapSense_IsWidgetEnabled(wdIndex, context))
            {
                continue;
            }
            ptrWdCxt = ptrWdCfg->ptrWdContext;
            /* Reverts back original customer's settings */
            ptrWdCxt->snsClkSource = (uint8_t)(((uint32_t)ptrWdCxt->snsClkSource >> CY_CAPSENSE_CLK_SOURCE_SMARTSENSE_POS) &
                    ~CY_CAPSENSE_CLK_SOURCE_SMARTSENSE_MASK);
        }

        autoTuneStatus |= Cy_CapSense_SsInitialize(context);
    }

    ptrCommonCxt->status &= ~CY_CAPSENSE_MW_STATE_SMARTSENSE_MASK;

    return autoTuneStatus;
}
#endif


/*******************************************************************************
* Function Name: Cy_CapSense_TransferRawCounts
****************************************************************************//**
*
* Transfers raw counts for specified sensors from internal MSCLP IP RAM to the
* corresponding field in the structure where the sensor data is stored.
*
* \param startSlotId
* The slot ID transfer will be started from.
*
* \param numberSlots
* The number of slots will be transferred.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_TransferRawCounts(
                uint32_t startSlotId,
                uint32_t numberSlots,
                cy_stc_capsense_context_t * context)
{
    cy_stc_capsense_sensor_context_t * ptrSnsCxt;
    MSCLP_Type * ptrHwBase = context->ptrCommonConfig->ptrChConfig->ptrHwBase;
    uint32_t lastSlot;
    uint32_t currSlot;
    uint32_t tmpRawCount;
    uint32_t wdIndex;
    uint32_t snsIndex;

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_RC_HW_IIR_FILTER_EN)
        /* Initialize frame data pointer */
        uint32_t * ptrSensorFrame = &context->ptrSensorFrameContext[startSlotId * CY_CAPSENSE_SENSOR_FRAME_SIZE];

        /* Initialize sensor data pointer */
        __IOM uint32_t * ptrSensorData = &ptrHwBase->SNS.SENSOR_DATA[0u];
    #endif

    lastSlot = startSlotId + numberSlots - 1u;

    /* Reads the raw counts for last scan */
    for (currSlot = startSlotId; currSlot <= lastSlot; currSlot++)
    {
        wdIndex = context->ptrScanSlots[currSlot].wdId;
        if (0u != Cy_CapSense_IsWidgetEnabled(wdIndex, context))
        {
            snsIndex = context->ptrScanSlots[currSlot].snsId;
            tmpRawCount = ptrHwBase->SNS.RESULT_FIFO_RD;
            ptrSnsCxt = &context->ptrWdConfig[wdIndex].ptrSnsContext[snsIndex];
            ptrSnsCxt->status &= (uint8_t)~CY_CAPSENSE_SNS_OVERFLOW_MASK;
            if (MSCLP_SNS_RESULT_FIFO_RD_OVERFLOW_Msk == (tmpRawCount & MSCLP_SNS_RESULT_FIFO_RD_OVERFLOW_Msk))
            {
                ptrSnsCxt->status |= CY_CAPSENSE_SNS_OVERFLOW_MASK;
            }
            ptrSnsCxt->raw = (uint16_t)tmpRawCount;

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_RC_HW_IIR_FILTER_EN)
                if (0u != context->ptrInternalContext->hwIirInit)
                {
                    ptrSensorFrame[CY_CAPSENSE_SNS_HW_IIR_INDEX] &= ~CY_CAPSENSE_FRC_HW_IIR_FILTER_MASK;
                    ptrSensorFrame[CY_CAPSENSE_SNS_HW_IIR_INDEX] |= (ptrSensorData[CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL3] & CY_CAPSENSE_FRC_HW_IIR_FILTER_MASK);
                }
                else
                {
                    ptrSensorFrame[CY_CAPSENSE_SNS_HW_IIR_INDEX] &= ~CY_CAPSENSE_FRC_HW_IIR_FILTER_MASK;
                    ptrSensorFrame[CY_CAPSENSE_SNS_HW_IIR_INDEX] |= (uint32_t)((uint32_t)ptrSnsCxt->raw << CY_CAPSENSE_BYTE_SHIFT);
                }
            #endif
        }
        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_RC_HW_IIR_FILTER_EN)
            ptrSensorFrame += CY_CAPSENSE_SENSOR_FRAME_SIZE;
            ptrSensorData += CY_MSCLP_11_SNS_REGS;
        #endif
    }
}


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_TransferLpRawCounts
****************************************************************************//**
*
* Transfers raw counts for the scanned low power sensors from internal MSCLP IP
* RAM to the raw count history.
*
* \param startSlotId
* The slot ID transfer will be started from.
*
* \param numberSlots
* The number of slots will be transferred.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_TransferLpRawCounts(
                uint32_t startSlotId,
                uint32_t numberSlots,
                cy_stc_capsense_context_t * context)
{
    MSCLP_Type * ptrHwBase;
    uint32_t lastSlot;
    uint32_t currSlot;
    uint32_t tmpRawCount;
    uint32_t wdIndex;
    uint32_t fifoSize;
    uint32_t i;
    uint8_t wdSnsMethod;
    const cy_stc_capsense_widget_config_t * ptrWdCfg;
    cy_stc_capsense_common_context_t * ptrCommonCxt = context->ptrCommonContext;
    cy_stc_capsense_lp_historic_context_t * ptrHistoricData = context->ptrLpHistoricContext;

    ptrHwBase = context->ptrCommonConfig->ptrChConfig->ptrHwBase;
    lastSlot = startSlotId + numberSlots - 1u;
    fifoSize = ptrHwBase->SNS.RESULT_FIFO_STATUS & MSCLP_SNS_RESULT_FIFO_STATUS_USED_Msk;

    /* Reset baseline after low power scan */
    if ((ptrHwBase->SNS.RESULT_FIFO_STATUS2 & MSCLP_SNS_RESULT_FIFO_STATUS2_FIFO_OVERFLOW_Msk) != 0uL)
    {
        ptrCommonCxt->lpScanSt = CY_CAPSENSE_SCAN_ST_BSLN_RESET_MSK;
    }
    else
    {
        /* Set valid mask for baseline */
        ptrCommonCxt->lpScanSt = CY_CAPSENSE_SCAN_ST_BSLN_RESET_MSK | CY_CAPSENSE_SCAN_ST_BSLN_VALID_MSK;
    }

    ptrCommonCxt->lpFirstSnsId = (uint8_t)startSlotId;
    ptrCommonCxt->lpSnsNumber = (uint8_t)numberSlots;
    ptrCommonCxt->lpNumFrame = (uint8_t)(fifoSize / numberSlots);

    /* Reads raw counts history from MSCv3LP HW internal RAM to pop the FIFO */
    for (i = 0u; i < ptrCommonCxt->lpNumFrame; i++)
    {
        for (currSlot = startSlotId; currSlot <= lastSlot; currSlot++)
        {
            tmpRawCount = ptrHwBase->SNS.RESULT_FIFO_RD & MSCLP_SNS_RESULT_FIFO_RD_RAW_COUNT_Msk;

            wdIndex = context->ptrLpScanSlots[currSlot].wdId;
            if (0u != Cy_CapSense_IsWidgetEnabled(wdIndex, context))
            {
                ptrWdCfg = &context->ptrWdConfig[wdIndex];
                wdSnsMethod = ptrWdCfg->senseMethod;

                if ((CY_CAPSENSE_CSX_GROUP == wdSnsMethod) ||
                    (CY_CAPSENSE_ISX_GROUP == wdSnsMethod))
                {
                    /* Limit raw counts */
                    if (tmpRawCount < ptrWdCfg->ptrWdContext->maxRawCount)
                    {
                        /* Invert raw counts for CSX/ISX widgets */
                        tmpRawCount = (ptrWdCfg->ptrWdContext->maxRawCount - tmpRawCount);
                    }
                    else
                    {
                        tmpRawCount = 0u;
                    }
                }

                *ptrHistoricData = (cy_stc_capsense_lp_historic_context_t)tmpRawCount;
            }
            ptrHistoricData++;
        }
    }
}
#endif


/*******************************************************************************
* Function Name: Cy_CapSense_WaitMrssStatusChange
****************************************************************************//**
*
* Waits till end of MRSS status is changed or till the provided timeout.
*
* \param timeout
* Watchdog timeout in microseconds.
*
* \param mrssStatus
* MRSS status to be set
* - CY_CAPSENSE_MRSS_TURN_ON - MRSS should be turned on
* - CY_CAPSENSE_MRSS_TURN_OFF - MRSS should be turned off
* - CY_CAPSENSE_MRSS_IMO_TURN_ON - MRSS_IMO should be turned on
* - CY_CAPSENSE_MRSS_IMO_TURN_OFF - MRSS_IMO should be turned off
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS       - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_TIMEOUT       - The software watchdog timeout occurred
*                                      during the wait, the MRSS status change was not
*                                      completed.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_WaitMrssStatusChange(
                uint32_t timeout,
                uint32_t mrssStatus,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t status = CY_CAPSENSE_STATUS_SUCCESS;
    uint32_t waitTime = timeout;
    uint32_t mrssMask = MSCLP_MRSS_STATUS_MRSS_UP_Msk;
    uint32_t mrssStatusLocal = mrssStatus;

    if ((CY_CAPSENSE_MRSS_IMO_TURN_ON == mrssStatus) || (CY_CAPSENSE_MRSS_IMO_TURN_OFF == mrssStatus))
    {
        mrssMask = MSCLP_MRSS_STATUS_IMO_UP_Msk;
        mrssStatusLocal = (mrssStatusLocal & 0x1u) << MSCLP_MRSS_STATUS_IMO_UP_Pos;
    }

    while (mrssStatusLocal == (context->ptrCommonConfig->ptrChConfig->ptrHwBase->MRSS_STATUS & mrssMask))
    {
        if (0uL == waitTime)
        {
            status = CY_CAPSENSE_STATUS_TIMEOUT;
            break;
        }
        /* Delay for 1us */
        Cy_SysLib_DelayUs(1u);
        waitTime--;
    }

    return status;
}


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_RC_HW_IIR_FILTER_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_ScanInitializeHwIirAllSlots
****************************************************************************//**
*
* Initializes (or re-initializes) the hardware IIR filter for all slots.
*
* This function initiates the blocking scan of all slots to initialize
* the hardware IIR filter. This should be done before firmware filters and 
* baselines initialization.
*
* Calling this function is accompanied by:
* * Cy_CapSense_InitializeAllFilters()
* * Cy_CapSense_InitializeAllBaselines()
* * Cy_CapSense_InitializeAllStatuses()
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - The input parameter is invalid.
* - CY_CAPSENSE_STATUS_HW_BUSY          - The HW is busy with the previous scan.
* - CY_CAPSENSE_STATUS_TIMEOUT          - The software watchdog timeout occurred
*                                         during the scan, the scan was not completed.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ScanInitializeHwIirAllSlots(
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t result;

    result = Cy_CapSense_ScanInitializeHwIirSlots(0u, CY_CAPSENSE_SLOT_COUNT, context);

    return result;
}


/*******************************************************************************
* Function Name: Cy_CapSense_ScanInitializeHwIirSlots
****************************************************************************//**
*
* Initializes (or re-initializes) the hardware IIR filter for specified slots.
*
* This function initiates the blocking scan of specified slots to initialize
* the hardware IIR filter. This should be done before firmware filters and
* baselines initialization.
*
* Calling this function is accompanied by:
* * Cy_CapSense_InitializeWidgetFilter()
* * Cy_CapSense_InitializeWidgetBaseline()
* * Cy_CapSense_InitializeWidgetStatus()
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param startSlotId
* The slot ID initialization will be started from.
*
* \param numberSlots
* The number of slots will be initialized.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - The input parameter is invalid.
* - CY_CAPSENSE_STATUS_HW_BUSY          - The HW is busy with the previous scan.
* - CY_CAPSENSE_STATUS_TIMEOUT          - The software watchdog timeout occurred
*                                         during the scan, the scan was not completed.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ScanInitializeHwIirSlots(
                uint32_t startSlotId,
                uint32_t numberSlots,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t result = CY_CAPSENSE_STATUS_SUCCESS;
    MSCLP_Type * ptrHwBase = context->ptrCommonConfig->ptrChConfig->ptrHwBase;
    uint32_t watchdog = 0u;
    uint32_t slotIdx;

    /* Disable HW IP to allow MRSS operations */
    ptrHwBase->CTL &= (~MSCLP_CTL_ENABLED_Msk);

    /* Check for system VDDA value and enable PUMP if VDDA is less then threshold */
    #if (CY_MSCLP_VDDA_PUMP_TRESHOLD > CY_CAPSENSE_VDDA_MV)
        ptrHwBase->PUMP_CTL = MSCLP_PUMP_CTL_PUMP_MODE_Msk;
    #else
        ptrHwBase->PUMP_CTL = 0x00u;
    #endif

    /* Check if IMO is running */
    if (0u == (context->ptrCommonConfig->ptrChConfig->ptrHwBase->MRSS_STATUS & MSCLP_MRSS_STATUS_MRSS_UP_Msk))
    {
        /* Enable only REF and IMO to provide access to the SNS_STC registers */
        ptrHwBase->MRSS_CMD = MSCLP_MRSS_CMD_MRSS_START_Msk;
        (void)Cy_CapSense_WaitMrssStatusChange(
                        CY_MSCLP_CLK_LF_PERIOD_MAX * CY_MSCLP_MRSS_TIMEOUT_SMALL,
                        CY_CAPSENSE_MRSS_TURN_ON, context);
    }

    /* Initialize the hardware raw count filter */
    ptrHwBase->SNS.CE_INIT_CTL |= MSCLP_SNS_CE_INIT_CTL_SENSOR_INIT_Msk;

    result |= Cy_CapSense_ScanSlots(startSlotId, numberSlots, context);

    for (slotIdx = startSlotId; slotIdx < (startSlotId + numberSlots); slotIdx++)
    {
        watchdog += Cy_CapSense_GetScanWatchdogTime(context->ptrScanSlots[slotIdx].wdId, slotIdx, context);
    }
    result |= Cy_CapSense_WaitEndScan(watchdog, context);

    return result;
}
#endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_RC_HW_IIR_FILTER_EN) */


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_GetCIC2SamplesMax
****************************************************************************//**
*
* This internal function determines the MAX number of CIC2 samples for specified
* decimation rate that can be accumulated in the internal CIC2 HW register
* with no overflow.
*
* \param cic2Rate
* CIC2 decimation rate.
*
* \return
* The MAX allowed number of CIC2 samples.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetCIC2SamplesMax(
                uint32_t cic2Rate)
{
    uint32_t retVal;

    retVal = CY_CAPSENSE_CIC2_ACC_MAX_VAL / (cic2Rate * cic2Rate);

    return retVal;
}


/*******************************************************************************
* Function Name: Cy_CapSense_GetCIC2HwDivider
****************************************************************************//**
*
* This internal function determines the value of the divider that will be
* applied to the data, accumulated by the CIC2 HW for the specified number of
* samples.
*
* \param cic2Samples
* The number of valid (FullNumber - 1) CIC2 samples for the specified sensing
* parameters. This value can be obtained by using the Cy_CapSense_GetCIC2SamplesNum
* function.
*
* \return
* The CIC2 HW divider value.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetCIC2HwDivider(
                uint32_t cic2Samples)
{
    uint32_t cic2Divider;

    cic2Divider = 1uL << Cy_CapSense_GetCIC2HwShift(cic2Samples);

    if (CY_CAPSENSE_CIC2_DIVIDER_MAX < cic2Divider)
    {
        cic2Divider = CY_CAPSENSE_CIC2_DIVIDER_MAX;
    }

    return cic2Divider;
}


/*******************************************************************************
* Function Name: Cy_CapSense_GetCIC2HwShift
****************************************************************************//**
*
* This internal function determines the value of the shift that will be
* applied to the data, accumulated by the CIC2 HW for the specified number of
* samples.
*
* \param cic2Samples
* The number of valid (FullNumber - 1) CIC2 samples for the specified sensing
* parameters. This value can be obtained by using the Cy_CapSense_GetCIC2SamplesNum
* function.
*
* \return
* The CIC2 HW Shift value.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetCIC2HwShift(
                uint32_t cic2Samples)
{
    uint32_t cic2Shift = 0u;

    while (cic2Samples > (1uL << cic2Shift))
    {
        cic2Shift++;
    }

    if (CY_CAPSENSE_CIC2_SHIFT_MAX < cic2Shift)
    {
        cic2Shift = CY_CAPSENSE_CIC2_SHIFT_MAX;
    }

    return cic2Shift;
}


#if (CY_CAPSENSE_CIC2_FILTER_AUTO_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_InitializeCic2Shift
****************************************************************************//**
*
* Performs the auto-selection of CIC2 HW filter Shift parameter.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS      - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_TIMEOUT      - A timeout reached during the scan time measurement.
* - CY_CAPSENSE_STATUS_BAD_PARAM    - Not valid input parameter.
* - CY_CAPSENSE_STATUS_HW_BUSY      - The MSCLP HW block is busy and cannot be
*                                     switched to another mode.
* - CY_CAPSENSE_STATUS_BAD_CONFIG   - The parameters are out of specified range.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_InitializeCic2Shift(
                cy_stc_capsense_context_t * context)
{
    uint32_t wdIndex;
    uint32_t scanSlotId;
    uint32_t tmpVal;
    uint32_t tmpShift;
    uint32_t tmpSample;
    cy_capsense_status_t retVal = CY_CAPSENSE_STATUS_SUCCESS;

    cy_stc_capsense_widget_context_t * ptrWdCxt;
    const cy_stc_capsense_widget_config_t * ptrWdCfg = context->ptrWdConfig;

    for (wdIndex = 0u; wdIndex < CY_CAPSENSE_TOTAL_WIDGET_COUNT; wdIndex++)
    {
        if (0u != Cy_CapSense_IsWidgetEnabled(wdIndex, context))
        {
            ptrWdCxt = ptrWdCfg->ptrWdContext;

            if (0u != (ptrWdCxt->cicShift & CY_CAPSENSE_CIC_AUTO_MASK))
            {
                scanSlotId = ptrWdCfg->firstSlotId;

                /* Obtain the scan duration in terms of Mod Clock cycles. */
                retVal |= Cy_CapSense_ExecuteSaturatedScan(&tmpVal, wdIndex, scanSlotId, CY_CAPSENSE_SATURATED_SCAN_TIME, context);
                /* Obtain the number of valid (FullNumber - 1) CIC2 samples */
                tmpSample = (tmpVal / ptrWdCxt->cicRate) - 1u;
                tmpShift = Cy_CapSense_GetCIC2HwShift(tmpSample);
                tmpVal >>= tmpShift;
                tmpVal *= ptrWdCfg->numChopCycles;
                if (CY_CAPSENSE_16_BIT_MASK < tmpVal)
                {
                    tmpShift++;
                }
                ptrWdCxt->cicShift = (uint8_t)tmpShift;
                ptrWdCxt->cicShift |= CY_CAPSENSE_CIC_AUTO_MASK;
            }

            #if ((CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_MATRIX_EN) || \
                (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CSD_TOUCHPAD_EN))
                if ((CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod) &&
                    (((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == ptrWdCfg->wdType) ||
                    ((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == ptrWdCfg->wdType)))
                {
                    if (0u != (ptrWdCxt->rowCicShift & CY_CAPSENSE_CIC_AUTO_MASK))
                    {
                        scanSlotId = (uint32_t)ptrWdCfg->firstSlotId + ptrWdCfg->numCols;

                        /* Obtain the scan duration in terms of Mod Clock cycles. */
                        retVal |= Cy_CapSense_ExecuteSaturatedScan(&tmpVal, wdIndex, scanSlotId, CY_CAPSENSE_SATURATED_SCAN_TIME, context);
                        /* Obtain the number of valid (FullNumber - 1) CIC2 samples */
                        tmpSample = (tmpVal / ptrWdCxt->cicRate) - 1u;
                        tmpShift = Cy_CapSense_GetCIC2HwShift(tmpSample);
                        tmpVal >>= tmpShift;
                        tmpVal *= ptrWdCfg->numChopCycles;
                        if (CY_CAPSENSE_16_BIT_MASK < tmpVal)
                        {
                            tmpShift++;
                        }
                        ptrWdCxt->rowCicShift = (uint8_t)tmpShift;
                        ptrWdCxt->rowCicShift |= CY_CAPSENSE_CIC_AUTO_MASK;
                    }
                }
            #endif
        }
        ptrWdCfg++;
    }

    /* Update Active frame configuration with new calculated CIC2 shift value. */
    Cy_CapSense_GenerateAllSensorConfig(CY_CAPSENSE_SNS_FRAME_ACTIVE, context);

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        /* Update LP frame configuration with new calculated CIC2 shift value. */
        Cy_CapSense_GenerateAllSensorConfig(CY_CAPSENSE_SNS_FRAME_LOW_POWER, context);
    #endif /* CY_CAPSENSE_LP_EN */

    /* Resetting the HW configuration in order to trigger the base frame initialization in scope of the
     * next  Cy_CapSense_SwitchHwConfiguration() function call with the desired HW configuration.
     */
    if (CY_CAPSENSE_STATUS_SUCCESS == retVal)
    {
        retVal |= Cy_CapSense_SwitchHwConfiguration(CY_CAPSENSE_HW_CONFIG_CAPTURED_DEFAULT, context);
    }

    if (CY_CAPSENSE_STATUS_SUCCESS == retVal)
    {
        retVal |= Cy_CapSense_SwitchHwConfiguration(CY_CAPSENSE_HW_CONFIG_REGULAR_SCANNING, context);
    }

    return retVal;
}
#endif /* #if (CY_CAPSENSE_CIC2_FILTER_AUTO_EN) */


#if (CY_CAPSENSE_CIC_RATE_MODE_AUTO_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_InitializeCic2Rate
****************************************************************************//**
*
* Performs the auto-selection of CIC2 HW filter Decimation Rate parameter.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS      - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_TIMEOUT      - A timeout reached during the scan time measurement.
* - CY_CAPSENSE_STATUS_BAD_PARAM    - Not valid input parameter.
* - CY_CAPSENSE_STATUS_HW_BUSY      - The MSCLP HW block is busy and cannot be
*                                     switched to another mode.
* - CY_CAPSENSE_STATUS_BAD_CONFIG   - The parameters are out of specified range.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_InitializeCic2Rate(
                cy_stc_capsense_context_t * context)
{
    uint32_t wdIndex;
    uint32_t scanSlotId;
    uint32_t sampleOverflow;
    uint32_t scanTime;
    uint32_t tmpVal;
    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_MATRIX_EN) || \
        (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_TOUCHPAD_EN))
        uint32_t tmpValRow;
    #endif
    cy_capsense_status_t retVal = CY_CAPSENSE_STATUS_SUCCESS;

    cy_stc_capsense_widget_context_t * ptrWdCxt;
    const cy_stc_capsense_widget_config_t * ptrWdCfg = context->ptrWdConfig;

    for (wdIndex = 0u; wdIndex < CY_CAPSENSE_TOTAL_WIDGET_COUNT; wdIndex++)
    {
        if (0u != Cy_CapSense_IsWidgetEnabled(wdIndex, context))
        {
            if ((CY_CAPSENSE_CIC_RATE_MODE_AUTO == ptrWdCfg->cicRateMode))
            {
                ptrWdCxt = ptrWdCfg->ptrWdContext;
                scanSlotId = ptrWdCfg->firstSlotId;

                /* Obtain the scan duration in terms of Mod Clock cycles */
                retVal |= Cy_CapSense_ExecuteSaturatedScan(&tmpVal, wdIndex, scanSlotId, CY_CAPSENSE_SATURATED_SCAN_TIME, context);

                #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_MATRIX_EN) || \
                    (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_TOUCHPAD_EN))
                    if ((CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod) &&
                        (((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == ptrWdCfg->wdType) ||
                        ((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == ptrWdCfg->wdType)))
                    {
                        scanSlotId = (uint32_t)ptrWdCfg->firstSlotId + ptrWdCfg->numCols;
                        /* Obtain the scan duration in terms of Mod Clock cycles. */
                        retVal |= Cy_CapSense_ExecuteSaturatedScan(&tmpValRow, wdIndex, scanSlotId, CY_CAPSENSE_SATURATED_SCAN_TIME, context);
                        if (tmpValRow < tmpVal)
                        {
                            tmpVal = tmpValRow;
                        }
                    }
                #endif

                scanTime = tmpVal;

                /* Phase 1 */
                tmpVal /= (CY_CAPSENSE_CIC2_MIN_VALID_SAMPLES + 1u);
                if (0u == tmpVal)
                {
                    tmpVal = 1u;
                }
                if (CY_CAPSENSE_MAX_DECIMATION_RATE > tmpVal)
                {
                    ptrWdCxt->cicRate = (uint8_t)tmpVal;
                }
                else
                {
                    /* Phase 2 */
                    tmpVal = CY_CAPSENSE_MAX_DECIMATION_RATE;
                    sampleOverflow = (scanTime / CY_CAPSENSE_MAX_DECIMATION_RATE) - 1u;

                    if ((CY_CAPSENSE_CIC2_MAX_VALID_SAMPLES / ptrWdCfg->numChopCycles) >= sampleOverflow)
                    {
                        ptrWdCxt->cicRate = (uint8_t)CY_CAPSENSE_MAX_DECIMATION_RATE;
                    }
                    else
                    {
                        /* Phase 3 */
                        ptrWdCxt->cicRate = (uint8_t)(((uint32_t)CY_CAPSENSE_25_BIT_MASK / ptrWdCfg->numChopCycles) / (scanTime - 1u));
                        if (0u == ptrWdCxt->cicRate)
                        {
                            retVal = CY_CAPSENSE_STATUS_BAD_CONFIG;
                            ptrWdCxt->cicRate = 1u;
                        }
                    }
                }
            }
        }
        ptrWdCfg++;
    }

    /* Update Active frame configuration with new calculated CIC2 decimation value. */
    Cy_CapSense_GenerateAllSensorConfig(CY_CAPSENSE_SNS_FRAME_ACTIVE, context);

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        /* Update LP frame configuration with new calculated CIC2 decimation value. */
        Cy_CapSense_GenerateAllSensorConfig(CY_CAPSENSE_SNS_FRAME_LOW_POWER, context);
    #endif /* CY_CAPSENSE_LP_EN */

    /* Resetting the HW configuration in order to trigger the base frame initialization in scope of the
     * next  Cy_CapSense_SwitchHwConfiguration() function call with the desired HW configuration.
     */
    if (CY_CAPSENSE_STATUS_SUCCESS == retVal)
    {
        retVal |= Cy_CapSense_SwitchHwConfiguration(CY_CAPSENSE_HW_CONFIG_CAPTURED_DEFAULT, context);
    }

    if (CY_CAPSENSE_STATUS_SUCCESS == retVal)
    {
        retVal |= Cy_CapSense_SwitchHwConfiguration(CY_CAPSENSE_HW_CONFIG_REGULAR_SCANNING, context);
    }

    return retVal;
}
#endif /* #if (CY_CAPSENSE_CIC2_FILTER_AUTO_EN) */
#endif /* #if (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CIC2_FILTER_EN) */


/*******************************************************************************
* Function Name: Cy_CapSense_RepeatScan
****************************************************************************//**
*
* Triggers the scan of the frame, which is already configured in the MSCLP
* HW block. The function is available only for the single-channel solution.
*
* The function repeats the frame scan last configured and
* triggered by the Cy_CapSense_ScanSlots() or Cy_CapSense_ScanLpSlots()
* functions.
*
* The function can be used only with the following limitations:
* - the previous scan is completed;
* - the scan frame to repeat consists of less than 37 sensors;
* - there were regular scans previously performed, not BIST or calibration
*   or SmartSense scans.
*
* The function can be used as many times as needed.
*
* \note
* The function is available only for the fifth-generation
* low power CAPSENSE&trade;.
*
* \param context
* The pointer to the CAPSENSE&trade; context
* structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed
*                                         successfully.
* - CY_CAPSENSE_STATUS_INVALID_STATE    - The previous scan is not completed or
*                                         it was a specific scan (BIST,
*                                         SmartSense, etc.) and the MSCLP HW
*                                         configuration was changed.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_RepeatScan(cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_INVALID_STATE;

    if ((CY_CAPSENSE_BUSY != Cy_CapSense_IsBusy(context)) &&
        (CY_CAPSENSE_ENABLE == context->ptrInternalContext->repeatScanEn))
    {
        Cy_CapSense_SetBusyFlags(context);
        context->ptrInternalContext->currentSlotIndex = context->ptrInternalContext->startSlotIndex;
        context->ptrCommonConfig->ptrChConfig->ptrHwBase->CTL |= MSCLP_CTL_ENABLED_Msk;

        #if (CY_CAPSENSE_DISABLE == CY_CAPSENSE_EXT_FRM_START_EN)
            context->ptrCommonConfig->ptrChConfig->ptrHwBase->WAKEUP_CMD = MSCLP_WAKEUP_CMD_START_FRAME_AOS_Msk;
        #endif

        capStatus = CY_CAPSENSE_STATUS_SUCCESS;
    }

    return capStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_SetupCpuOperatingMode
****************************************************************************//**
*
* Configures the MSCLP HW block for operation in the CPU operating mode.
* Use the Cy_CapSense_StartCpuScan() function to trigger scan in the CPU operating
* mode. The end of the scan in the CPU operating mode can be detected by using the
* Cy_CapSense_WaitEndOfCpuScan() function.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_SetupCpuOperatingMode(cy_stc_capsense_context_t * context)
{
    MSCLP_Type * ptrHwBase = context->ptrCommonConfig->ptrChConfig->ptrHwBase;

    /* Disable HW IP to allow MRSS operations */
    ptrHwBase->CTL &= (~MSCLP_CTL_ENABLED_Msk);

    /* Check for system VDDA value and enable PUMP if VDDA is less then threshold */
    #if (CY_MSCLP_VDDA_PUMP_TRESHOLD > CY_CAPSENSE_VDDA_MV)
        ptrHwBase->PUMP_CTL = MSCLP_PUMP_CTL_PUMP_MODE_Msk;
    #else
        ptrHwBase->PUMP_CTL = 0x00u;
    #endif

    /* Check if IMO is running for the calibration operation */
    if (0u == (context->ptrCommonConfig->ptrChConfig->ptrHwBase->MRSS_STATUS & MSCLP_MRSS_STATUS_MRSS_UP_Msk))
    {
        /* Enable only REF and IMO to provide access to the SNS_STC registers */
        ptrHwBase->MRSS_CMD = MSCLP_MRSS_CMD_MRSS_START_Msk;
        (void)Cy_CapSense_WaitMrssStatusChange(
                        CY_MSCLP_CLK_LF_PERIOD_MAX * CY_MSCLP_MRSS_TIMEOUT_SMALL,
                        CY_CAPSENSE_MRSS_TURN_ON, context);
    }

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_EXT_FRM_START_EN)
        /* Clear the external start scan mode */
        ptrHwBase->CTL &= ~MSCLP_CTL_EXT_FRAME_START_MODE_Msk;
    #endif

    /* Enable HW IP to allow a scan frame start */
    ptrHwBase->CTL |= MSCLP_CTL_ENABLED_Msk;

    /* Disable HW processing */
    ptrHwBase->CE_CTL = 0x00u;

    /* Disable all interrupts */
    ptrHwBase->INTR_LP_MASK = 0x00u;
    (void)ptrHwBase->INTR_LP_MASK;

    /* Clear all pending interrupts */
    ptrHwBase->INTR_LP = CY_CAPSENSE_MSCLP_INTR_LP_ALL_MSK;
    (void)ptrHwBase->INTR_LP;
    ptrHwBase->INTR = CY_CAPSENSE_MSCLP_INTR_ALL_MSK;
    (void)ptrHwBase->INTR;

    /* Set CPU operating mode */
    context->ptrInternalContext->operatingMode = CY_CAPSENSE_CTL_OPERATING_MODE_CPU;
    CY_REG32_CLR_SET(ptrHwBase->CTL, MSCLP_CTL_OPERATING_MODE, CY_CAPSENSE_CTL_OPERATING_MODE_CPU);

    /* Set raw counts to store to FIFO */
    CY_REG32_CLR_SET(ptrHwBase->SCAN_CTL1, MSCLP_SCAN_CTL1_RC_STORE_EN, CY_CAPSENSE_ENABLE);
}


/*******************************************************************************
* Function Name: Cy_CapSense_StartCpuScan
****************************************************************************//**
*
* Sets configuration of sensor frame registers of the MSCLP HW block and
* starts the scan. The end of the scan in the CPU operating mode can be detected
* by using the Cy_CapSense_WaitEndOfCpuScan() function.
*
* \note Call the Cy_CapSense_SetupCpuOperatingMode() function to switch the
* MSCLP HW block to the CPU operating mode before triggering CPU scan by using
* the Cy_CapSense_StartCpuScan() routine.
*
* \param scanConfig
* The pointer to a scan configuration structure.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_StartCpuScan(const uint32_t * scanConfig, cy_stc_capsense_context_t * context)
{
    MSCLP_Type * ptrHwBase = context->ptrCommonConfig->ptrChConfig->ptrHwBase;

    /* Enable HW IP */
    ptrHwBase->CTL |= MSCLP_CTL_ENABLED_Msk;

    /* Clear all pending interrupts */
    ptrHwBase->INTR_LP = CY_CAPSENSE_MSCLP_INTR_LP_ALL_MSK;
    (void)ptrHwBase->INTR_LP;
    ptrHwBase->INTR = CY_CAPSENSE_MSCLP_INTR_ALL_MSK;
    (void)ptrHwBase->INTR;

    /* Set sensor config registers (frame) */
    Cy_MSCLP_ConfigureScan(ptrHwBase, CY_MSCLP_6_SNS_REGS, scanConfig);

    /* Configure the last slot */
    ptrHwBase->SNS.SNS_CTL |= MSCLP_SNS_SNS_CTL_LAST_Msk | MSCLP_SNS_SNS_CTL_VALID_Msk;

    /* Start scanning with START_SCAN */
    ptrHwBase->SNS.SNS_CTL |= MSCLP_SNS_SNS_CTL_START_SCAN_Msk;

    /* Start FSM with START_FRAME */
    ptrHwBase->SNS.FRAME_CMD = MSCLP_SNS_FRAME_CMD_START_FRAME_Msk;
}


/*******************************************************************************
* Function Name: Cy_CapSense_WaitEndOfCpuScan
****************************************************************************//**
*
* This internal function checks for the scan status. If the scan ends before
* the software watch-dog triggering, the function returns a non-zero watch-dog
* cycles number. If the software watch-dog triggers during the scan,
* the function returns zero.
*
* Use the Cy_CapSense_GetScanWatchdogTime() or Cy_CapSense_CalcSampleWatchdogTime()
* function to calculate the watchdog time in microseconds for the scan with the
* specified parameters.
*
* \param watchdogTime
* A watch-dog time interval in microseconds.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns watch-dog counter. If it is equal to zero, it means timeout happened.
*
*******************************************************************************/
uint32_t Cy_CapSense_WaitEndOfCpuScan(uint32_t watchdogTime, cy_stc_capsense_context_t * context)
{
    uint32_t tmpVal;
    const uint32_t cpuCyclesPerLoop = 5u;
    MSCLP_Type * ptrHwBase = context->ptrCommonConfig->ptrChConfig->ptrHwBase;

    tmpVal = context->ptrCommonConfig->cpuClkHz / CY_CAPSENSE_CONVERSION_MEGA;
    tmpVal = Cy_CapSense_WatchdogCyclesNum(watchdogTime, tmpVal, cpuCyclesPerLoop);

    while ((ptrHwBase->INTR & MSCLP_INTR_MASK_SCAN_Msk) == 0u)
    {
        if (0uL == tmpVal)
        {
            break;
        }
        tmpVal--;
    }

    /* Clear all pending interrupts */
    ptrHwBase->INTR = CY_CAPSENSE_MSCLP_INTR_ALL_MSK;
    (void)ptrHwBase->INTR;
    return tmpVal;
}


/*******************************************************************************
* Function Name: Cy_CapSense_ExecuteSaturatedScan
****************************************************************************//**
*
* This internal function executes a scan with the saturated channel to obtain
* the MAX raw count or the scan duration for the specified scan slot.
*
* \param ptrMaxRaw
* Specifies the pointer to store the resulting MAX raw count value or scan
* time in Mod Clock cycles.
*
* \param widgetId
* Specifies the ID number of the widget. A macro for the widget ID can be found
* in the cycfg_capsense.h file defined as CY_CAPSENSE_<WIDGET_NAME>_WDGT_ID.
*
* \param scanSlotId
* The slot ID scans will be done for.
*
* \param mode
* Saturated scan execution mode:
* - CY_CAPSENSE_SATURATED_MAX_COUNT   - Used to obtain the MAX raw count.
* - CY_CAPSENSE_SATURATED_SCAN_TIME   - Used to obtain the scan duration in terms of Mod Clock cycles.
*
* \param context
* The pointer to the context structure allocated by the user or middleware.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS      - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_TIMEOUT      - A timeout reached during the scan time measurement.
* - CY_CAPSENSE_STATUS_BAD_PARAM    - Not valid input parameter.
* - CY_CAPSENSE_STATUS_HW_BUSY      - The MSCLP HW block is busy and cannot be
*                                     switched to another mode.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_ExecuteSaturatedScan(
                uint32_t * ptrMaxRaw,
                uint32_t widgetId,
                uint32_t scanSlotId,
                uint32_t mode,
                cy_stc_capsense_context_t * context)
{
    uint32_t tmpVal;
    uint32_t slotFrameIdx;
    uint32_t * ptrSnsFrame;
    uint32_t scanConfigTmp[CY_MSCLP_6_SNS_REGS];
    cy_stc_capsense_widget_config_t const * ptrWdCfg = &context->ptrWdConfig[widgetId];
    cy_capsense_status_t status;

    MSCLP_Type * ptrHwBase = context->ptrCommonConfig->ptrChConfig->ptrHwBase;

    #if (CY_CAPSENSE_DISABLE == CY_CAPSENSE_CIC2_FILTER_EN)
        uint32_t kref;
        uint32_t epiCounts;
        uint32_t epiKrefDelay;
    #endif

    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN) && \
        ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_AUTO_EN) || (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC_RATE_MODE_AUTO_EN)))
        uint32_t shiftTemp= 0u;
    #endif

    #if ((CY_CAPSENSE_DISABLE == CY_CAPSENSE_CIC2_FILTER_EN) || ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN) && \
        ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_AUTO_EN) || (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC_RATE_MODE_AUTO_EN))))
        cy_stc_capsense_widget_context_t * ptrWdCxt = &context->ptrWdContext[widgetId];
    #endif

    (void)mode;

    /* Configures the MSCLP HW block for operation with the permanently saturated channel. */
    status = Cy_CapSense_SwitchHwConfiguration(CY_CAPSENSE_HW_CONFIG_CHANNEL_SATURATION, context);

    /* Obtain the scan parameters offset in the cy_capsense_sensorFrameContext[]
     * array for the slots that are part of Active widgets.
     */
    slotFrameIdx = scanSlotId * CY_CAPSENSE_SENSOR_FRAME_SIZE;
    ptrSnsFrame = &context->ptrSensorFrameContext[slotFrameIdx];

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        if (ptrWdCfg->wdType == (uint8_t)CY_CAPSENSE_WD_LOW_POWER_E)
        {
            /* Obtain the scan parameters offset in the cy_capsense_sensorFrameContext[]
             * array for the slots that are part of Low power widgets.
             */
            slotFrameIdx  = scanSlotId * CY_MSCLP_11_SNS_REGS;
            slotFrameIdx += CY_CAPSENSE_FRM_LP_SNS_SW_SEL_CSW_LO_MASK2_INDEX;
            ptrSnsFrame = &context->ptrSensorFrameLpContext[slotFrameIdx];
        }
    #endif

    /* The measurement with a saturated channel will be performed with all the sensors disconnected.
     * The code below sets up the configuration of the LO_MASK registers with 0x00000000u.
     * The SW_SEL_CSW_FUNC[0u] is configured in the scope of the Cy_CapSense_ConfigureSaturationMode()
     * routine with all the switches open.
     */
    scanConfigTmp[CY_CAPSENSE_SNS_SW_SEL_CSW_LO_MASK2_INDEX] = 0x00u; /* Set up the SNS_SW_SEL_CSW_LO_MASK2 register configuration. */
    scanConfigTmp[CY_CAPSENSE_SNS_SW_SEL_CSW_LO_MASK1_INDEX] = 0x00u; /* Set up the SNS_SW_SEL_CSW_LO_MASK1 register configuration. */
    scanConfigTmp[CY_CAPSENSE_SNS_SW_SEL_CSW_LO_MASK0_INDEX] = 0x00u; /* Set up the SNS_SW_SEL_CSW_LO_MASK0 register configuration. */

    /* The code below sets up configuration of the sense control registers. */
    scanConfigTmp[CY_CAPSENSE_SNS_SCAN_CTL_INDEX] = ptrSnsFrame[CY_CAPSENSE_SNS_SCAN_CTL_INDEX]; /* Set up the SNS_SCAN_CTL register configuration. */
    scanConfigTmp[CY_CAPSENSE_SNS_CDAC_CTL_INDEX] = ptrSnsFrame[CY_CAPSENSE_SNS_CDAC_CTL_INDEX]; /* Set up the SNS_CDAC_CTL register configuration. */
    scanConfigTmp[CY_CAPSENSE_SNS_CTL_INDEX] = ptrSnsFrame[CY_CAPSENSE_SNS_CTL_INDEX]; /* Set up the SNS_CTL register configuration. */

    /* Disable system chopping */
    scanConfigTmp[CY_CAPSENSE_SNS_SCAN_CTL_INDEX] &= ~MSCLP_SNS_SNS_SCAN_CTL_NUM_CONV_Msk;

    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN) && \
        ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_AUTO_EN) || (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC_RATE_MODE_AUTO_EN)))
        if (CY_CAPSENSE_SATURATED_SCAN_TIME == mode)
        {
            /* Disable the CIC2 shift and set the decimation rate to 1 (DECIM_RATE = 0) to increment the
             * CIC2 accumulator each Mod Clock cycle and then copy the result to FIFO without shifting.
             * The final value in the FIFO fill is the equal number of Mod Clock cycles per scan minus 1 because
             * the first CIC2 sample is invalid and will be skipped. This skipped Mod Clock cycle will be considered
             * at the end of this function.
             */
            scanConfigTmp[CY_CAPSENSE_SNS_SCAN_CTL_INDEX] &= (uint32_t)(~MSCLP_SNS_SNS_SCAN_CTL_CIC2_SHIFT_Msk);
            scanConfigTmp[CY_CAPSENSE_SNS_CTL_INDEX] &= (uint32_t)(~MSCLP_SNS_SNS_CTL_DECIM_RATE_Msk);

            /* In case Max Rawcount are going to be overflowed let's use CIC2 shift */
            shiftTemp = 0u;
            tmpVal = ptrWdCxt->snsClk;
            if (tmpVal < ptrWdCxt->rowSnsClk)
            {
                tmpVal = ptrWdCxt->rowSnsClk;
            }
            tmpVal *= ptrWdCxt->numSubConversions;
            if (CY_CAPSENSE_CLK_SOURCE_PRS == ((uint32_t)ptrWdCxt->snsClkSource & CY_CAPSENSE_CLK_SOURCE_MASK))
            {
                tmpVal <<= 1u;
            }
            while ((tmpVal >> shiftTemp) > CY_CAPSENSE_16_BIT_MASK)
            {
                shiftTemp++;
            }
            if (CY_CAPSENSE_CIC2_SHIFT_MAX < shiftTemp)
            {
                status = CY_CAPSENSE_STATUS_CONFIG_OVERFLOW;
            }
            /* Consider System Chopping for overflow */
            tmpVal <<= (ptrWdCfg->numChopCycles - 1u);
            if (CY_CAPSENSE_25_BIT_MASK < tmpVal)
            {
                status = CY_CAPSENSE_STATUS_CONFIG_OVERFLOW;
            }
            scanConfigTmp[CY_CAPSENSE_SNS_SCAN_CTL_INDEX] |= (uint32_t)(shiftTemp << MSCLP_SNS_SNS_SCAN_CTL_CIC2_SHIFT_Pos);
        }
    #endif

    if (status == CY_CAPSENSE_STATUS_SUCCESS)
    {
        /* Initiate the scan in the CPU operating mode. */
        Cy_CapSense_StartCpuScan((const uint32_t *)scanConfigTmp, context);

        tmpVal = Cy_CapSense_GetScanWatchdogTime(widgetId, scanSlotId, context);
        tmpVal = Cy_CapSense_WaitEndOfCpuScan(tmpVal, context);

        if (0u == tmpVal)
        {
            status |= CY_CAPSENSE_STATUS_TIMEOUT;
        }
    }

    tmpVal = (ptrHwBase->SNS.RESULT_FIFO_RD & MSCLP_SNS_RESULT_FIFO_RD_RAW_COUNT_Msk) >>
            MSCLP_SNS_RESULT_FIFO_RD_RAW_COUNT_Pos;

    /* Disable HW IP */
    ptrHwBase->CTL &= (~MSCLP_CTL_ENABLED_Msk);

    *ptrMaxRaw = CY_CAPSENSE_16_BIT_MASK;

    #if (CY_CAPSENSE_DISABLE == CY_CAPSENSE_CIC2_FILTER_EN)

        epiKrefDelay = CY_CAPSENSE_NUM_EPI_KREF_DELAY;
        kref = ((scanConfigTmp[CY_CAPSENSE_SNS_CTL_INDEX] & MSCLP_SNS_SNS_CTL_SENSE_DIV_Msk) >> MSCLP_SNS_SNS_CTL_SENSE_DIV_Pos) + 1u;
        if (CY_CAPSENSE_CLK_SOURCE_PRS == ((uint32_t)ptrWdCxt->snsClkSource & CY_CAPSENSE_CLK_SOURCE_MASK))
        {
            epiKrefDelay = CY_CAPSENSE_NUM_EPI_KREF_DELAY_PRS;
        }
        epiCounts = epiKrefDelay * ((kref + 3u) >> 2u);
        if (CY_CAPSENSE_CLK_SOURCE_PRS == ((uint32_t)ptrWdCxt->snsClkSource & CY_CAPSENSE_CLK_SOURCE_MASK))
        {
            if ((CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod) || (CY_CAPSENSE_ISX_GROUP == ptrWdCfg->senseMethod))
            {
                kref <<= 1u;
            }
        }
        if (0uL == (kref & 0x01uL))
        {
            epiCounts--;
        }
        tmpVal -= epiCounts;
        tmpVal *= ptrWdCfg->numChopCycles;
        if (tmpVal <= CY_CAPSENSE_16_BIT_MASK)
        {
            *ptrMaxRaw = (uint16_t)tmpVal;
        }

    #elif ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN) && \
          ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_AUTO_EN) || (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC_RATE_MODE_AUTO_EN)))

        if (CY_CAPSENSE_SATURATED_SCAN_TIME == mode)
        {
            tmpVal <<= shiftTemp;
            /* The final value in the FIFO fill is the equal number of Mod Clock cycles per scan minus 1 because
             * the first CIC2 sample is invalid and is always skipped. The code below takes into account this skipped
             * Mod Clock cycle.
             */
            tmpVal++;
            *ptrMaxRaw = tmpVal;
        }
        else
        {
            tmpVal *= ptrWdCfg->numChopCycles;
            if (tmpVal <= CY_CAPSENSE_16_BIT_MASK)
            {
                *ptrMaxRaw = (uint16_t)tmpVal;
            }
        }
    #else
        tmpVal *= ptrWdCfg->numChopCycles;
        if (tmpVal <= CY_CAPSENSE_16_BIT_MASK)
        {
            *ptrMaxRaw = (uint16_t)tmpVal;
        }
    #endif

    if (0u == *ptrMaxRaw)
    {
        *ptrMaxRaw = 1u;
    }
    return status;
}


/*******************************************************************************
* Function Name: Cy_CapSense_ConfigureSaturationMode
****************************************************************************//**
*
* Configures the MSCLP HW block for operation with the permanently saturated
* channel.
* The raw data counter is continuously enabled from the beginning to the end of
* the scan. The scan is performed in the CPU operating mode.
*
* \param context
* The pointer to the context structure allocated by the user or middleware.
*
*******************************************************************************/
void Cy_CapSense_ConfigureSaturationMode(
                cy_stc_capsense_context_t * context)
{
    uint32_t i;
    MSCLP_Type * ptrHwBase = context->ptrCommonConfig->ptrChConfig->ptrHwBase;

    Cy_CapSense_SetupCpuOperatingMode(context);

    /* Configure the Switch Control Global Function #0 to have all switches open.
     * All the sensing electrodes will be disconnected during the MAX raw count measurement.
     */
    ptrHwBase->SW_SEL_CSW_FUNC[0u] = 0x00u;

    /* Iterate through all the MODE structures and update them with the configuration,
     * required to saturate the measurement channel.
     */
    for (i = 0u; i < MSCLP_SENSE_MODE_NR; i++)
    {
        /* The 0x03 value of the RMF field enables the internal voltage divider and
         * configures it to generate VDDA*0.8 voltage at the output.
         */
        ptrHwBase->MODE[i].SW_SEL_TOP  = _VAL2FLD(MSCLP_MODE_SW_SEL_TOP_RMF, 0x03u);

        /* Set the CPF and the CMG bits to get the positive comparator input connected
         * to the VDDA*0.8 voltage level and the negative comparator input to the GND.
         */
        ptrHwBase->MODE[i].SW_SEL_COMP = _VAL2FLD(MSCLP_MODE_SW_SEL_COMP_CPF, 0x01u) |
                                         _VAL2FLD(MSCLP_MODE_SW_SEL_COMP_CMG, 0x01u);
    }

}

#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_AUTO_DITHER_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_ConfigureAutoDitherMode
****************************************************************************//**
*
* Configures the MSCLP HW block for operation in the auto-dithering mode.
*
* \param context
* The pointer to the context structure allocated by the user or middleware.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_CONFIG_OVERFLOW  - The numberSlots parameter exceeds
*                                         the maximum number of sensor configurations
*                                         which is possible to be loaded into the
*                                         internal buffer of the CAPSENSE&trade HW block.
* - CY_CAPSENSE_STATUS_BAD_CONFIG       - The function does not suppose to be
*                                         called with the current CAPSENSE&trade;
*                                         configuration.
* - CY_CAPSENSE_STATUS_HW_BUSY          - The MSCLP HW block is busy and cannot be
*                                         configured.
*
*******************************************************************************/
static cy_capsense_status_t Cy_CapSense_ConfigureAutoDitherMode(
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t status = CY_CAPSENSE_STATUS_SUCCESS;
    cy_en_msclp_status_t msclpStatus;
    const cy_stc_capsense_common_config_t * ptrCommonCfg = context->ptrCommonConfig;
    MSCLP_Type * ptrHwBase = ptrCommonCfg->ptrChConfig->ptrHwBase;

    /* Generate sensor frame configuration for active widgets*/
    Cy_CapSense_GenerateAllSensorConfig(CY_CAPSENSE_SNS_FRAME_ACTIVE, context);

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        /* Generate sensor frame configuration for LP widgets */
        Cy_CapSense_GenerateAllSensorConfig(CY_CAPSENSE_SNS_FRAME_LOW_POWER, context);
    #endif /* CY_CAPSENSE_LP_EN */

    /* Write configuration data into all MSCLP block registers */
    msclpStatus = Cy_MSCLP_Configure(ptrHwBase,
                            context->ptrBaseFrameContext,
                            CY_MSCLP_CAPSENSE_KEY,
                            ptrCommonCfg->ptrChConfig->ptrHwContext);

    Cy_CapSense_SetupCpuOperatingMode(context);

    if (CY_MSCLP_SUCCESS != msclpStatus)
    {
        status = CY_CAPSENSE_STATUS_HW_BUSY;
    }

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN)
        /* Set FILTER_MODE to CIC1 */
        ptrHwBase->FILTER_CTL &= ~MSCLP_FILTER_CTL_FILTER_MODE_Msk;
    #endif /* CY_CAPSENSE_CIC2_FILTER_EN */

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_EXT_FRM_START_EN)
        /* Clear the external start scan mode */
        ptrHwBase->CTL &= ~MSCLP_CTL_EXT_FRAME_START_MODE_Msk;
    #endif

    return status;
}
#endif

/*******************************************************************************
* Function Name: Cy_CapSense_GetScanWatchdogTime
****************************************************************************//**
*
* This internal function calculates the watchdog time in microseconds for the
* specified slot. The calculated value is the duration of one sample with the
* five-time margin.
*
* WATCHDOG_TIME = (SCAN_CYCLES / MOD_CLK_FREQ) * 5;
*
* where:
*
* SCAN_CYCLES = (INIT_CYCLES + PRO_CYCLES + CONV_CYCLES + EPI_CYCLES) * NUM_CONV;
* INIT_CYCLES = INIT_CMOD_RAIL_CYCLES + INIT_CMOD_SHORT_CYCLES;
* PRO_CYCLES = PRO_OFFSET_CYCLES + (PRO_WAIT_KREF_DELAY * SENSE_DIV / 4);
* CONV_CYCLES = (PRO_DUMMY_SUB_CONVS + NUM_SUB_CONVS) * SENSE_DIV;
* EPI_CYCLES = EPI_KREF_DELAY * SENSE_DIV / 4;
*
* The corresponding parameters are listed below:
* - EPI_KREF_DELAY - The duration of EPILOGUE defined in relation to Kref.
*   The value is interpreted as SENSE_DIV/4 increments.
* - INIT_CMOD_RAIL_CYCLES - Duration of the coarse initialization phase when
*   Cmod1 is connected to VDDA and Cmod2 is connected to VSSA. The parameter is
*   defined in terms of Mod Clock cycles.
* - INIT_CMOD_SHORT_CYCLES - Duration of the coarse short phase when
*   Cmod1 and Cmod2 are shorted together. The parameter is defined in terms of
*   Mod Clock cycles.
* - PRO_OFFSET_CYCLES - Maximum number of Mod Clock cycles to be assigned for
*   the PRO_OFFSET state. If NUM_PRO_OFFSET_TRIPS are observed before this
*   timeout, exit at that point.
* - PRO_DUMMY_SUB_CONVS - Number of sub-conversions (dummy cycles) to be run
*   during PRO_DUMMY.
* - PRO_WAIT_KREF_DELAY - The duration of PRO_WAIT defined in relation to Kref.
*   The value is interpreted as SENSE_DIV/4 increments.
* - SENSE_DIV - The length of one sub-conversion in terms of Mod Clock cycles.
* - NUM_SUB_CONVS - Number of sub-conversions.
* - NUM_CONV - Number of chop cycles.
* - MOD_CLK_FREQ - Modulation clock frequency.
*
* \param widgetId
* Specifies the ID number of the widget. A macro for the widget ID can be found
* in the cycfg_capsense.h file defined as CY_CAPSENSE_<WIDGET_NAME>_WDGT_ID.
*
* \param scanSlotId
* The slot ID the watchdog time calculation will be done for.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns watch-dog time interval in microseconds.
*
*******************************************************************************/
uint32_t Cy_CapSense_GetScanWatchdogTime(
                uint32_t widgetId,
                uint32_t scanSlotId,
                cy_stc_capsense_context_t * context)
{
    uint32_t tmpVal;
    uint32_t snsClkDivider;
    uint32_t modClkFreqMhz;
    const cy_stc_capsense_widget_config_t * ptrWdCfg;

    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_TOUCHPAD_EN) ||\
         (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_MATRIX_EN))
        const cy_stc_capsense_scan_slot_t * ptrScanSlots;
    #endif /* CY_CAPSENSE_CSD_TOUCHPAD_EN || CY_CAPSENSE_CSD_MATRIX_EN */

    /* Define the MARGIN_KOEFF = 5 */
    const uint32_t watchdogTimeMarginCoeff = 5u;

    (void)scanSlotId;

    /* Initialize the .modClkFreqMhz field with the MRSS IMO frequency value. */
    #if (CY_CAPSENSE_IMO_FREQUENCY == CY_CAPSENSE_IMO_25_MHZ)
        modClkFreqMhz  = CY_CAPSENSE_IMO_CLK_25_MHZ;
    #elif (CY_CAPSENSE_IMO_FREQUENCY == CY_CAPSENSE_IMO_38_MHZ)
        modClkFreqMhz  = CY_CAPSENSE_IMO_CLK_38_MHZ;
    #else /* (CY_CAPSENSE_IMO_FREQUENCY == CY_CAPSENSE_IMO_46_MHZ) */
        modClkFreqMhz  = CY_CAPSENSE_IMO_CLK_46_MHZ;
    #endif

    /* Initialize pointers with the configuration address for the specified scan slot and MSC channel #0 */
    ptrWdCfg = &context->ptrWdConfig[widgetId];

    /* Initialize the .snsClkDivider field with the value for the slot that is
    *  specified by the scanSlotId parameter of the function.
    */
    snsClkDivider = ptrWdCfg->ptrWdContext->snsClk;
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN)
        if (CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod)
        {
            #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_TOUCHPAD_EN) ||\
                 (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_MATRIX_EN))
                ptrScanSlots = &context->ptrScanSlots[scanSlotId];
                if (ptrWdCfg->numCols <= ptrScanSlots->snsId)
                {
                    snsClkDivider = ptrWdCfg->ptrWdContext->rowSnsClk;
                }
            #endif /* CY_CAPSENSE_CSD_TOUCHPAD_EN || CY_CAPSENSE_CSD_MATRIX_EN */
                    }
    #endif /* CY_CAPSENSE_CSD_EN */

    /* Calculate the INIT_CYCLES number. */
    tmpVal  = ((uint32_t)context->ptrInternalContext->numCoarseInitChargeCycles + context->ptrInternalContext->numCoarseInitSettleCycles);

    /* Add the PRO_OFFSET_CYCLES number. */
    tmpVal += (uint32_t)context->ptrInternalContext->numProOffsetCycles;

    /* Add the sum of PRO_CYCLES and EPI_CYCLES. Shift by 2 is required because for the fifth-generation low power devices
    *  the .numEpiCycles parameter are interpreted as SENSE_DIV/4 increments.
    */
    if (CY_CAPSENSE_CLK_SOURCE_PRS == (ptrWdCfg->ptrWdContext->snsClkSource & CY_CAPSENSE_CLK_SOURCE_MASK))
    {
        tmpVal += ((uint32_t)context->ptrInternalContext->numProWaitKrefDelayPrs + context->ptrInternalContext->numEpiKrefDelayPrs) * (snsClkDivider >> 2u);
    }
    else
    {
        tmpVal += ((uint32_t)context->ptrInternalContext->numProWaitKrefDelay + context->ptrInternalContext->numEpiKrefDelay) * (snsClkDivider >> 2u);
    }

    /* Add the CONV_CYCLES number. */
    tmpVal += ((uint32_t)context->ptrInternalContext->numFineInitCycles + ptrWdCfg->ptrWdContext->numSubConversions) * snsClkDivider;

    if (CY_CAPSENSE_CLK_SOURCE_PRS == (ptrWdCfg->ptrWdContext->snsClkSource & CY_CAPSENSE_CLK_SOURCE_MASK))
    {
        /* Taking into account correction that is implemented in the Cy_CapSense_AdjustSnsClkDivider() function,
         * the scan duration is two time longer if the PRS is used as the sense clock source.
         */
        tmpVal <<= 1u;
    }

    /* Calculate the SCAN_CYCLES number by multiplying the Mod Clock cycles number per one chop cycle by
    *  number of chop cycles.
    */
    tmpVal *= ptrWdCfg->numChopCycles;

    /* Convert the calculated duration in terms of clk_mod cycles to the microseconds. */
    tmpVal /= modClkFreqMhz;

    /* Multiply the calculated value by the MARGIN_KOEFF value. */
    tmpVal *= watchdogTimeMarginCoeff;

    return tmpVal;
}

#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_AUTO_DITHER_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_CdacDitherScaleCalc
****************************************************************************//**
*
* This internal function calculates the dither scale value based on highest
* raw count value in AUTO dithering mode.
*
* \note
* This function doesn't handle liquid level widgets.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return status
* Returns the status of the operation (different statuses can be combined):
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed
*                                         successfully.
* - CY_CAPSENSE_STATUS_BAD_PARAM        - At least one of input parameters is
*                                         not valid.
* - CY_CAPSENSE_STATUS_HW_BUSY          - The HW is busy with the previous scan.
*
*******************************************************************************/
static cy_capsense_status_t Cy_CapSense_CdacDitherScaleCalc(
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t status = CY_CAPSENSE_STATUS_SUCCESS;
    cy_en_msclp_status_t msclpStatus;
    const cy_stc_capsense_widget_config_t * ptrWdCfg;
    uint32_t wdIndex;
    uint32_t * ptrSnsFrame;
    uint32_t rawCountMax;

    const cy_stc_capsense_common_config_t * ptrCommonCfg = context->ptrCommonConfig;
    MSCLP_Type * ptrHwBase = ptrCommonCfg->ptrChConfig->ptrHwBase;

    /* Force HW configuration update on the next scan */
    status = Cy_CapSense_SwitchHwConfiguration(CY_CAPSENSE_HW_CONFIG_AUTO_DITHERING, context);

    ptrWdCfg = context->ptrWdConfig;
    for (wdIndex = 0u; wdIndex < CY_CAPSENSE_TOTAL_WIDGET_COUNT; wdIndex++)
    {
        if (0u != Cy_CapSense_IsWidgetEnabled(wdIndex, context))
        {
            if ((CY_CAPSENSE_CDAC_DITHERING_MODE_AUTO == ptrWdCfg->cdacDitherScaleMode) &&
                ((uint8_t)CY_CAPSENSE_WD_LIQUID_LEVEL_E != ptrWdCfg->wdType))
            {
                /* Handle only CSD and CSX widgets */
                if (CY_CAPSENSE_ISX_GROUP != ptrWdCfg->senseMethod)
                {
                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
                        /* Scan low power widgets */
                        if ((uint8_t)CY_CAPSENSE_WD_LOW_POWER_E == ptrWdCfg->wdType)
                        {
                            ptrSnsFrame = &context->ptrSensorFrameLpContext[ptrWdCfg->firstSlotId * CY_CAPSENSE_LP_SENSOR_FRAME_SIZE + 
                                                                                        CY_CAPSENSE_FRM_LP_SNS_SW_SEL_CSW_LO_MASK2_INDEX];
                            status |= Cy_CapSense_CdacDitherGetMaxRaw(ptrSnsFrame, ptrWdCfg, CY_CAPSENSE_LP_SENSOR_FRAME_SIZE, &rawCountMax, context);
                        }
                        else
                    #endif /* CY_CAPSENSE_LP_EN */
                    /* Scan active widgets */
                    {
                        ptrSnsFrame = &context->ptrSensorFrameContext[ptrWdCfg->firstSlotId * CY_CAPSENSE_SENSOR_FRAME_SIZE];
                        status |= Cy_CapSense_CdacDitherGetMaxRaw(ptrSnsFrame, ptrWdCfg, CY_CAPSENSE_SENSOR_FRAME_SIZE, &rawCountMax, context);
                    }

                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
                        /* Divide the result by 2 for the FW CSX scanning method */
                        if (CY_CAPSENSE_CSX_GROUP == ptrWdCfg->senseMethod)
                        {
                            rawCountMax /= CY_CAPSENSE_DIVIDER_TWO;
                        }
                    #endif

                    /* Set dither value according to measured widget raw counts */
                    if (rawCountMax < CY_CAPSENSE_DITHERING_SNS_CAP_300_FEMTO_RAW)
                    {
                        context->ptrWdContext[wdIndex].cdacDitherValue = 6u;
                    } else if (rawCountMax < CY_CAPSENSE_DITHERING_SNS_CAP_500_FEMTO_RAW)
                    {
                        context->ptrWdContext[wdIndex].cdacDitherValue = 5u;
                    } else if (rawCountMax < CY_CAPSENSE_DITHERING_SNS_CAP_1000_FEMTO_RAW)
                    {
                        context->ptrWdContext[wdIndex].cdacDitherValue = 4u;
                    } else if (rawCountMax < CY_CAPSENSE_DITHERING_SNS_CAP_3000_FEMTO_RAW)
                    {
                        context->ptrWdContext[wdIndex].cdacDitherValue = 3u;
                    } else if (rawCountMax < CY_CAPSENSE_DITHERING_SNS_CAP_5000_FEMTO_RAW)
                    {
                        context->ptrWdContext[wdIndex].cdacDitherValue = 2u;
                    } else if (rawCountMax < CY_CAPSENSE_DITHERING_SNS_CAP_10000_FEMTO_RAW)
                    {
                        context->ptrWdContext[wdIndex].cdacDitherValue = 1u;
                    } else
                    {
                        context->ptrWdContext[wdIndex].cdacDitherValue = 0u;
                    }
                }
            }
        }
        /* Increment pointer to the next widget */
        ptrWdCfg++;
    }

    /* Update Active frame configuration */
    Cy_CapSense_GenerateAllSensorConfig(CY_CAPSENSE_SNS_FRAME_ACTIVE, context);

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        /* Update LP frame configuration */
        Cy_CapSense_GenerateAllSensorConfig(CY_CAPSENSE_SNS_FRAME_LOW_POWER, context);
    #endif /* CY_CAPSENSE_LP_EN */

    /* Write configuration data into all MSCLP block registers */
    msclpStatus = Cy_MSCLP_Configure(ptrHwBase,
                                    context->ptrBaseFrameContext,
                                    CY_MSCLP_CAPSENSE_KEY,
                                    ptrCommonCfg->ptrChConfig->ptrHwContext);

    if (CY_MSCLP_SUCCESS != msclpStatus)
    {
        status = CY_CAPSENSE_STATUS_HW_BUSY;
    }

    return status;
}

/*******************************************************************************
* Function Name: Cy_CapSense_CdacDitherGetMaxRaw
****************************************************************************//**
*
* This internal function performs scanning for each sensor in a widget and finds
* the biggest raw count value.
*
* \param ptrSnsFrame
* The pointer to sensor frame array for current widget.
*
* \param ptrWdCfg
* The pointer to the widget config structure.
*
* \param snsFrameSize
* Sensor frame size:
* - CY_CAPSENSE_SENSOR_FRAME_SIZE - for active widgets
* - CY_CAPSENSE_LP_SENSOR_FRAME_SIZE - for low power widgets
*
* \param ptrRawCountMax
* The pointer to variable for storing raw counts maximum value.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return status
* Returns the status of the operation (different statuses can be combined):
* - CY_CAPSENSE_STATUS_SUCCESS       - The operation is performed
*                                      successfully.
* - CY_CAPSENSE_STATUS_TIMEOUT       - The software watchdog timeout occurred
*                                      during the scan, the scan was not completed.
*
*******************************************************************************/
static cy_capsense_status_t Cy_CapSense_CdacDitherGetMaxRaw(
                uint32_t * ptrSnsFrame,
                const cy_stc_capsense_widget_config_t * ptrWdCfg,
                uint32_t snsFrameSize,
                uint32_t * ptrRawCountMax,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t status = CY_CAPSENSE_STATUS_SUCCESS;
    uint32_t tmpRawCount;
    uint32_t watchdog;
    uint32_t scanConfigTmp[CY_MSCLP_6_SNS_REGS];
    uint32_t scanSlotId;
    uint32_t index;

    const cy_stc_capsense_common_config_t * ptrCommonCfg = context->ptrCommonConfig;
    MSCLP_Type * ptrHwBase = ptrCommonCfg->ptrChConfig->ptrHwBase;

    /* Reset maximum raw raw counts value before measurement */
    *ptrRawCountMax = 0u;

    /* Perform preliminary scans for active widgets */
    for (scanSlotId = 0u; scanSlotId < ptrWdCfg->numSns; scanSlotId++)
    {
        /* Inherit sensor frame to local array */
        for (index = 0u; index < CY_MSCLP_6_SNS_REGS; index++)
        {
            scanConfigTmp[index] = ptrSnsFrame[index];
        }
        /* Configure Sensor Clock, Clock Sources */
        scanConfigTmp[CY_CAPSENSE_SNS_CTL_INDEX] &= (uint32_t)~(MSCLP_SNS_SNS_CTL_START_SCAN_Msk | 
                                                    MSCLP_SNS_SNS_CTL_LAST_Msk | MSCLP_SNS_SNS_CTL_MULTI_CH_MODE_Msk | 
                                                    MSCLP_SNS_SNS_CTL_SENSE_DIV_Msk | MSCLP_SNS_SNS_CTL_LFSR_MODE_Msk);
        scanConfigTmp[CY_CAPSENSE_SNS_CTL_INDEX] |= (((CY_CAPSENSE_CDAC_DITHERING_KREF - 1u) << MSCLP_SNS_SNS_CTL_SENSE_DIV_Pos) |
                                                                (1u << MSCLP_SNS_SNS_CTL_LAST_Pos));

        /* Configure Number of sub-conversions, Compensation divider */
        scanConfigTmp[CY_CAPSENSE_SNS_SCAN_CTL_INDEX] = (((CY_CAPSENSE_CDAC_DITHERING_NUM_SUBCONV - 1u) << MSCLP_SNS_SNS_SCAN_CTL_NUM_SUB_CONVS_Pos) |
                                                        ((CY_CAPSENSE_CDAC_DITHERING_COMP_DIV - 1u) << MSCLP_SNS_SNS_SCAN_CTL_COMP_DIV_Pos));

        /* Configure Cap DACs and Clock reference rate*/
        scanConfigTmp[CY_CAPSENSE_SNS_CDAC_CTL_INDEX] = 0u;
        scanConfigTmp[CY_CAPSENSE_SNS_CDAC_CTL_INDEX] |= ((CY_CAPSENSE_CDAC_DITHERING_CDAC_REF << MSCLP_SNS_SNS_CDAC_CTL_SEL_RE_Pos) |
                                                        (CY_CAPSENSE_CDAC_DITHERING_CLOCK_REF_RATE << MSCLP_SNS_SNS_CDAC_CTL_CLOCK_REF_RATE_Pos));

        Cy_CapSense_StartCpuScan((const uint32_t *)scanConfigTmp, context);

        watchdog = Cy_CapSense_WaitEndOfCpuScan(CY_CAPSENSE_CDAC_DITHERING_WATCHDOG_TIME, context);

        /* Check if the watchdog timeout happened */
        if (0u == watchdog)
        {
            status = CY_CAPSENSE_STATUS_TIMEOUT;
        }
        else
        {
            /* Read raw counts */
            tmpRawCount = ptrHwBase->SNS.RESULT_FIFO_RD & MSCLP_SNS_RESULT_FIFO_RD_RAW_COUNT_Msk;
            if (*ptrRawCountMax < tmpRawCount)
            {
                /* Keep maximum raw counts */
                *ptrRawCountMax = tmpRawCount;
            }
        }
        /* Increment pointer to the next sensor */
        ptrSnsFrame += snsFrameSize;
    }

    return status;
}
#endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CDAC_AUTO_DITHER_EN) */


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LIQUID_LEVEL_FOAM_REJECTION_EN)
/*******************************************************************************
* Function Name: Cy_CapSense_ShortIntegration
****************************************************************************//**
*
* Initiates the check of specified slots. Widgets with short integration time
* like foam rejection feature can't be scanned with the others in one scan.
*
* \note
* This function is available only for the fifth-generation low power CAPSENSE&trade;.
*
* \param startSlotId
* The slot ID scan will be started from.
*
* \param numberSlots
* The number of slots will be scanned.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS          - The operation is performed successfully.
* - CY_CAPSENSE_STATUS_MIXED_SENSORS    - Sensors with short integration time
* and w/o can't be scanned in one frame.
*
*******************************************************************************/
static cy_capsense_status_t Cy_CapSense_ShortIntegration(
                uint32_t startSlotId,
                uint32_t numberSlots,
                cy_stc_capsense_context_t * context)
{
    uint32_t curSlotIndex;
    uint32_t wdIndex;
    uint32_t snsIndex;
    const cy_stc_capsense_scan_slot_t * ptrScanSlots;
    const cy_stc_capsense_widget_config_t * ptrWdCfg;
    uint32_t regularWdCnt = 0u;
    uint32_t irregularWdCnt = 0u;
    uint32_t lastSlot = startSlotId + numberSlots - 1u;
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_SUCCESS;

    ptrScanSlots = context->ptrScanSlots;
    curSlotIndex = startSlotId;

    do
    {
        wdIndex  = ptrScanSlots[curSlotIndex].wdId;
        snsIndex = ptrScanSlots[curSlotIndex].snsId;
        ptrWdCfg = &context->ptrWdConfig[wdIndex];

        if (((uint8_t)CY_CAPSENSE_WD_LIQUID_LEVEL_E == ptrWdCfg->wdType) &&
                (0u != (ptrWdCfg->centroidConfig & CY_CAPSENSE_LLW_FOAM_EN_MASK)))
        {
            irregularWdCnt++;
        }
        else
        {
            regularWdCnt++;
        }

        if ((0u != regularWdCnt) && (0u != irregularWdCnt))
        {
            capStatus = CY_CAPSENSE_STATUS_MIXED_SENSORS;
            break;
        }

        /* Jump to the next widget */
        curSlotIndex += (ptrWdCfg->numSlots - snsIndex);
    } while (curSlotIndex <= lastSlot);

    if ((CY_CAPSENSE_STATUS_SUCCESS == capStatus) && (0u < irregularWdCnt))
    {
        /* Configures Foam rejection scan */
        context->ptrCommonConfig->ptrChConfig->ptrHwBase->SENSE_DUTY_CTL = 
                ((CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_WIDTH_SEL_FOAM << MSCLP_SENSE_DUTY_CTL_PHASE_WIDTH_SEL_Pos) | 
                 (CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_CYCLES_FOAM << MSCLP_SENSE_DUTY_CTL_PHASE_SHIFT_CYCLES_Pos) | 
                 ((uint32_t)ptrWdCfg->ptrWdContext->sigPFC << MSCLP_SENSE_DUTY_CTL_PHASE_WIDTH_Pos));
    }

    return capStatus;
}
#endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LIQUID_LEVEL_FOAM_REJECTION_EN) */


#endif /* CY_IP_M0S8MSCV3LP */


/* [] END OF FILE */
