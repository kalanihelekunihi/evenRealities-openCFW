/***************************************************************************//**
* \file cy_capsense_generator_lp.c
* \version 6.10.0
*
* \brief
* This file contains the source of functions common for register map
* generator module.
*
********************************************************************************
* \copyright
* Copyright 2020-2025, Cypress Semiconductor Corporation (an Infineon company)
* or an affiliate of Cypress Semiconductor Corporation. All rights reserved.
* You may use this file only in accordance with the license, terms, conditions,
* disclaimers, and limitations in the end user license agreement accompanying
* the software package with which this file was provided.
*******************************************************************************/


#include <string.h>
#include "cycfg_capsense_defines.h"
#include "cycfg_peripherals.h"
#include "cy_capsense_common.h"
#include "cy_capsense_structure.h"
#include "cy_capsense_sensing_lp.h"
#include "cy_capsense_generator_lp.h"
#if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
    #include "cy_msclp.h"
#endif

#if (defined(CY_IP_M0S8MSCV3LP))


/*******************************************************************************
* Internal function prototypes
*******************************************************************************/
void Cy_CapSense_GenerateModeConfig(
                const cy_stc_capsense_context_t * context);

#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_ENABLED)
    static void Cy_CapSense_GenerateMultiphaseSensorConfig(
                uint32_t snsFrameType,
                uint32_t scanSlotIndex,
                uint32_t * ptrSensorCfgLoc,
                cy_stc_capsense_context_t * context);
#endif


/*******************************************************************************
* Function Name: Cy_CapSense_GenerateBaseConfig
****************************************************************************//**
*
* Generates the configuration for all registers that have to be configured
* one-time to initialize the MSCLP block.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS       - The operation is performed successfully.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_GenerateBaseConfig(cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t capStatus;

    cy_stc_capsense_internal_context_t * ptrIntrCxt = context->ptrInternalContext;
    const cy_stc_msclp_base_config_t cy_capsense_smTemplate = CY_CAPSENSE_SENSING_METHOD_BASE_TEMPLATE;
    cy_stc_msclp_base_config_t * ptrBaseCfg = context->ptrBaseFrameContext;
    const cy_stc_msclp_base_config_t * ptrTemplateCfg = &cy_capsense_smTemplate;

    /*
     * BASE CONFIGURATION
     */

    /* Copy template of a base config */
    ptrBaseCfg->ctl = ptrTemplateCfg->ctl;
    ptrBaseCfg->scanCtl1 = ptrTemplateCfg->scanCtl1;
    ptrBaseCfg->scanCtl2 = ptrTemplateCfg->scanCtl2;
    ptrBaseCfg->initCtl1 = ptrTemplateCfg->initCtl1;
    ptrBaseCfg->initCtl2 = ptrTemplateCfg->initCtl2;
    ptrBaseCfg->initCtl3 = ptrTemplateCfg->initCtl3;
    ptrBaseCfg->initCtl4 = ptrTemplateCfg->initCtl4;
    ptrBaseCfg->senseDutyCtl = ptrTemplateCfg->senseDutyCtl;
    ptrBaseCfg->ccompCdacCtl = ptrTemplateCfg->ccompCdacCtl;
    ptrBaseCfg->mscCmpCtl = ptrTemplateCfg->mscCmpCtl;

    ptrBaseCfg->aosCtl = ptrTemplateCfg->aosCtl;
    ptrBaseCfg->ceCtl = ptrTemplateCfg->ceCtl;
    ptrBaseCfg->pumpCtl = ptrTemplateCfg->pumpCtl;

    ptrBaseCfg->intr = ptrTemplateCfg->intr;
    ptrBaseCfg->intrSet = ptrTemplateCfg->intrSet;
    ptrBaseCfg->intrMask = ptrTemplateCfg->intrMask;
    ptrBaseCfg->intrLp = ptrTemplateCfg->intrLp;
    ptrBaseCfg->intrLpSet = ptrTemplateCfg->intrLpSet;
    ptrBaseCfg->intrLpMask = ptrTemplateCfg->intrLpMask;
    ptrBaseCfg->swSelCdacRe = ptrTemplateCfg->swSelCdacRe;
    ptrBaseCfg->swSelCdacCo = ptrTemplateCfg->swSelCdacCo;
    ptrBaseCfg->swSelCdacCf = ptrTemplateCfg->swSelCdacCf;
    ptrBaseCfg->swSelBgr = ptrTemplateCfg->swSelBgr;

    /*
     * CONFIGURATION FROM CAPSENSE&trade; DATA STRUCTURE
     */

    ptrBaseCfg->ctl &= ~MSCLP_CTL_EXT_FRAME_START_MODE_Msk;

    /* Set the current scanning mode */
    CY_REG32_CLR_SET(ptrBaseCfg->ctl, MSCLP_CTL_OPERATING_MODE, ptrIntrCxt->operatingMode);
    /* Generating the common configuration for the number of the auto-resampling cycles and the counter behaviour when the
     * RAW_COUNT exceeds 0xFFFF
     */
    CY_REG32_CLR_SET(ptrBaseCfg->scanCtl1, MSCLP_SCAN_CTL1_NUM_AUTO_RESAMPLE, context->ptrCommonConfig->numBadScans);
    CY_REG32_CLR_SET(ptrBaseCfg->scanCtl1, MSCLP_SCAN_CTL1_RAW_COUNT_MODE,    context->ptrCommonConfig->counterMode);

    /* Generating the common configuration for the number of epilogue cycles */
    CY_REG32_CLR_SET(ptrBaseCfg->scanCtl2, MSCLP_SCAN_CTL2_NUM_EPI_KREF_DELAY, ((0u < ptrIntrCxt->numEpiKrefDelay) ? ptrIntrCxt->numEpiKrefDelay : 1uL));
    CY_REG32_CLR_SET(ptrBaseCfg->scanCtl2, MSCLP_SCAN_CTL2_NUM_EPI_KREF_DELAY_PRS, ((0u < ptrIntrCxt->numEpiKrefDelayPrs) ? ptrIntrCxt->numEpiKrefDelayPrs : 1uL));
    /* Generating the common configuration for the system level chopping */
    CY_REG32_CLR_SET(ptrBaseCfg->scanCtl2, MSCLP_SCAN_CTL2_CHOP_POL, context->ptrCommonConfig->chopPolarity);

    /* Generating the common configuration for the coarse initialization and coarse short phase */
    CY_REG32_CLR_SET(ptrBaseCfg->initCtl1, MSCLP_INIT_CTL1_NUM_INIT_CMOD_12_RAIL_CYCLES,  ptrIntrCxt->numCoarseInitChargeCycles);
    CY_REG32_CLR_SET(ptrBaseCfg->initCtl1, MSCLP_INIT_CTL1_NUM_INIT_CMOD_12_SHORT_CYCLES, ptrIntrCxt->numCoarseInitSettleCycles);

    CY_REG32_CLR_SET(ptrBaseCfg->initCtl3, MSCLP_INIT_CTL3_CMOD_SEL, CY_CAPSENSE_CMOD12_PAIR_SELECTION);
    CY_REG32_CLR_SET(ptrBaseCfg->initCtl3, MSCLP_INIT_CTL3_NUM_PRO_OFFSET_CYCLES, ptrIntrCxt->numProOffsetCycles);

    /* Generating the common configuration for the number of sub-conversions to be run during PRO_DUMMY and PRO_WAIT phases. */
    CY_REG32_CLR_SET(ptrBaseCfg->initCtl4, MSCLP_INIT_CTL4_NUM_PRO_DUMMY_SUB_CONVS, context->ptrInternalContext->numFineInitCycles);
    CY_REG32_CLR_SET(ptrBaseCfg->initCtl4, MSCLP_INIT_CTL4_NUM_PRO_WAIT_KREF_DELAY, context->ptrInternalContext->numProWaitKrefDelay);
    CY_REG32_CLR_SET(ptrBaseCfg->initCtl4, MSCLP_INIT_CTL4_NUM_PRO_WAIT_KREF_DELAY_PRS,  context->ptrInternalContext->numProWaitKrefDelayPrs);

    /* Generating the common configuration for the clock dithering */
    ptrBaseCfg->sensePeriodCtl = _VAL2FLD(MSCLP_SENSE_PERIOD_CTL_LFSR_POLY,  context->ptrInternalContext->lfsrPoly) |
                                 _VAL2FLD(MSCLP_SENSE_PERIOD_CTL_LFSR_SCALE, context->ptrInternalContext->lfsrScale);

    /* Generating the common configuration for the CIC2 Filter */
    ptrBaseCfg->filterCtl = _VAL2FLD(MSCLP_FILTER_CTL_FILTER_MODE, CY_CAPSENSE_CIC2_FILTER_EN);

    /* Generating the common configuration for the dithering CapDAC */
    ptrBaseCfg->ditherCdacCtl = _VAL2FLD(MSCLP_DITHER_CDAC_CTL_SEL_FL,       context->ptrInternalContext->cdacDitherSeed) |
                                _VAL2FLD(MSCLP_DITHER_CDAC_CTL_LFSR_POLY_FL, context->ptrInternalContext->cdacDitherPoly);

    /* Generating the common configuration for the Compensation CDAC */
    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_COMP_USAGE) || \
        (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CDAC_COMP_USAGE) || \
        (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CDAC_COMP_USAGE))
        CY_REG32_CLR_SET(ptrBaseCfg->ccompCdacCtl, MSCLP_CCOMP_CDAC_CTL_SEL_CO_PRO_OFFSET, ptrIntrCxt->proOffsetCdacComp);
    #else
        ptrBaseCfg->swSelCdacCo = 0u;
    #endif

    #if (CY_CAPSENSE_IMO_FREQUENCY == CY_CAPSENSE_IMO_25_MHZ)
        ptrBaseCfg->imoCtl = _VAL2FLD(MSCLP_IMO_CTL_FREQ, CY_MSCLP_IMO_25_MHZ);
    #elif (CY_CAPSENSE_IMO_FREQUENCY == CY_CAPSENSE_IMO_38_MHZ)
        ptrBaseCfg->imoCtl = _VAL2FLD(MSCLP_IMO_CTL_FREQ, CY_MSCLP_IMO_38_MHZ);
    #else /* (CY_CAPSENSE_IMO_FREQUENCY == CY_CAPSENSE_IMO_46_MHZ) */
        ptrBaseCfg->imoCtl = _VAL2FLD(MSCLP_IMO_CTL_FREQ, CY_MSCLP_IMO_46_MHZ);
    #endif
    ptrBaseCfg->imoCtl |= _VAL2FLD(MSCLP_IMO_CTL_CLOCK_MSC_DIV, (uint32_t)context->ptrInternalContext->modClk - 1u);

    Cy_CapSense_GenerateModeConfig(context);

    /* PINS FUNCTIONS CONFIGURATION */
    capStatus = Cy_CapSense_GeneratePinFunctionConfig(context);

    return capStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_GeneratePinFunctionConfig
****************************************************************************//**
*
* Configures pin function-related registers in base configuration per defined
* CapSense configuration.
*
* \param context
* The pointer to the CAPSENSE&trade; context
* structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_GeneratePinFunctionConfig(
                const cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_SUCCESS;

    uint32_t i;
    uint8_t idCounter = 0u;

    uint8_t * ptrMapping = &context->ptrInternalContext->mapPinState[0u];
    uint32_t * ptrCswFunc = &context->ptrBaseFrameContext->swSelCswFunc[0u];
    const uint32_t pinStates[CY_CAPSENSE_CTRLMUX_PIN_STATE_NUMBER] = CY_CAPSENSE_PIN_STATES_ARR;

    for (i = 0u; i < CY_CAPSENSE_CTRLMUX_PIN_STATE_NUMBER; i++)
    {
        ptrMapping[i] = CY_CAPSENSE_PIN_STATE_IDX_UNDEFINED;
    }

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
        ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_CSX_RX] = idCounter;
        idCounter++;
        ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_CSX_TX] = idCounter;
        idCounter++;

        /* Set CSX inactive sensor connection */
        switch (context->ptrInternalContext->intrCsxInactSnsConn)
        {
            case CY_CAPSENSE_SNS_CONNECTION_HIGHZ:
                ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_HIGH_Z] = idCounter;
                idCounter++;
                break;
            case CY_CAPSENSE_SNS_CONNECTION_VDDA_BY_2:
                ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_CSX_VDDA2] = idCounter;
                idCounter++;
                break;
            default:
                ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_GND] = idCounter;
                idCounter++;
                break;
        }

        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_TX_ENABLED)
            ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_CSX_NEG_TX] = idCounter;
            idCounter++;
        #endif /* CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_TX_ENABLED */
    #endif /* CY_CAPSENSE_CSX_EN */

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN)
        ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_CSD_SNS] = idCounter;
        idCounter++;

        /* Set CSD inactive sensor connection if it is not assigned already */
        switch (context->ptrInternalContext->intrCsdInactSnsConn)
        {
            case CY_CAPSENSE_SNS_CONNECTION_HIGHZ:
                if (CY_CAPSENSE_PIN_STATE_IDX_UNDEFINED == ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_HIGH_Z])
                {
                    ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_HIGH_Z] = idCounter;
                    idCounter++;
                }
                break;
            case CY_CAPSENSE_SNS_CONNECTION_GROUND:
                if (CY_CAPSENSE_PIN_STATE_IDX_UNDEFINED == ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_GND])
                {
                    ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_GND] = idCounter;
                    idCounter++;
                }
                break;
            default:
                /* No action */
                break;
        }

        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_SHIELD_EN)
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SHIELD_PASSIVE_EN)
                if (CY_CAPSENSE_PIN_STATE_IDX_UNDEFINED ==
                        ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_PAS_SHIELD])
                {
                    ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_PAS_SHIELD] = idCounter;
                    idCounter++;
                }
            #else
                if (CY_CAPSENSE_PIN_STATE_IDX_UNDEFINED ==
                        ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_ACT_SHIELD])
                {
                    ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_ACT_SHIELD] = idCounter;
                    idCounter++;
                }
            #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SHIELD_PASSIVE_EN) */
        #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_SHIELD_EN) */

        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
            ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_MPSC_CSP] = idCounter;
            idCounter++;
            ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_MPSC_CSN] = idCounter;
            idCounter++;

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MPSC_ZERO_PIN_EN)
                    ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_MPSC_CSZ] = idCounter;
                    idCounter++;
            #endif
        #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED) */
    #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN) */

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN)
        ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_ISX_RX] = idCounter;
        idCounter++;
        ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_ISX_LX] = idCounter;
        idCounter++;

        /* Set ISX inactive sensor connection if it is not assigned already */
        switch (context->ptrInternalContext->intrIsxInactSnsConn)
        {
            case CY_CAPSENSE_SNS_CONNECTION_HIGHZ:
                if (CY_CAPSENSE_PIN_STATE_IDX_UNDEFINED == ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_HIGH_Z])
                {
                    ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_HIGH_Z] = idCounter;
                    idCounter++;
                }
                break;
            case CY_CAPSENSE_SNS_CONNECTION_GROUND:
                if (CY_CAPSENSE_PIN_STATE_IDX_UNDEFINED == ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_GND])
                {
                    ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_GND] = idCounter;
                    idCounter++;
                }
                break;
            default:
                /* No action */
                break;
        }

        #if (((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_SHIELD_EN) && \
              (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN)) || \
              (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN))

            if ((CY_CAPSENSE_SNS_CONNECTION_SHIELD == context->ptrInternalContext->intrCsdInactSnsConn) || 
                (CY_CAPSENSE_SNS_CONNECTION_VDDA_BY_2 == context->ptrInternalContext->intrCsxInactSnsConn))
            {
                if (CY_CAPSENSE_PIN_STATE_IDX_UNDEFINED == ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_GND])
                {
                    ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_GND] = idCounter;
                    idCounter++;
                }
            }
        #endif

    #endif /* CY_CAPSENSE_ISX_EN */

    context->ptrInternalContext->numFunc = idCounter;

    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN) && \
         (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) && \
         (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN) && \
         ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_SHIELD_EN) || \
         (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_TX_ENABLED)))
        if (MSCLP_CSW_GLOBAL_FUNC_NR < idCounter)
        {
            capStatus = CY_CAPSENSE_STATUS_CONFIG_OVERFLOW;
        }
        else
        {
            for (i = 0u; i < CY_CAPSENSE_CTRLMUX_PIN_STATE_NUMBER; i++)
            {
                if (CY_CAPSENSE_PIN_STATE_IDX_UNDEFINED != ptrMapping[i])
                {
                    ptrCswFunc[ptrMapping[i]] = pinStates[i];
                }
            }
        }
    #else
        for (i = 0u; i < CY_CAPSENSE_CTRLMUX_PIN_STATE_NUMBER; i++)
        {
            if (CY_CAPSENSE_PIN_STATE_IDX_UNDEFINED != ptrMapping[i])
            {
                ptrCswFunc[ptrMapping[i]] = pinStates[i];
            }
        }
    #endif

    return capStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_GenerateSensorConfig
****************************************************************************//**
*
* Generates configuration to configure registers to
* the scan of the single sensor in the specified slot of the specified Sensor Frame.
*
* \param snsFrameType
* The Sensor Frame type:
* * CY_CAPSENSE_SNS_FRAME_ACTIVE     - Sensor frame for Active slot
* * CY_CAPSENSE_SNS_FRAME_LOW_POWER  - Sensor frame for Low Power slot
*
* \param scanSlot
* The specified slot index.
*
* \param ptrSensorCfg
* Specifies the pointer to the sensor configuration to be filled.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS       - The operation is performed successfully.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_GenerateSensorConfig(
                uint32_t snsFrameType,
                uint32_t scanSlot,
                uint32_t * ptrSensorCfg,
                cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_BAD_PARAM;
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        const cy_stc_capsense_internal_context_t * ptrInternalCxt = context->ptrInternalContext;
        const cy_stc_capsense_scan_slot_t * ptrScanSlot = (CY_CAPSENSE_SNS_FRAME_ACTIVE == snsFrameType) ? &context->ptrScanSlots[scanSlot] :
                                                                                                           &context->ptrLpScanSlots[scanSlot];
    #else
        const cy_stc_capsense_scan_slot_t * ptrScanSlot = &context->ptrScanSlots[scanSlot];
        (void)snsFrameType;
    #endif /* CY_CAPSENSE_LP_EN */
    cy_stc_capsense_widget_config_t const * ptrWdCfg = &context->ptrWdConfig[ptrScanSlot->wdId];
    cy_stc_capsense_widget_context_t const * ptrWdCxt = &context->ptrWdContext[ptrScanSlot->wdId];
    uint32_t snsMethod = ptrWdCfg->senseMethod;
    uint32_t modeSel = 0u;
    uint32_t tempValue;
    uint32_t *ptrSensorCfgLocal = ptrSensorCfg;

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        if (CY_CAPSENSE_SNS_FRAME_LOW_POWER == snsFrameType) /* If Low Power Sensor Frame */
        {
            ptrSensorCfgLocal[CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL0] = _VAL2FLD(MSCLP_SNS_SNS_LP_AOS_SNS_CTL0_RC_COEFF, ptrInternalCxt->iirCoeffLp) |
                                                                _VAL2FLD(MSCLP_SNS_SNS_LP_AOS_SNS_CTL0_BL_COEFF_SLOW, ptrInternalCxt->bslnCoefSlow) |
                                                                _VAL2FLD(MSCLP_SNS_SNS_LP_AOS_SNS_CTL0_BL_COEFF_FAST, ptrInternalCxt->bslnCoefFast) |
                                                                _VAL2FLD(MSCLP_SNS_SNS_LP_AOS_SNS_CTL0_LOW_BL_RESET, ptrWdCxt->lowBslnRst) |
                                                                _VAL2FLD(MSCLP_SNS_SNS_LP_AOS_SNS_CTL0_BL_UPDATE_DELAY, ptrInternalCxt->bslnUpdateDelay);
            ptrSensorCfgLocal[CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL1] = _VAL2FLD(MSCLP_SNS_SNS_LP_AOS_SNS_CTL1_NOISE_THR, ptrWdCxt->noiseTh) |
                                                                _VAL2FLD(MSCLP_SNS_SNS_LP_AOS_SNS_CTL1_NOISE_THR_NEG, ptrWdCxt->nNoiseTh);
            ptrSensorCfgLocal[CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL2] = _VAL2FLD(MSCLP_SNS_SNS_LP_AOS_SNS_CTL2_SIGNAL_THR, ptrWdCxt->fingerTh) |
                                                                _VAL2FLD(MSCLP_SNS_SNS_LP_AOS_SNS_CTL2_DEBOUNCE_THRESHOLD, ptrWdCxt->onDebounce) |
                                                                _BOOL2FLD(MSCLP_SNS_SNS_LP_AOS_SNS_CTL2_SIGNAL_TYPE, (CY_CAPSENSE_CSD_GROUP != snsMethod));
            ptrSensorCfgLocal[CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL3] = 0u;
            ptrSensorCfgLocal[CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL4] = 0u;

            ptrSensorCfgLocal += (CY_MSCLP_11_SNS_REGS - CY_MSCLP_6_SNS_REGS);
        }
    #endif

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_RC_HW_IIR_FILTER_EN)
        if (CY_CAPSENSE_SNS_FRAME_LOW_POWER != snsFrameType)
        {
            /* Set raw count filter coefficient */
            ptrSensorCfgLocal[CY_CAPSENSE_SNS_HW_IIR_INDEX] = (uint32_t)((uint32_t)ptrWdCfg->iirCoeffHw << CY_CAPSENSE_RC_HW_IIR_FILTER_COEFF_POS);
        }
    #endif

    ptrSensorCfgLocal[CY_CAPSENSE_SNS_SCAN_CTL_INDEX] = _VAL2FLD(MSCLP_SNS_SNS_SCAN_CTL_NUM_CONV, (uint32_t)ptrWdCfg->numChopCycles - 1uL) | /* System level chopping */
                                                        _VAL2FLD(MSCLP_SNS_SNS_SCAN_CTL_NUM_SUB_CONVS, (uint32_t)ptrWdCxt->numSubConversions - 1uL); /* Number of sub-conversions */
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CIC2_FILTER_EN)
        tempValue = ptrWdCxt->cicShift;
        #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_TOUCHPAD_EN) ||\
             (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_MATRIX_EN))
            if ((((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == ptrWdCfg->wdType) ||
                 ((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == ptrWdCfg->wdType)) &&
                  (ptrWdCfg->numCols <= ptrScanSlot->snsId) &&
                  (CY_CAPSENSE_CSD_GROUP == ptrWdCfg->senseMethod))
            {
                tempValue = ptrWdCxt->rowCicShift;
            }
        #endif
        ptrSensorCfgLocal[CY_CAPSENSE_SNS_SCAN_CTL_INDEX] |= (uint32_t)(tempValue & (uint32_t)~(uint32_t)CY_CAPSENSE_CIC_AUTO_MASK) << CY_CAPSENSE_CIC_FIELD_POSITION;
    #endif

    if ((CY_CAPSENSE_ENABLE == ptrWdCxt->coarseInitBypassEn) &&
      (scanSlot != ptrWdCfg->firstSlotId))
    {
        ptrSensorCfgLocal[CY_CAPSENSE_SNS_SCAN_CTL_INDEX] |= MSCLP_SNS_SNS_SCAN_CTL_INIT_BYPASS_Msk;
    }

    /* CapDAC configuration, after the SNS_SCAN_CTL initialization */
    capStatus = Cy_CapSense_GenerateCdacConfig(ptrScanSlot, ptrSensorCfgLocal, context);

    if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
    {
        tempValue = ptrWdCxt->snsClk;
        switch (snsMethod)
        {
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN)
                case CY_CAPSENSE_CSD_GROUP:
                    modeSel = CY_CAPSENSE_REG_MODE_CSD;
                    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_TOUCHPAD_EN) ||\
                         (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_MATRIX_EN))
                        if ((((uint8_t)CY_CAPSENSE_WD_MATRIX_BUTTON_E == ptrWdCfg->wdType) ||
                             ((uint8_t)CY_CAPSENSE_WD_TOUCHPAD_E == ptrWdCfg->wdType)) &&
                              (ptrWdCfg->numCols <= ptrScanSlot->snsId))
                        {
                            tempValue = ptrWdCxt->rowSnsClk;
                        }
                    #endif /* CY_CAPSENSE_CSD_TOUCHPAD_EN || CY_CAPSENSE_CSD_MATRIX_EN */
                    break;
            #endif /* CY_CAPSENSE_CSD_EN */

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
                case CY_CAPSENSE_CSX_GROUP:
                    modeSel = CY_CAPSENSE_REG_MODE_CSX;
                    break;
            #endif /* CY_CAPSENSE_CSX_EN */

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN)
                case CY_CAPSENSE_ISX_GROUP:
                    modeSel = CY_CAPSENSE_REG_MODE_ISX;
                    break;
            #endif /* CY_CAPSENSE_ISX_EN */

            default:
                capStatus = CY_CAPSENSE_STATUS_BAD_PARAM;
                break;
        }

        if (CY_CAPSENSE_STATUS_SUCCESS == capStatus)
        {
            tempValue = Cy_CapSense_AdjustSnsClkDivider((uint8_t)snsMethod, ptrWdCxt->snsClkSource, (uint16_t)tempValue) - 1u;

            ptrSensorCfgLocal[CY_CAPSENSE_SNS_CTL_INDEX] = _VAL2FLD(MSCLP_SNS_SNS_CTL_SENSE_MODE_SEL, modeSel) |
                                                        #if (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CIC2_FILTER_EN)
                                                           _VAL2FLD(MSCLP_SNS_SNS_CTL_DECIM_RATE, (uint32_t)ptrWdCxt->cicRate - 1u) |
                                                        #endif /* (CY_CAPSENSE_DISABLE != CY_CAPSENSE_CIC2_FILTER_EN) */
                                                                    MSCLP_SNS_SNS_CTL_VALID_Msk |
                                                                    MSCLP_SNS_SNS_CTL_START_SCAN_Msk |
                                                            _VAL2FLD(MSCLP_SNS_SNS_CTL_SENSE_DIV, tempValue) |
                                                            _VAL2FLD(MSCLP_SNS_SNS_CTL_LFSR_MODE, ptrWdCxt->snsClkSource) |
                                                            _VAL2FLD(MSCLP_SNS_SNS_CTL_LFSR_BITS, ptrWdCxt->lfsrBits);
        }
    }

    return capStatus;
}


#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_ENABLED)
/*******************************************************************************
* Function Name: Cy_CapSense_GenerateMultiphaseSensorConfig
********************************************************************************
*
* Generates configuration for the multi-phase sensor groups.
*
* \param snsFrameType
* The Sensor Frame type:
* * CY_CAPSENSE_SNS_FRAME_ACTIVE     - Sensor frame for Active slot
* * CY_CAPSENSE_SNS_FRAME_LOW_POWER  - Sensor frame for Low Power slot
*
* \param scanSlotIndex
* Sensor frame slot number.
*
* \param ptrSensorCfgLoc
* Specifies the pointer to the mask registers.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
static void Cy_CapSense_GenerateMultiphaseSensorConfig(
                uint32_t snsFrameType,
                uint32_t scanSlotIndex,
                uint32_t * ptrSensorCfgLoc,
                cy_stc_capsense_context_t * context)
{
    uint8_t * ptrMapping = &context->ptrInternalContext->mapPinState[0u];
    const cy_stc_capsense_widget_config_t * ptrWdCfg;
    const cy_stc_capsense_scan_slot_t * ptrScanSlots;

    uint32_t snsFuncState;
    cy_stc_capsense_electrode_config_t const * eltdPinCfg;

    uint32_t wdIndex;
    uint32_t snsMethod;
    uint32_t snsIndex;

    uint32_t i = 0u;
    uint32_t j = 0u;
    uint32_t pattern = 0u;
    uint32_t order;

    uint32_t snsMask = 0u;
    uint32_t snsMaskNegative;
    uint32_t snsFuncStateNegative;

    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED) && (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MPSC_ZERO_PIN_EN))
        uint32_t zeroPattern = 0u;
        uint32_t snsMaskZero = 0u;
        uint32_t snsFuncStateZero;
    #endif

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        ptrScanSlots = (snsFrameType == CY_CAPSENSE_SNS_FRAME_ACTIVE) ? (context->ptrScanSlots) : (context->ptrLpScanSlots);
    #else
        ptrScanSlots = context->ptrScanSlots;
        (void)snsFrameType;
    #endif

    snsIndex = ptrScanSlots[scanSlotIndex].snsId;
    wdIndex = ptrScanSlots[scanSlotIndex].wdId;
    ptrWdCfg = &context->ptrWdConfig[wdIndex];
    snsMethod = ptrWdCfg->senseMethod;

    /* Prepare masks and pin states */
    snsMask = 0u;
    snsMaskNegative = 0u;

    snsFuncState = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_CSX_TX];
    snsFuncStateNegative = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_CSX_NEG_TX];

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
        if (CY_CAPSENSE_CSD_GROUP == snsMethod)
        {
            snsFuncState = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_MPSC_CSP];
            snsFuncStateNegative = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_MPSC_CSN];

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MPSC_ZERO_PIN_EN)
                snsFuncStateZero = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_MPSC_CSZ];
            #endif
        }
    #endif

    order = ptrWdCfg->mpOrder;
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_TX_ENABLED)
        if (CY_CAPSENSE_CSX_GROUP == snsMethod)
        {
            /* Finds the first sensor number in mptx group */
            i = snsIndex - (snsIndex % order);
            /* Finds TX electrode of the first group sensor */
            i = ptrWdCfg->numCols + (i % ptrWdCfg->numRows);
        }
    #endif
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
        if (CY_CAPSENSE_CSD_GROUP == snsMethod)
        {
            if (snsIndex < ptrWdCfg->numCols)
            {
                /* Finds the first sensor number in mpsc group */
                i = snsIndex - (snsIndex % order);
            }
            else
            {
                order = ptrWdCfg->mpOrderRows;
                /* Finds the first sensor number in mpsc group */
                i = snsIndex - ((snsIndex - ptrWdCfg->numCols) % order);
            }
        }
    #endif

    /* Finds the first electrode of the sensor */
    eltdPinCfg = &ptrWdCfg->ptrEltdConfig[i];

    /* Finding the right vector / pattern for mpsc operation */
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_TX_ENABLED)
        if (CY_CAPSENSE_CSX_GROUP == snsMethod)
        {
            pattern = ptrWdCfg->ptrMpTable->vector;
            i = (snsIndex % ptrWdCfg->mpOrder);
        }
    #endif
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
        if (CY_CAPSENSE_CSD_GROUP == snsMethod)
        {
            pattern = (snsIndex < ptrWdCfg->numCols) ? ptrWdCfg->ptrMpTable->vector : (ptrWdCfg->ptrMpTable + 1u)->vector;

            if (snsIndex < ptrWdCfg->numCols)
            {
                i = (snsIndex % order);  /* bit position in vector */
            }
            else
            {
                i = ((snsIndex - ptrWdCfg->numCols) % order);
            }

            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MPSC_ZERO_PIN_EN)
                /* Set initial position of the zero electrode position */
                zeroPattern = (0uL != (order % 2u)) ? 1u : 0u;
            #endif
        }
    #endif

    if (0u != i)
    {
        pattern = (pattern >> i) | (pattern << (order - i));  /* rotate (adjust) the vector for the proper electrode position */

        #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED) && (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MPSC_ZERO_PIN_EN))
            if (0uL != (order % 2u))
            {
                zeroPattern = (1uL << order) >> i;  /* recalculate zero electrode position */
            }
        #endif
    }

    if (CY_CAPSENSE_MULTIPHASE_MAX_ORDER > order)
    {
        pattern &= (0x01uL << order) - 1u;  /* cut the pattern to the vector/order size */
    }

    /* Loop through all involved MPSC electrodes */
    for (j = 0u; j < order; j++)
    {
        if (0u != (pattern & 0x01u))  /* Positive electrode */
        {
            /* Loop through all pads for this electrode (ganged sensor) */
            for (i = 0u; i < eltdPinCfg->numPins; i++)
            {
                snsMask |= 0x01uL << eltdPinCfg->ptrPin[i].padNumber;
            }
        }
        else  /* Negative electrode */
        {
            /* Loop through all pads for this electrode (ganged sensor) */
            for (i = 0u; i < eltdPinCfg->numPins; i++)
            {
                snsMaskNegative |= 0x01uL << eltdPinCfg->ptrPin[i].padNumber;
            }
        }

        #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED) && (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MPSC_ZERO_PIN_EN))
            if (CY_CAPSENSE_CSD_GROUP == snsMethod)
            {
                if (0u != (zeroPattern & 0x01u))
                {
                    /* Loop through all pads for this electrode (ganged sensor) */
                    for (i = 0u; i < eltdPinCfg->numPins; i++)
                    {
                        snsMaskZero |= 0x01uL << eltdPinCfg->ptrPin[i].padNumber;
                    }
                }
            }
        #endif

        pattern >>= 0x01u;
        eltdPinCfg++;

        #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED) && (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MPSC_ZERO_PIN_EN))
            if (CY_CAPSENSE_CSD_GROUP == snsMethod)
            {
                if (0uL != (order % 2u))
                {
                    zeroPattern >>= 0x01u;
                }
            }
        #endif
    }
    Cy_CapSense_CalculateMaskRegisters(snsMask, snsFuncState, ptrSensorCfgLoc);
    Cy_CapSense_CalculateMaskRegisters(snsMaskNegative, snsFuncStateNegative, ptrSensorCfgLoc);

    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED) && (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MPSC_ZERO_PIN_EN))
        if (CY_CAPSENSE_CSD_GROUP == snsMethod)
        {
            if (0uL != (order % 2u))
            {
                Cy_CapSense_CalculateMaskRegisters(snsMaskZero, snsFuncStateZero, ptrSensorCfgLoc);
            }
        }
    #endif
}
#endif /* CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_ENABLED */


/*******************************************************************************
* Function Name: Cy_CapSense_GenerateAllSensorConfig
********************************************************************************
*
* Generates configuration to configure registers to start
* a scan for all sensors of the specified Sensor Frame.
*
* \param snsFrameType
* The Sensor Frame type:
* * CY_CAPSENSE_SNS_FRAME_ACTIVE     - Sensor frame for Active slot
* * CY_CAPSENSE_SNS_FRAME_LOW_POWER  - Sensor frame for Low Power slot
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_GenerateAllSensorConfig(
                uint32_t snsFrameType,
                cy_stc_capsense_context_t * context)
{
    uint32_t scanSlotIndex;
    const cy_stc_capsense_pin_config_t * ptrPinCfg = context->ptrPinConfig;
    uint32_t * ptrSensorCfgLoc;
    uint32_t sensorSlotNum;
    uint8_t * ptrMapping = &context->ptrInternalContext->mapPinState[0u];
    uint32_t snsMethod;
    uint32_t snsMaskInactive = 0u;
    uint32_t snsFuncState = 0u;
    uint32_t wdIndex;
    const cy_stc_capsense_widget_config_t * ptrWdCfg;
    const cy_stc_capsense_scan_slot_t * ptrScanSlots;

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN)
        uint32_t snsFuncStateSelfCap;
    #endif
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
        uint32_t snsFuncStateMutualCap;
    #endif
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN)  
        uint32_t snsFuncStateInductive;
    #endif

    uint32_t i = 0u;
    uint32_t snsMask = 0u;
    uint32_t snsIndex;
    cy_stc_capsense_electrode_config_t const * eltdPinCfg;

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        ptrScanSlots = (snsFrameType == CY_CAPSENSE_SNS_FRAME_ACTIVE) ? (context->ptrScanSlots) : (context->ptrLpScanSlots);
    #else
        ptrScanSlots = context->ptrScanSlots;
    #endif

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN)
        #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) || (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_SHIELD_EN))
            uint32_t snsMaskInactiveIsx = 0u;
            uint32_t numEltd;
            uint32_t eltdIndex;
        #endif
    #endif

    /* Create mask for all project electrodes */
    for (i = 0u; i < context->ptrCommonConfig->numPin; i++)
    {
        snsMask |= (0x01uL << ptrPinCfg->padNumber);
        ptrPinCfg++;
    }

    /* Add to mask all shield electrodes (if present) */
    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_SHIELD_EN)
        ptrPinCfg = context->ptrShieldPinConfig;
        for (i = 0u; i < context->ptrCommonConfig->csdShieldNumPin; i++)
        {
            snsMask |= (0x01uL << ptrPinCfg->padNumber);
            ptrPinCfg++;
        }
    #endif /*  (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_SHIELD_EN) */

    snsMaskInactive = snsMask;

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN)
        /* Create separate inactive mask of ISX pins only */
        #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) || (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_SHIELD_EN))
            for (wdIndex = 0u; wdIndex < context->ptrCommonConfig->numWd; wdIndex++)
            {
                ptrWdCfg = &context->ptrWdConfig[wdIndex];
                snsMethod = ptrWdCfg->senseMethod;

                if (CY_CAPSENSE_ISX_GROUP == snsMethod)
                {
                    numEltd = (uint32_t)ptrWdCfg->numRows + ptrWdCfg->numCols;
                    eltdPinCfg = ptrWdCfg->ptrEltdConfig;

                    for (eltdIndex = 0u; eltdIndex < numEltd; eltdIndex++)
                    {
                        /* Loop through all pads for this electrode (ganged sensor) */
                        for (i = 0u; i < eltdPinCfg->numPins; i++)
                        {
                            snsMaskInactiveIsx |= (0x01uL << eltdPinCfg->ptrPin[i].padNumber);
                        }
                        eltdPinCfg++;
                    }
                }
            }
        #endif /* ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) || (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_SHIELD_EN)) */
    #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN) */

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
        /* Define inactive pin state for CSX scans */
        switch (context->ptrInternalContext->intrCsxInactSnsConn)
        {
            case CY_CAPSENSE_SNS_CONNECTION_HIGHZ:
                snsFuncStateMutualCap = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_HIGH_Z];
                break;
            case CY_CAPSENSE_SNS_CONNECTION_VDDA_BY_2:
                snsFuncStateMutualCap = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_CSX_VDDA2];
                break;
            default:
                snsFuncStateMutualCap = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_GND];
                break;
        }
    #endif

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN)
        /* Define inactive pin state for ISX scans */
        switch (context->ptrInternalContext->intrIsxInactSnsConn)
        {
            case CY_CAPSENSE_SNS_CONNECTION_GROUND:
                snsFuncStateInductive = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_GND];
                break;
            default:
                snsFuncStateInductive = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_HIGH_Z];
                break;
        }
    #endif

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN)
        /* Define inactive pin state for CSD scans */
        switch (context->ptrInternalContext->intrCsdInactSnsConn)
        {
            case CY_CAPSENSE_SNS_CONNECTION_HIGHZ:
                snsFuncStateSelfCap = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_HIGH_Z];
                break;
            case CY_CAPSENSE_SNS_CONNECTION_SHIELD:
                #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SHIELD_PASSIVE_EN)
                    snsFuncStateSelfCap = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_PAS_SHIELD];
                #else
                    snsFuncStateSelfCap = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_ACT_SHIELD];
                #endif
                break;
            default:
                snsFuncStateSelfCap = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_GND];
                break;
        }
    #endif

    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
        if (CY_CAPSENSE_SNS_FRAME_LOW_POWER == snsFrameType)
        {
            sensorSlotNum = CY_CAPSENSE_SLOT_LP_COUNT;
            ptrSensorCfgLoc = context->ptrSensorFrameLpContext;
            ptrScanSlots = context->ptrLpScanSlots;
        }
        else
        {
            sensorSlotNum = CY_CAPSENSE_SLOT_COUNT;
            ptrSensorCfgLoc = context->ptrSensorFrameContext;
            ptrScanSlots = context->ptrScanSlots;
        }
    #else
        sensorSlotNum = CY_CAPSENSE_SLOT_COUNT;
        ptrSensorCfgLoc = context->ptrSensorFrameContext;
        ptrScanSlots = context->ptrScanSlots;
    #endif

    for (scanSlotIndex = 0u; scanSlotIndex < sensorSlotNum; scanSlotIndex++)
    {
        (void)Cy_CapSense_GenerateSensorConfig(snsFrameType, scanSlotIndex, ptrSensorCfgLoc, context);

        snsIndex = ptrScanSlots[scanSlotIndex].snsId;
        wdIndex = ptrScanSlots[scanSlotIndex].wdId;
        ptrWdCfg = &context->ptrWdConfig[wdIndex];
        snsMethod = ptrWdCfg->senseMethod;

        switch(snsMethod)
        {
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN)
                case CY_CAPSENSE_CSD_GROUP:
                    snsFuncState = snsFuncStateSelfCap;
                    break;
            #endif
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
                case CY_CAPSENSE_CSX_GROUP:
                    snsFuncState = snsFuncStateMutualCap;
                    break;
            #endif
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN)
                case CY_CAPSENSE_ISX_GROUP:
                    snsFuncState = snsFuncStateInductive;
                    break;
            #endif
                default:
                    /* Do nothing */
                    break;
        }

        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_LP_EN)
            if (CY_CAPSENSE_SNS_FRAME_LOW_POWER == snsFrameType)
            {
                ptrSensorCfgLoc += (CY_MSCLP_11_SNS_REGS - CY_MSCLP_6_SNS_REGS);
            }
        #endif

        /* INACTIVE SENSORS */ 
        Cy_CapSense_CalculateMaskRegisters(snsMaskInactive, snsFuncState, ptrSensorCfgLoc);

        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN)
            /* 
            * The previous call of Cy_CapSense_CalculateMaskRegisters() configures all pins to ISC. 
            * This call overwrites previous configuration for ISX electrodes since they can support only High-Z state. 
            */
            #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) || (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_SHIELD_EN))
                if (((CY_CAPSENSE_CSX_GROUP == snsMethod) && (ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_CSX_VDDA2] == (uint8_t)snsFuncState)) ||
                    ((CY_CAPSENSE_CSD_GROUP == snsMethod) && 
                    ((ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_PAS_SHIELD] == (uint8_t)snsFuncState) ||
                     (ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_ACT_SHIELD] == (uint8_t)snsFuncState))))
                {
                    Cy_CapSense_CalculateMaskRegisters(snsMaskInactiveIsx, ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_GND], ptrSensorCfgLoc);
                }
            #endif
        #endif

        /* SHIELD ELECTRODE */
        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_SHIELD_EN)
            if (0u < context->ptrCommonConfig->csdShieldNumPin)
            {
                snsMask = 0u;

                if (CY_CAPSENSE_CSD_GROUP == snsMethod)
                {
                    #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SHIELD_PASSIVE_EN)
                        snsFuncState = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_PAS_SHIELD];
                    #else
                        snsFuncState = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_ACT_SHIELD];
                    #endif
                }

                for (i = 0u; i < context->ptrCommonConfig->csdShieldNumPin; i++)
                {
                    snsMask |= 0x01uL << context->ptrShieldPinConfig[i].padNumber;
                }
                Cy_CapSense_CalculateMaskRegisters(snsMask, snsFuncState, ptrSensorCfgLoc);
            }
        #endif

        /* ACTIVE SELF-CAP SENSOR */
        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN)
            if (CY_CAPSENSE_CSD_GROUP == snsMethod)
            {
                #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED)
                    if (((CY_CAPSENSE_MPSC_MIN_ORDER <= ptrWdCfg->mpOrder) && (snsIndex < ptrWdCfg->numCols)) ||      /* for cols */
                        ((CY_CAPSENSE_MPSC_MIN_ORDER <= ptrWdCfg->mpOrderRows) && (snsIndex >= ptrWdCfg->numCols)))   /* for rows */
                    {
                        Cy_CapSense_GenerateMultiphaseSensorConfig(snsFrameType, scanSlotIndex, ptrSensorCfgLoc, context);
                    }
                    else
                    {
                        snsMask = 0u;
                        snsFuncState = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_CSD_SNS];
                        eltdPinCfg = &ptrWdCfg->ptrEltdConfig[snsIndex];
                        /* Loop through all pads for this electrode (ganged sensor) */
                        for (i = 0u; i < eltdPinCfg->numPins; i++)
                        {
                            snsMask |= 0x01uL << eltdPinCfg->ptrPin[i].padNumber;
                        }
                        Cy_CapSense_CalculateMaskRegisters(snsMask, snsFuncState, ptrSensorCfgLoc);
                    }
                #else
                    snsMask = 0u;
                    snsFuncState = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_CSD_SNS];
                    eltdPinCfg = &ptrWdCfg->ptrEltdConfig[snsIndex];
                    /* Loop through all pads for this electrode (ganged sensor) */
                    for (i = 0u; i < eltdPinCfg->numPins; i++)
                    {
                        snsMask |= 0x01uL << eltdPinCfg->ptrPin[i].padNumber;
                    }
                    Cy_CapSense_CalculateMaskRegisters(snsMask, snsFuncState, ptrSensorCfgLoc);
                #endif /* CY_CAPSENSE_ENABLE == CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED */
            }
        #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_EN) */

        /* ACTIVE MUTUAL-CAP SENSOR */
        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN)
            if (CY_CAPSENSE_CSX_GROUP == snsMethod)
            {
                /* RX ELECTRODE */
                snsMask = 0u;
                snsFuncState = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_CSX_RX];
                i = snsIndex / ptrWdCfg->numRows;
                eltdPinCfg = &ptrWdCfg->ptrEltdConfig[i];

                /* Loop through all pads for this electrode (ganged sensor) */
                for (i = 0u; i < eltdPinCfg->numPins; i++)
                {
                    snsMask |= 0x01uL << eltdPinCfg->ptrPin[i].padNumber;
                }
                Cy_CapSense_CalculateMaskRegisters(snsMask, snsFuncState, ptrSensorCfgLoc);

                /* Handles multi-phase TX feature */
                #if (CY_CAPSENSE_DISABLE != CY_CAPSENSE_MULTI_PHASE_TX_ENABLED)
                    if (ptrWdCfg->mpOrder >= CY_CAPSENSE_MPTX_MIN_ORDER)
                    {
                        Cy_CapSense_GenerateMultiphaseSensorConfig(snsFrameType, scanSlotIndex, ptrSensorCfgLoc, context);
                    }
                    else
                    {
                        /* TX ELECTRODE */
                        snsMask = 0u;
                        snsFuncState = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_CSX_TX];
                        i = ptrWdCfg->numCols +
                                (snsIndex % ptrWdCfg->numRows);
                        eltdPinCfg = &ptrWdCfg->ptrEltdConfig[i];

                        /* Loop through all pads for this electrode (ganged sensor) */
                        for (i = 0u; i < eltdPinCfg->numPins; i++)
                        {
                            snsMask |= 0x01uL << eltdPinCfg->ptrPin[i].padNumber;
                        }
                        Cy_CapSense_CalculateMaskRegisters(snsMask, snsFuncState, ptrSensorCfgLoc);
                    }
                #else
                    /* TX ELECTRODE */
                    snsMask = 0u;
                    snsFuncState = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_CSX_TX];
                    i = ptrWdCfg->numCols + (snsIndex % ptrWdCfg->numRows);
                    eltdPinCfg = &ptrWdCfg->ptrEltdConfig[i];

                    /* Loop through all pads for this electrode (ganged sensor) */
                    for (i = 0u; i < eltdPinCfg->numPins; i++)
                    {
                        snsMask |= 0x01uL << eltdPinCfg->ptrPin[i].padNumber;
                    }
                    Cy_CapSense_CalculateMaskRegisters(snsMask, snsFuncState, ptrSensorCfgLoc);
                #endif
            }
        #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_EN) */

        /* ACTIVATE INDUCTIVE SENSOR */
        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN)
            if (CY_CAPSENSE_ISX_GROUP == snsMethod)
            {
                /* RX ELECTRODE */
                snsMask = 0u;
                snsFuncState = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_ISX_RX];
                i = snsIndex;
                eltdPinCfg = &ptrWdCfg->ptrEltdConfig[i];

                /* Loop through all pads for this electrode (ganged sensor) */
                for (i = 0u; i < eltdPinCfg->numPins; i++)
                {
                    snsMask |= 0x01uL << eltdPinCfg->ptrPin[i].padNumber;
                }
                Cy_CapSense_CalculateMaskRegisters(snsMask, snsFuncState, ptrSensorCfgLoc);

                /* LX ELECTRODE */
                snsMask = 0u;
                snsFuncState = ptrMapping[CY_CAPSENSE_PIN_STATE_IDX_ISX_LX];
                i = snsIndex + ptrWdCfg->numRows;
                eltdPinCfg = &ptrWdCfg->ptrEltdConfig[i];

                /* Loop through all pads for this electrode (ganged sensor) */
                for (i = 0u; i < eltdPinCfg->numPins; i++)
                {
                    snsMask |= 0x01uL << eltdPinCfg->ptrPin[i].padNumber;
                }
                Cy_CapSense_CalculateMaskRegisters(snsMask, snsFuncState, ptrSensorCfgLoc);
            }
        #endif /* (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_EN) */

        ptrSensorCfgLoc +=  CY_MSCLP_6_SNS_REGS;
        #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_RC_HW_IIR_FILTER_EN)
            if (CY_CAPSENSE_SNS_FRAME_LOW_POWER != snsFrameType)
            {
                ptrSensorCfgLoc++;
            }
        #endif
    }
}


/*******************************************************************************
* Function Name: Cy_CapSense_CalculateMaskRegisters
****************************************************************************//**
*
* Calculates the mask for pins that have to be updated for Control MUX
* connection.
*
* \param mask
* Specifies the mask of pins that should be updated.
*
* \param funcState
* Specifies the pin state functionality.
*
* \param ptrCfg
* Specifies the pointer to the mask registers.
*
*******************************************************************************/
void Cy_CapSense_CalculateMaskRegisters(
                uint32_t mask,
                uint32_t funcState,
                uint32_t * ptrCfg)
{
    uint32_t * ptrCfgMask = ptrCfg;

    ptrCfgMask[0u] &= ~mask;
    ptrCfgMask[1u] &= ~mask;
    ptrCfgMask[2u] &= ~mask;
    if (0u != (funcState & 0x04u))
    {
        ptrCfgMask[0u] |= mask;
    }
    if (0u != (funcState & 0x02u))
    {
        ptrCfgMask[1u] |= mask;
    }
    if (0u != (funcState & 0x01u))
    {
        ptrCfgMask[2u] |= mask;
    }
}


/*******************************************************************************
* Function Name: Cy_CapSense_GenerateCdacConfig
****************************************************************************//**
*
* Generates the Cap DAC configuration for a selected sensor.
*
* \param ptrScanSlot
* The pointer to the slot structure \ref cy_stc_capsense_scan_slot_t.
*
* \param ptrSensorCfg
* Specifies the pointer to the sensor configuration to be filled.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
* \return
* Returns the status of the operation:
* - CY_CAPSENSE_STATUS_SUCCESS       - The operation is performed successfully.
*
*******************************************************************************/
cy_capsense_status_t Cy_CapSense_GenerateCdacConfig(
                const cy_stc_capsense_scan_slot_t * ptrScanSlot,
                uint32_t * ptrSensorCfg,
                const cy_stc_capsense_context_t * context)
{
    cy_capsense_status_t capStatus = CY_CAPSENSE_STATUS_SUCCESS;
    uint32_t compDiv;
    uint32_t wdIndex = ptrScanSlot->wdId;
    uint32_t snsIndex = ptrScanSlot->snsId;
    const cy_stc_capsense_widget_config_t * ptrWdCfg = &context->ptrWdConfig[wdIndex];
    uint32_t snsCdacCtlReg = MSCLP_SNS_SNS_CDAC_CTL_CLOCK_REF_RATE_Msk;
    uint8_t senseMethod = ptrWdCfg->senseMethod;
    cy_stc_capsense_internal_context_t * ptrIntCxt = context->ptrInternalContext;

    /* Compensation CDAC Divider */
    compDiv = context->ptrWdContext[wdIndex].cdacCompDivider;
    compDiv = (compDiv > 0u) ? (compDiv - 1u) : 0u;
    ptrSensorCfg[CY_CAPSENSE_SNS_SCAN_CTL_INDEX] |= _VAL2FLD(MSCLP_SNS_SNS_SCAN_CTL_COMP_DIV, compDiv);

    if (((CY_CAPSENSE_CSD_GROUP == senseMethod) && (CY_CAPSENSE_ENABLE == ptrIntCxt->csdCdacDitherEn)) ||
        ((CY_CAPSENSE_CSX_GROUP == senseMethod) && (CY_CAPSENSE_ENABLE == ptrIntCxt->csxCdacDitherEn)) ||
        ((CY_CAPSENSE_ISX_GROUP == senseMethod) && (CY_CAPSENSE_ENABLE == ptrIntCxt->isxCdacDitherEn)))
    {
        snsCdacCtlReg |= _VAL2FLD(MSCLP_SNS_SNS_CDAC_CTL_LFSR_SCALE_FL, ptrWdCfg->ptrWdContext->cdacDitherValue) |
                         _VAL2FLD(MSCLP_SNS_SNS_CDAC_CTL_FL_MODE, 1uL); /* the same as it was for msc */
    }

    #if (0u != CY_CAPSENSE_LIQUID_LEVEL_EN)
        /* Uses configuration from Configurator for LLW if tuning is complete */
        if (((uint8_t)CY_CAPSENSE_WD_LIQUID_LEVEL_E == ptrWdCfg->wdType) &&
            (0u != (ptrWdCfg->centroidConfig & CY_CAPSENSE_LLW_TUNING_COMPLETED_MASK)))
        {
            snsCdacCtlReg |= _VAL2FLD(MSCLP_SNS_SNS_CDAC_CTL_SEL_RE, ptrWdCfg->ptrWdContext->cdacRef);
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_FINE_EN)
                snsCdacCtlReg |= _VAL2FLD(MSCLP_SNS_SNS_CDAC_CTL_SEL_CF, ptrWdCfg->ptrWdContext->cdacFine);
            #endif
            #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_COMP_EN)
                snsCdacCtlReg |= _VAL2FLD(MSCLP_SNS_SNS_CDAC_CTL_SEL_CO, ptrWdCfg->ptrSnsContext[snsIndex].cdacComp);
            #endif
        }
    #endif
    /* Ref CDAC Code setup */
    if ((CY_CAPSENSE_CDAC_MODE_MANUAL == ((ptrWdCfg->cdacConfig & CY_CAPSENSE_CDAC_REF_MODE_MASK) >> CY_CAPSENSE_CDAC_REF_MODE_POS)) ||
        (0u != (CY_CAPSENSE_MW_STATE_SMARTSENSE_MASK & context->ptrCommonContext->status)))
    {
        if ((CY_CAPSENSE_CSD_GROUP == senseMethod) &&
            (ptrWdCfg->numCols <= snsIndex))
        {
            snsCdacCtlReg |= _VAL2FLD(MSCLP_SNS_SNS_CDAC_CTL_SEL_RE, ptrWdCfg->ptrWdContext->rowCdacRef);
        }
        else
        {
            snsCdacCtlReg |= _VAL2FLD(MSCLP_SNS_SNS_CDAC_CTL_SEL_RE, ptrWdCfg->ptrWdContext->cdacRef);
        }
    }

    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_FINE_EN) || \
         (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CDAC_FINE_EN) || \
         (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CDAC_FINE_EN))
        /* Ref-Fine CDAC Code setup */
        if (CY_CAPSENSE_CDAC_MODE_MANUAL == ((ptrWdCfg->cdacConfig & CY_CAPSENSE_CDAC_FINE_MODE_MASK) >> CY_CAPSENSE_CDAC_FINE_MODE_POS))
        {
            if ((CY_CAPSENSE_CSD_GROUP == senseMethod) &&
                (ptrWdCfg->numCols <= snsIndex))
            {
                snsCdacCtlReg |= _VAL2FLD(MSCLP_SNS_SNS_CDAC_CTL_SEL_CF, ptrWdCfg->ptrWdContext->rowCdacFine);
            }
            else
            {
                snsCdacCtlReg |= _VAL2FLD(MSCLP_SNS_SNS_CDAC_CTL_SEL_CF, ptrWdCfg->ptrWdContext->cdacFine);
            }
        }
    #endif

    #if ((CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_COMP_EN) || \
         (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CDAC_COMP_EN) || \
         (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CDAC_COMP_EN))
        if (CY_CAPSENSE_CDAC_MODE_MANUAL == ((ptrWdCfg->cdacConfig & CY_CAPSENSE_CDAC_COMP_MODE_MASK) >> CY_CAPSENSE_CDAC_COMP_MODE_POS))
        {
            switch (senseMethod)
            {
                #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSD_CDAC_COMP_EN)
                    case CY_CAPSENSE_CSD_GROUP :
                #endif /* CY_CAPSENSE_CSD_CDAC_COMP_EN */
                #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_CSX_CDAC_COMP_EN)
                    case CY_CAPSENSE_CSX_GROUP :
                #endif /* CY_CAPSENSE_CSX_CDAC_COMP_EN */
                #if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_ISX_CDAC_COMP_EN)
                    case CY_CAPSENSE_ISX_GROUP :
                #endif /* CY_CAPSENSE_ISX_CDAC_COMP_EN */
                        snsCdacCtlReg |= _VAL2FLD(MSCLP_SNS_SNS_CDAC_CTL_SEL_CO, ptrWdCfg->ptrSnsContext[snsIndex].cdacComp);
                        break;
                default:
                    /* No action for other methods */
                    break;
            }
        }
    #endif

    ptrSensorCfg[CY_CAPSENSE_SNS_CDAC_CTL_INDEX] = snsCdacCtlReg;

    return capStatus;
}


/*******************************************************************************
* Function Name: Cy_CapSense_GenerateModeConfig
****************************************************************************//**
*
* Configures mode-related registers in base configuration per defined
* CapSense configuration.
*
* \param context
* The pointer to the CAPSENSE&trade; context structure \ref cy_stc_capsense_context_t.
*
*******************************************************************************/
void Cy_CapSense_GenerateModeConfig(const cy_stc_capsense_context_t * context)
{
    const cy_stc_msclp_mode_config_t modeArr[CY_CAPSENSE_REG_MODE_NUMBER] = CY_CAPSENSE_SM_MODES_ARR;
    cy_stc_msclp_mode_config_t * mode = context->ptrBaseFrameContext->mode;

    mode[CY_CAPSENSE_REG_MODE_CSD] = modeArr[CY_CAPSENSE_REG_MODE_CSD];
    mode[CY_CAPSENSE_REG_MODE_CSX] = modeArr[CY_CAPSENSE_REG_MODE_CSX];
    mode[CY_CAPSENSE_REG_MODE_ISX] = modeArr[CY_CAPSENSE_REG_MODE_ISX];

    if (CY_CAPSENSE_ENABLE == context->ptrInternalContext->csdCdacDitherEn)
    {
        mode[CY_CAPSENSE_REG_MODE_CSD] = modeArr[CY_CAPSENSE_MODE_IDX_CSD_DITHERING];
    }

    if (CY_CAPSENSE_ENABLE == context->ptrInternalContext->csxCdacDitherEn)
    {
        mode[CY_CAPSENSE_REG_MODE_CSX] = modeArr[CY_CAPSENSE_MODE_IDX_CSX_DITHERING];
    }

    if (CY_CAPSENSE_SNS_CONNECTION_VDDA_BY_2 == context->ptrInternalContext->intrCsxInactSnsConn)
    {
        /* Close the reference to filter switch */
        mode[CY_CAPSENSE_REG_MODE_CSX].swSelSh |= MSCLP_MODE_SW_SEL_SH_SOMB_Msk;
    }

    if (CY_CAPSENSE_ENABLE == context->ptrInternalContext->isxCdacDitherEn)
    {
        mode[CY_CAPSENSE_REG_MODE_ISX] = modeArr[CY_CAPSENSE_MODE_IDX_ISX_DITHERING];
    }
}


/*******************************************************************************
* Function Name: Cy_CapSense_AdjustSnsClkDivider
****************************************************************************//**
*
* If the PRS is selected as the Sense Clock source, adjusts the Sense Clock
* divider to obtain the max frequency of the PRS sequence equal to
* ModClkFreq / SenseClkDivider. Updates the sense Clock divider with the minimal
* supported value in case if it is out of range for the specified parameters.
*
* \param snsMethod
*  Specifies the widget group:
*   - CSD (CY_CAPSENSE_CSD_GROUP)
*   - CSX (CY_CAPSENSE_CSX_GROUP)
*   - ISX (CY_CAPSENSE_ISX_GROUP)
*
* \param snsClkSource
*  Specifies the sense Clock source, supported by MSCv3 HW:
*   - CY_CAPSENSE_CLK_SOURCE_DIRECT
*   - CY_CAPSENSE_CLK_SOURCE_SSC
*   - CY_CAPSENSE_CLK_SOURCE_PRS
*
* \param snsClkDivider
* The divider value for the sense clock.
*
* \return
*  Adjusted value of the Sense Clock divider.
*
*******************************************************************************/
uint32_t Cy_CapSense_AdjustSnsClkDivider(
                        uint8_t snsMethod,
                        uint8_t snsClkSource,
                        uint16_t snsClkDivider)
{
    uint32_t retVal = (uint32_t)snsClkDivider;

    if (CY_CAPSENSE_CLK_SOURCE_PRS == ((uint32_t)snsClkSource & CY_CAPSENSE_CLK_SOURCE_MASK))
    {
        if ((CY_CAPSENSE_CSD_GROUP == snsMethod) ||
            (CY_CAPSENSE_ISX_GROUP == snsMethod))
        {
            retVal >>= CY_CAPSENSE_4PH_PRS_SNS_CLOCK_DIVIDER_SHIFT;
        }
        else
        {
            retVal >>= CY_CAPSENSE_2PH_PRS_SNS_CLOCK_DIVIDER_SHIFT;
        }
    }

    return retVal;
}


#endif /* CY_IP_M0S8MSCV3LP */


/* [] END OF FILE */
