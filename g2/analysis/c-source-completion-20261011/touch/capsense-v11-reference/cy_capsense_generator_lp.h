/***************************************************************************//**
* \file cy_capsense_generator_lp.h
* \version 11.0.0
*
* \brief
* This file provides the function prototypes specific to the register
* map generation module.
*
********************************************************************************
* \copyright
* (c) 2020-2026, Infineon Technologies AG, or an affiliate of Infineon
* Technologies AG. All rights reserved.
* This software, associated documentation and materials ("Software") is
* owned by Infineon Technologies AG or one of its affiliates ("Infineon")
* and is protected by and subject to worldwide patent protection, worldwide
* copyright laws, and international treaty provisions. Therefore, you may use
* this Software only as provided in the license agreement accompanying the
* software package from which you obtained this Software. If no license
* agreement applies, then any use, reproduction, modification, translation, or
* compilation of this Software is prohibited without the express written
* permission of Infineon.
*
* Disclaimer: UNLESS OTHERWISE EXPRESSLY AGREED WITH INFINEON, THIS SOFTWARE
* IS PROVIDED AS-IS, WITH NO WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
* INCLUDING, BUT NOT LIMITED TO, ALL WARRANTIES OF NON-INFRINGEMENT OF
* THIRD-PARTY RIGHTS AND IMPLIED WARRANTIES SUCH AS WARRANTIES OF FITNESS FOR A
* SPECIFIC USE/PURPOSE OR MERCHANTABILITY.
* Infineon reserves the right to make changes to the Software without notice.
* You are responsible for properly designing, programming, and testing the
* functionality and safety of your intended application of the Software, as
* well as complying with any legal requirements related to its use. Infineon
* does not guarantee that the Software will be free from intrusion, data theft
* or loss, or other breaches ("Security Breaches"), and Infineon shall have
* no liability arising out of any Security Breaches. Unless otherwise
* explicitly approved by Infineon, the Software may not be used in any
* application where a failure of the Product or any consequences of the use
* thereof can reasonably be expected to result in personal injury.
*******************************************************************************/


#if !defined(CY_CAPSENSE_GENERATOR_LP_H)
#define CY_CAPSENSE_GENERATOR_LP_H

#include "cy_capsense_common.h"
#include "cy_capsense_structure.h"
#include "cy_capsense_sm_base_full_wave_lp.h"

#if (defined(CY_IP_M0S8MSCV3LP))

#if defined(__cplusplus)
extern "C" {
#endif

/*******************************************************************************
* Function Prototypes
*******************************************************************************/

/******************************************************************************/
/** \cond SECTION_CAPSENSE_INTERNAL */
/** \addtogroup group_capsense_internal *//** \{ */
/******************************************************************************/
cy_capsense_status_t Cy_CapSense_GenerateBaseConfig(
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_GeneratePinFunctionConfig(
                const cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_GenerateModeConfig(
                const cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_GenerateSensorConfig(
                uint32_t snsFrameType,
                uint32_t scanSlot,
                uint32_t * ptrSensorCfg,
                cy_stc_capsense_context_t * context);
void Cy_CapSense_GenerateAllSensorConfig(
                uint32_t snsFrameType,
                cy_stc_capsense_context_t * context);
cy_capsense_status_t Cy_CapSense_GenerateCdacConfig(
                const cy_stc_capsense_scan_slot_t * ptrScanSlot,
                uint32_t * ptrSensorCfg,
                const cy_stc_capsense_context_t * context);
void Cy_CapSense_CalculateMaskRegisters(
                uint32_t mask,
                uint32_t funcState,
                uint32_t * ptrCfg);
uint32_t Cy_CapSense_AdjustSnsClkDivider(
                uint8_t snsMethod,
                uint8_t snsClkSource,
                uint16_t snsClkDivider);
void Cy_CapSense_ApplyWidgetCdacParam(
                uint32_t widgetId,
                cy_stc_capsense_context_t * context);
/** \} \endcond */


/*******************************************************************************
* Sensing modes
*******************************************************************************/
/** CSD sense mode configuration index */
#define CY_CAPSENSE_REG_MODE_CSD                        (0u)
/** CSX sense mode configuration index */
#define CY_CAPSENSE_REG_MODE_CSX                        (1u)
/** ISX sense mode configuration index */
#define CY_CAPSENSE_REG_MODE_ISX                        (2u)
/** CSD sense mode configuration index with CapDAC dithering enabled */
#define CY_CAPSENSE_REG_MODE_CSD_DITHERING              (3u)
/** CSX sense mode configuration index with CapDAC dithering enabled */
#define CY_CAPSENSE_REG_MODE_CSX_DITHERING              (4u)
/** ISX sense mode configuration index with CapDAC dithering enabled */
#define CY_CAPSENSE_REG_MODE_ISX_DITHERING              (5u)
/** WBX sense mode configuration index */
#define CY_CAPSENSE_REG_MODE_WBX                        (6u)
/** Sense mode undefined */
#define CY_CAPSENSE_REG_MODE_UNDEFINED                  (255u)


/*******************************************************************************
* Sensor Config Register indexes in the frame
*******************************************************************************/
#define CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL0                                  (0u)
#define CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL1                                  (1u)
#define CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL2                                  (2u)
#define CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL3                                  (3u)
#define CY_CAPSENSE_FRM_LP_SNS_LP_AOS_SNS_CTL4                                  (4u)
#define CY_CAPSENSE_FRM_LP_SNS_SW_SEL_CSW_LO_MASK2_INDEX                        (5u)
#define CY_CAPSENSE_FRM_LP_SNS_SW_SEL_CSW_LO_MASK1_INDEX                        (6u)
#define CY_CAPSENSE_FRM_LP_SNS_SW_SEL_CSW_LO_MASK0_INDEX                        (7u)
#define CY_CAPSENSE_FRM_LP_SNS_SCAN_CTL_INDEX                                   (8u)
#define CY_CAPSENSE_FRM_LP_SNS_CDAC_CTL_INDEX                                   (9u)
#define CY_CAPSENSE_FRM_LP_SNS_CTL_INDEX                                        (10u)

#define CY_CAPSENSE_SNS_SW_SEL_CSW_LO_MASK2_INDEX                               (0u)
#define CY_CAPSENSE_SNS_SW_SEL_CSW_LO_MASK1_INDEX                               (1u)
#define CY_CAPSENSE_SNS_SW_SEL_CSW_LO_MASK0_INDEX                               (2u)
#define CY_CAPSENSE_SNS_SCAN_CTL_INDEX                                          (3u)
#define CY_CAPSENSE_SNS_CDAC_CTL_INDEX                                          (4u)
#define CY_CAPSENSE_SNS_CTL_INDEX                                               (5u)
#define CY_CAPSENSE_SNS_HW_IIR_INDEX                                            (6u)


/*******************************************************************************
* Scaling Macros
*******************************************************************************/
#define CY_CAPSENSE_CDAC_REF_MAX_VALUE                                          (255u)
#define CY_CAPSENSE_CDAC_FINE_MAX_VALUE                                         (31u)
#define CY_CAPSENSE_CDAC_COMP_MAX_VALUE                                         (255u)
#define CY_CAPSENSE_CDAC_REF_MIN_VALUE                                          (1u)
#define CY_CAPSENSE_CDAC_FINE_MIN_VALUE                                         (1u)
#define CY_CAPSENSE_CDAC_COMP_MIN_VALUE                                         (0u)
#define CY_CAPSENSE_CDAC_TRIM_MIDDLE_POINT                                      (32768u)
#define CY_CAPSENSE_CDAC_TRIM_ROUND                                             (16384u)
#define CY_CAPSENSE_CDAC_TRIM_OFFSET                                            (15u)
#define CY_CAPSENSE_CDAC_TRIM_OVERFLOW_OFFSET                                   (6u)
#define CY_CAPSENSE_CDAC_FINE_LSB_X100                                          (260u)


/*******************************************************************************
* Macros for Cmod selection
*******************************************************************************/
#define CY_CAPSENSE_CMOD12_PAIR_SELECTION                                       (0uL)


/* CSW0 = GND */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW0_GND_VALUE \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC0_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC0_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC0_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC0_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC0_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC0_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW1 = HIGH-Z */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW1_HIGH_Z_VALUE \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC1_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC1_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC1_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC1_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC1_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC1_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW2 = CSX RX */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW2_CSX_RX_VALUE \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC2_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC2_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC2_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC2_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC2_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC2_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW3 = CSX TX */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW3_CSX_TX_VALUE \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC3_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC3_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC3_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC3_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC3_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC3_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW4 = CSX NTX */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW4_CSX_NEG_TX_VALUE \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC4_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC4_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC4_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC4_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC4_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC4_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW5 = CSD SNS */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW5_CSD_SNS_VALUE \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC5_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC5_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC5_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC5_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC5_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC5_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW6 = ISX LX */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW6_ISX_LX_VALUE \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC6_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC6_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC6_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC6_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC6_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC6_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW7 = ISX RX */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW7_ISX_RX_VALUE \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC7_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC7_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC7_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC7_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC7_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC7_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW8 = SHIELD Active */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW8_ACT_SHLD_VALUE \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC8_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC8_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC8_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC8_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC8_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC8_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW9 = SHIELD Passive */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW9_PAS_SHLD_VALUE \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC9_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC9_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC9_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC9_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC9_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC9_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW10 = VDDA/2 */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW10_VDDA2_VALUE \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC10_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC10_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC10_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC10_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC10_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC10_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW11 = CSP */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW11_CSP_VALUE \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC11_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC11_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC11_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC11_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC11_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC11_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW12 = CSN */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW12_CSN_VALUE \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC12_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC12_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC12_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC12_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC12_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC12_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW13 = CSZ */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW13_CSZ_VALUE \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC13_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC13_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC13_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC13_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC13_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC13_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW14 = Wheatstone Bridge Node A */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW14_WBX_NODE_A \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC14_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC14_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC14_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC14_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC14_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC14_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))

/* CSW15 = Wheatstone Bridge Node B */
#define CY_CAPSENSE_SM_REG_SW_SEL_CSW15_WBX_NODE_B \
((CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC15_FLD_SW_AMUXA << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXA_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC15_FLD_SW_AMUXB << MSCLP_SW_SEL_CSW_FUNC_SW_AMUXB_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC15_FLD_SW_PU    << MSCLP_SW_SEL_CSW_FUNC_SW_PU_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC15_FLD_SW_PD    << MSCLP_SW_SEL_CSW_FUNC_SW_PD_Pos)    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC15_FLD_REF_MODE << MSCLP_SW_SEL_CSW_FUNC_REF_MODE_Pos) | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CSW_FUNC15_FLD_DDRV_EN  << MSCLP_SW_SEL_CSW_FUNC_DDRV_EN_Pos))


/* Indexes of this values must correspond to the CY_CAPSENSE_CTRLMUX_PIN_STATE_... definitions in the common.h */
#define CY_CAPSENSE_PIN_STATES_ARR \
{CY_CAPSENSE_SM_REG_SW_SEL_CSW0_GND_VALUE,\
 CY_CAPSENSE_SM_REG_SW_SEL_CSW1_HIGH_Z_VALUE,\
 CY_CAPSENSE_SM_REG_SW_SEL_CSW2_CSX_RX_VALUE,\
 CY_CAPSENSE_SM_REG_SW_SEL_CSW3_CSX_TX_VALUE,\
 CY_CAPSENSE_SM_REG_SW_SEL_CSW4_CSX_NEG_TX_VALUE,\
 CY_CAPSENSE_SM_REG_SW_SEL_CSW5_CSD_SNS_VALUE,\
 CY_CAPSENSE_SM_REG_SW_SEL_CSW6_ISX_LX_VALUE,\
 CY_CAPSENSE_SM_REG_SW_SEL_CSW7_ISX_RX_VALUE,\
 CY_CAPSENSE_SM_REG_SW_SEL_CSW8_ACT_SHLD_VALUE,\
 CY_CAPSENSE_SM_REG_SW_SEL_CSW9_PAS_SHLD_VALUE,\
 CY_CAPSENSE_SM_REG_SW_SEL_CSW10_VDDA2_VALUE, \
 CY_CAPSENSE_SM_REG_SW_SEL_CSW11_CSP_VALUE, \
 CY_CAPSENSE_SM_REG_SW_SEL_CSW12_CSN_VALUE, \
 CY_CAPSENSE_SM_REG_SW_SEL_CSW13_CSZ_VALUE, \
 CY_CAPSENSE_SM_REG_SW_SEL_CSW14_WBX_NODE_A, \
 CY_CAPSENSE_SM_REG_SW_SEL_CSW15_WBX_NODE_B}


/************************* CSD RM register values *****************************/

#define CY_CAPSENSE_CSD_RM_SENSE_DUTY_CTL \
((CY_CAPSENSE_SM_REG_MODE0_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE0_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE0_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH2_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH2_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE0_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH3_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH3_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE0_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH0_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH0_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE0_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH1_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH1_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE0_SENSE_DUTY_CTL_FLD_PH_GAP_2CYCLE_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PH_GAP_2CYCLE_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE0_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE0_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE0_SENSE_DUTY_CTL_FLD_PHX_GAP_2CYCLE_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHX_GAP_2CYCLE_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE0_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_EN       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_SHIFT_EN_Pos)        | \
 (CY_CAPSENSE_SM_REG_MODE0_SENSE_DUTY_CTL_FLD_PHASE_MODE_SEL       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_MODE_SEL_Pos))

#define CY_CAPSENSE_CSD_RM_SW_SEL_CDAC_FL \
((CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CDAC_FL_FLD_SW_FLTCA             << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTCA_Pos)              | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CDAC_FL_FLD_SW_FLCB              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLCB_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CDAC_FL_FLD_SW_FLTV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CDAC_FL_FLD_SW_FLTG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CDAC_FL_FLD_SW_FLBV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CDAC_FL_FLD_SW_FLBG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CDAC_FL_FLD_ACTIVATION_MODE      << MSCLP_MODE_SW_SEL_CDAC_FL_ACTIVATION_MODE_Pos))

#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SHIELD_ACTIVE_EN)
#define CY_CAPSENSE_CSD_RM_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE6_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_CSD_RM_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE6_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE6_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))
#elif (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SHIELD_PASSIVE_EN)
#define CY_CAPSENSE_CSD_RM_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE8_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_CSD_RM_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE8_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE8_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))
#else
#define CY_CAPSENSE_CSD_RM_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE0_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_CSD_RM_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE0_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))
#endif /* CY_CAPSENSE_ENABLE == CY_CAPSENSE_SHIELD_ACTIVE_EN */

#define CY_CAPSENSE_CSD_RM_SW_SEL_COMP \
((CY_CAPSENSE_SM_REG_MODE0_SW_SEL_COMP_FLD_CPCS1                   << MSCLP_MODE_SW_SEL_COMP_CPCS1_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_COMP_FLD_CPCS3                   << MSCLP_MODE_SW_SEL_COMP_CPCS3_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_COMP_FLD_CPMA                    << MSCLP_MODE_SW_SEL_COMP_CPMA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_COMP_FLD_CPCA                    << MSCLP_MODE_SW_SEL_COMP_CPCA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_COMP_FLD_CPCB                    << MSCLP_MODE_SW_SEL_COMP_CPCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_COMP_FLD_CMCB                    << MSCLP_MODE_SW_SEL_COMP_CMCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_COMP_FLD_CPF                     << MSCLP_MODE_SW_SEL_COMP_CPF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_COMP_FLD_CMCS2                   << MSCLP_MODE_SW_SEL_COMP_CMCS2_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_COMP_FLD_CMCS4                   << MSCLP_MODE_SW_SEL_COMP_CMCS4_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_COMP_FLD_CMV                     << MSCLP_MODE_SW_SEL_COMP_CMV_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_COMP_FLD_CMG                     << MSCLP_MODE_SW_SEL_COMP_CMG_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_COMP_FLD_CMF                     << MSCLP_MODE_SW_SEL_COMP_CMF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_COMP_FLD_HALF_WAVE_EN            << MSCLP_MODE_SW_SEL_COMP_HALF_WAVE_EN_Pos))

#define CY_CAPSENSE_CSD_RM_SW_SEL_CMOD1 \
((CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD1_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD1_FLD_SW_C1CA                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CA_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD1_FLD_SW_C1CC                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CC_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD1_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD1_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD1_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD1_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD1_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD1_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD1_DDRV_EN_Pos))

#define CY_CAPSENSE_CSD_RM_SW_SEL_CMOD2 \
((CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD2_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD2_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD2_FLD_SW_C2CB                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CB_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD2_FLD_SW_C2CD                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CD_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD2_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD2_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD2_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD2_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE0_SW_SEL_CMOD2_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD2_DDRV_EN_Pos))

/************************* CSX RM register values *****************************/

#define CY_CAPSENSE_CSX_RM_SENSE_DUTY_CTL \
((CY_CAPSENSE_SM_REG_MODE1_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE1_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE1_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH2_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH2_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE1_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH3_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH3_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE1_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH0_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH0_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE1_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH1_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH1_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE1_SENSE_DUTY_CTL_FLD_PH_GAP_2CYCLE_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PH_GAP_2CYCLE_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE1_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE1_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE1_SENSE_DUTY_CTL_FLD_PHX_GAP_2CYCLE_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHX_GAP_2CYCLE_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE1_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_EN       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_SHIFT_EN_Pos)        | \
 (CY_CAPSENSE_SM_REG_MODE1_SENSE_DUTY_CTL_FLD_PHASE_MODE_SEL       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_MODE_SEL_Pos))

#define CY_CAPSENSE_CSX_RM_SW_SEL_CDAC_FL \
((CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CDAC_FL_FLD_SW_FLTCA             << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTCA_Pos)              | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CDAC_FL_FLD_SW_FLCB              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLCB_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CDAC_FL_FLD_SW_FLTV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CDAC_FL_FLD_SW_FLTG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CDAC_FL_FLD_SW_FLBV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CDAC_FL_FLD_SW_FLBG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CDAC_FL_FLD_ACTIVATION_MODE      << MSCLP_MODE_SW_SEL_CDAC_FL_ACTIVATION_MODE_Pos))

#define CY_CAPSENSE_CSX_RM_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE1_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_CSX_RM_SW_SEL_COMP \
((CY_CAPSENSE_SM_REG_MODE1_SW_SEL_COMP_FLD_CPCS1                   << MSCLP_MODE_SW_SEL_COMP_CPCS1_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_COMP_FLD_CPCS3                   << MSCLP_MODE_SW_SEL_COMP_CPCS3_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_COMP_FLD_CPMA                    << MSCLP_MODE_SW_SEL_COMP_CPMA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_COMP_FLD_CPCA                    << MSCLP_MODE_SW_SEL_COMP_CPCA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_COMP_FLD_CPCB                    << MSCLP_MODE_SW_SEL_COMP_CPCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_COMP_FLD_CMCB                    << MSCLP_MODE_SW_SEL_COMP_CMCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_COMP_FLD_CPF                     << MSCLP_MODE_SW_SEL_COMP_CPF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_COMP_FLD_CMCS2                   << MSCLP_MODE_SW_SEL_COMP_CMCS2_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_COMP_FLD_CMCS4                   << MSCLP_MODE_SW_SEL_COMP_CMCS4_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_COMP_FLD_CMV                     << MSCLP_MODE_SW_SEL_COMP_CMV_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_COMP_FLD_CMG                     << MSCLP_MODE_SW_SEL_COMP_CMG_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_COMP_FLD_CMF                     << MSCLP_MODE_SW_SEL_COMP_CMF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_COMP_FLD_HALF_WAVE_EN            << MSCLP_MODE_SW_SEL_COMP_HALF_WAVE_EN_Pos))

#define CY_CAPSENSE_CSX_RM_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE1_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))

#define CY_CAPSENSE_CSX_RM_SW_SEL_CMOD1 \
((CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD1_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD1_FLD_SW_C1CA                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CA_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD1_FLD_SW_C1CC                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CC_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD1_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD1_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD1_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD1_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD1_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD1_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD1_DDRV_EN_Pos))

#define CY_CAPSENSE_CSX_RM_SW_SEL_CMOD2 \
((CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD2_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD2_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD2_FLD_SW_C2CB                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CB_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD2_FLD_SW_C2CD                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CD_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD2_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD2_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD2_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD2_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE1_SW_SEL_CMOD2_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD2_DDRV_EN_Pos))

/************************* ISX RM register values (external VDDA/2) ***********/

#define CY_CAPSENSE_ISX_RM_SENSE_DUTY_CTL \
((CY_CAPSENSE_SM_REG_MODE2_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE2_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE2_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH2_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH2_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE2_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH3_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH3_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE2_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH0_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH0_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE2_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH1_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH1_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE2_SENSE_DUTY_CTL_FLD_PH_GAP_2CYCLE_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PH_GAP_2CYCLE_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE2_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE2_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE2_SENSE_DUTY_CTL_FLD_PHX_GAP_2CYCLE_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHX_GAP_2CYCLE_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE2_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_EN       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_SHIFT_EN_Pos)        | \
 (CY_CAPSENSE_SM_REG_MODE2_SENSE_DUTY_CTL_FLD_PHASE_MODE_SEL       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_MODE_SEL_Pos))

#define CY_CAPSENSE_ISX_RM_SW_SEL_CDAC_FL \
((CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CDAC_FL_FLD_SW_FLTCA             << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTCA_Pos)              | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CDAC_FL_FLD_SW_FLCB              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLCB_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CDAC_FL_FLD_SW_FLTV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CDAC_FL_FLD_SW_FLTG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CDAC_FL_FLD_SW_FLBV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CDAC_FL_FLD_SW_FLBG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CDAC_FL_FLD_ACTIVATION_MODE      << MSCLP_MODE_SW_SEL_CDAC_FL_ACTIVATION_MODE_Pos))

#define CY_CAPSENSE_ISX_RM_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE2_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_ISX_RM_SW_SEL_COMP \
((CY_CAPSENSE_SM_REG_MODE2_SW_SEL_COMP_FLD_CPCS1                   << MSCLP_MODE_SW_SEL_COMP_CPCS1_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_COMP_FLD_CPCS3                   << MSCLP_MODE_SW_SEL_COMP_CPCS3_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_COMP_FLD_CPMA                    << MSCLP_MODE_SW_SEL_COMP_CPMA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_COMP_FLD_CPCA                    << MSCLP_MODE_SW_SEL_COMP_CPCA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_COMP_FLD_CPCB                    << MSCLP_MODE_SW_SEL_COMP_CPCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_COMP_FLD_CMCB                    << MSCLP_MODE_SW_SEL_COMP_CMCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_COMP_FLD_CPF                     << MSCLP_MODE_SW_SEL_COMP_CPF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_COMP_FLD_CMCS2                   << MSCLP_MODE_SW_SEL_COMP_CMCS2_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_COMP_FLD_CMCS4                   << MSCLP_MODE_SW_SEL_COMP_CMCS4_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_COMP_FLD_CMV                     << MSCLP_MODE_SW_SEL_COMP_CMV_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_COMP_FLD_CMG                     << MSCLP_MODE_SW_SEL_COMP_CMG_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_COMP_FLD_CMF                     << MSCLP_MODE_SW_SEL_COMP_CMF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_COMP_FLD_HALF_WAVE_EN            << MSCLP_MODE_SW_SEL_COMP_HALF_WAVE_EN_Pos))

#define CY_CAPSENSE_ISX_RM_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE2_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))

#define CY_CAPSENSE_ISX_RM_SW_SEL_CMOD1 \
((CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD1_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD1_FLD_SW_C1CA                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CA_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD1_FLD_SW_C1CC                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CC_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD1_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD1_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD1_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD1_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD1_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD1_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD1_DDRV_EN_Pos))

#define CY_CAPSENSE_ISX_RM_SW_SEL_CMOD2 \
((CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD2_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD2_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD2_FLD_SW_C2CB                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CB_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD2_FLD_SW_C2CD                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CD_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD2_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD2_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD2_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD2_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE2_SW_SEL_CMOD2_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD2_DDRV_EN_Pos))

/****************** CSD RM with CapDAC dithering register values *********************/

#define CY_CAPSENSE_CSD_RM_DITHER_SENSE_DUTY_CTL \
((CY_CAPSENSE_SM_REG_MODE3_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE3_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE3_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH2_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH2_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE3_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH3_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH3_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE3_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH0_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH0_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE3_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH1_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH1_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE3_SENSE_DUTY_CTL_FLD_PH_GAP_2CYCLE_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PH_GAP_2CYCLE_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE3_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE3_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE3_SENSE_DUTY_CTL_FLD_PHX_GAP_2CYCLE_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHX_GAP_2CYCLE_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE3_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_EN       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_SHIFT_EN_Pos)        | \
 (CY_CAPSENSE_SM_REG_MODE3_SENSE_DUTY_CTL_FLD_PHASE_MODE_SEL       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_MODE_SEL_Pos))

#define CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_CDAC_FL \
((CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CDAC_FL_FLD_SW_FLTCA             << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTCA_Pos)              | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CDAC_FL_FLD_SW_FLCB              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLCB_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CDAC_FL_FLD_SW_FLTV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CDAC_FL_FLD_SW_FLTG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CDAC_FL_FLD_SW_FLBV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CDAC_FL_FLD_SW_FLBG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CDAC_FL_FLD_ACTIVATION_MODE      << MSCLP_MODE_SW_SEL_CDAC_FL_ACTIVATION_MODE_Pos))

#if (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SHIELD_ACTIVE_EN)
#define CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE7_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE7_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE7_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))
#elif (CY_CAPSENSE_ENABLE == CY_CAPSENSE_SHIELD_PASSIVE_EN)
#define CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE9_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE9_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE9_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))
#else
#define CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE3_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE3_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))
#endif /* CY_CAPSENSE_ENABLE == CY_CAPSENSE_SHIELD_ACTIVE_EN */

#define CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_COMP \
((CY_CAPSENSE_SM_REG_MODE3_SW_SEL_COMP_FLD_CPCS1                   << MSCLP_MODE_SW_SEL_COMP_CPCS1_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_COMP_FLD_CPCS3                   << MSCLP_MODE_SW_SEL_COMP_CPCS3_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_COMP_FLD_CPMA                    << MSCLP_MODE_SW_SEL_COMP_CPMA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_COMP_FLD_CPCA                    << MSCLP_MODE_SW_SEL_COMP_CPCA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_COMP_FLD_CPCB                    << MSCLP_MODE_SW_SEL_COMP_CPCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_COMP_FLD_CMCB                    << MSCLP_MODE_SW_SEL_COMP_CMCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_COMP_FLD_CPF                     << MSCLP_MODE_SW_SEL_COMP_CPF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_COMP_FLD_CMCS2                   << MSCLP_MODE_SW_SEL_COMP_CMCS2_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_COMP_FLD_CMCS4                   << MSCLP_MODE_SW_SEL_COMP_CMCS4_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_COMP_FLD_CMV                     << MSCLP_MODE_SW_SEL_COMP_CMV_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_COMP_FLD_CMG                     << MSCLP_MODE_SW_SEL_COMP_CMG_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_COMP_FLD_CMF                     << MSCLP_MODE_SW_SEL_COMP_CMF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_COMP_FLD_HALF_WAVE_EN            << MSCLP_MODE_SW_SEL_COMP_HALF_WAVE_EN_Pos))

#define CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_CMOD1 \
((CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD1_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD1_FLD_SW_C1CA                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CA_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD1_FLD_SW_C1CC                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CC_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD1_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD1_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD1_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD1_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD1_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD1_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD1_DDRV_EN_Pos))

#define CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_CMOD2 \
((CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD2_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD2_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD2_FLD_SW_C2CB                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CB_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD2_FLD_SW_C2CD                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CD_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD2_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD2_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD2_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD2_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE3_SW_SEL_CMOD2_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD2_DDRV_EN_Pos))

/****************** CSX RM with CapDAC dithering register values *********************/

#define CY_CAPSENSE_CSX_RM_DITHER_SENSE_DUTY_CTL \
((CY_CAPSENSE_SM_REG_MODE4_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE4_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE4_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH2_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH2_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE4_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH3_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH3_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE4_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH0_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH0_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE4_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH1_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH1_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE4_SENSE_DUTY_CTL_FLD_PH_GAP_2CYCLE_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PH_GAP_2CYCLE_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE4_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE4_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE4_SENSE_DUTY_CTL_FLD_PHX_GAP_2CYCLE_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHX_GAP_2CYCLE_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE4_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_EN       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_SHIFT_EN_Pos)        | \
 (CY_CAPSENSE_SM_REG_MODE4_SENSE_DUTY_CTL_FLD_PHASE_MODE_SEL       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_MODE_SEL_Pos))

#define CY_CAPSENSE_CSX_RM_DITHER_SW_SEL_CDAC_FL \
((CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CDAC_FL_FLD_SW_FLTCA             << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTCA_Pos)              | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CDAC_FL_FLD_SW_FLCB              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLCB_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CDAC_FL_FLD_SW_FLTV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CDAC_FL_FLD_SW_FLTG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CDAC_FL_FLD_SW_FLBV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CDAC_FL_FLD_SW_FLBG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CDAC_FL_FLD_ACTIVATION_MODE      << MSCLP_MODE_SW_SEL_CDAC_FL_ACTIVATION_MODE_Pos))

#define CY_CAPSENSE_CSX_RM_DITHER_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE4_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_CSX_RM_DITHER_SW_SEL_COMP \
((CY_CAPSENSE_SM_REG_MODE4_SW_SEL_COMP_FLD_CPCS1                   << MSCLP_MODE_SW_SEL_COMP_CPCS1_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_COMP_FLD_CPCS3                   << MSCLP_MODE_SW_SEL_COMP_CPCS3_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_COMP_FLD_CPMA                    << MSCLP_MODE_SW_SEL_COMP_CPMA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_COMP_FLD_CPCA                    << MSCLP_MODE_SW_SEL_COMP_CPCA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_COMP_FLD_CPCB                    << MSCLP_MODE_SW_SEL_COMP_CPCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_COMP_FLD_CMCB                    << MSCLP_MODE_SW_SEL_COMP_CMCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_COMP_FLD_CPF                     << MSCLP_MODE_SW_SEL_COMP_CPF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_COMP_FLD_CMCS2                   << MSCLP_MODE_SW_SEL_COMP_CMCS2_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_COMP_FLD_CMCS4                   << MSCLP_MODE_SW_SEL_COMP_CMCS4_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_COMP_FLD_CMV                     << MSCLP_MODE_SW_SEL_COMP_CMV_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_COMP_FLD_CMG                     << MSCLP_MODE_SW_SEL_COMP_CMG_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_COMP_FLD_CMF                     << MSCLP_MODE_SW_SEL_COMP_CMF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_COMP_FLD_HALF_WAVE_EN            << MSCLP_MODE_SW_SEL_COMP_HALF_WAVE_EN_Pos))

#define CY_CAPSENSE_CSX_RM_DITHER_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE4_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))

#define CY_CAPSENSE_CSX_RM_DITHER_SW_SEL_CMOD1 \
((CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD1_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD1_FLD_SW_C1CA                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CA_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD1_FLD_SW_C1CC                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CC_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD1_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD1_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD1_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD1_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD1_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD1_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD1_DDRV_EN_Pos))

#define CY_CAPSENSE_CSX_RM_DITHER_SW_SEL_CMOD2 \
((CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD2_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD2_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD2_FLD_SW_C2CB                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CB_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD2_FLD_SW_C2CD                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CD_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD2_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD2_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD2_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD2_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE4_SW_SEL_CMOD2_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD2_DDRV_EN_Pos))

/****************** ISX RM with CapDAC dithering register values (external VDDA/2) */

#define CY_CAPSENSE_ISX_RM_DITHER_SENSE_DUTY_CTL \
((CY_CAPSENSE_SM_REG_MODE5_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE5_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE5_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH2_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH2_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE5_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH3_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH3_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE5_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH0_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH0_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE5_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH1_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH1_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE5_SENSE_DUTY_CTL_FLD_PH_GAP_2CYCLE_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PH_GAP_2CYCLE_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE5_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE5_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE5_SENSE_DUTY_CTL_FLD_PHX_GAP_2CYCLE_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHX_GAP_2CYCLE_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE5_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_EN       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_SHIFT_EN_Pos)        | \
 (CY_CAPSENSE_SM_REG_MODE5_SENSE_DUTY_CTL_FLD_PHASE_MODE_SEL       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_MODE_SEL_Pos))

#define CY_CAPSENSE_ISX_RM_DITHER_SW_SEL_CDAC_FL \
((CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CDAC_FL_FLD_SW_FLTCA             << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTCA_Pos)              | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CDAC_FL_FLD_SW_FLCB              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLCB_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CDAC_FL_FLD_SW_FLTV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CDAC_FL_FLD_SW_FLTG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CDAC_FL_FLD_SW_FLBV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CDAC_FL_FLD_SW_FLBG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CDAC_FL_FLD_ACTIVATION_MODE      << MSCLP_MODE_SW_SEL_CDAC_FL_ACTIVATION_MODE_Pos))

#define CY_CAPSENSE_ISX_RM_DITHER_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE5_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_ISX_RM_DITHER_SW_SEL_COMP \
((CY_CAPSENSE_SM_REG_MODE5_SW_SEL_COMP_FLD_CPCS1                   << MSCLP_MODE_SW_SEL_COMP_CPCS1_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_COMP_FLD_CPCS3                   << MSCLP_MODE_SW_SEL_COMP_CPCS3_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_COMP_FLD_CPMA                    << MSCLP_MODE_SW_SEL_COMP_CPMA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_COMP_FLD_CPCA                    << MSCLP_MODE_SW_SEL_COMP_CPCA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_COMP_FLD_CPCB                    << MSCLP_MODE_SW_SEL_COMP_CPCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_COMP_FLD_CMCB                    << MSCLP_MODE_SW_SEL_COMP_CMCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_COMP_FLD_CPF                     << MSCLP_MODE_SW_SEL_COMP_CPF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_COMP_FLD_CMCS2                   << MSCLP_MODE_SW_SEL_COMP_CMCS2_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_COMP_FLD_CMCS4                   << MSCLP_MODE_SW_SEL_COMP_CMCS4_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_COMP_FLD_CMV                     << MSCLP_MODE_SW_SEL_COMP_CMV_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_COMP_FLD_CMG                     << MSCLP_MODE_SW_SEL_COMP_CMG_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_COMP_FLD_CMF                     << MSCLP_MODE_SW_SEL_COMP_CMF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_COMP_FLD_HALF_WAVE_EN            << MSCLP_MODE_SW_SEL_COMP_HALF_WAVE_EN_Pos))

#define CY_CAPSENSE_ISX_RM_DITHER_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE5_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))

#define CY_CAPSENSE_ISX_RM_DITHER_SW_SEL_CMOD1 \
((CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD1_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD1_FLD_SW_C1CA                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CA_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD1_FLD_SW_C1CC                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CC_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD1_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD1_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD1_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD1_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD1_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD1_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD1_DDRV_EN_Pos))

#define CY_CAPSENSE_ISX_RM_DITHER_SW_SEL_CMOD2 \
((CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD2_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD2_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD2_FLD_SW_C2CB                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CB_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD2_FLD_SW_C2CD                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CD_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD2_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD2_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD2_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD2_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE5_SW_SEL_CMOD2_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD2_DDRV_EN_Pos))

/************************* MPSC RM register values *****************************/

#define CY_CAPSENSE_MPSC_RM_SENSE_DUTY_CTL \
((CY_CAPSENSE_SM_REG_MODE10_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE10_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE10_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH2_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH2_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE10_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH3_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH3_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE10_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH0_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH0_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE10_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH1_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH1_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE10_SENSE_DUTY_CTL_FLD_PH_GAP_2CYCLE_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PH_GAP_2CYCLE_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE10_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE10_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE10_SENSE_DUTY_CTL_FLD_PHX_GAP_2CYCLE_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHX_GAP_2CYCLE_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE10_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_EN       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_SHIFT_EN_Pos)        | \
 (CY_CAPSENSE_SM_REG_MODE10_SENSE_DUTY_CTL_FLD_PHASE_MODE_SEL       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_MODE_SEL_Pos))

#define CY_CAPSENSE_MPSC_RM_SW_SEL_CDAC_FL \
((CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CDAC_FL_FLD_SW_FLTCA             << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTCA_Pos)              | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CDAC_FL_FLD_SW_FLCB              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLCB_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CDAC_FL_FLD_SW_FLTV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CDAC_FL_FLD_SW_FLTG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CDAC_FL_FLD_SW_FLBV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CDAC_FL_FLD_SW_FLBG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CDAC_FL_FLD_ACTIVATION_MODE      << MSCLP_MODE_SW_SEL_CDAC_FL_ACTIVATION_MODE_Pos))

#define CY_CAPSENSE_MPSC_RM_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE10_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_MPSC_RM_SW_SEL_COMP \
((CY_CAPSENSE_SM_REG_MODE10_SW_SEL_COMP_FLD_CPCS1                   << MSCLP_MODE_SW_SEL_COMP_CPCS1_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_COMP_FLD_CPCS3                   << MSCLP_MODE_SW_SEL_COMP_CPCS3_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_COMP_FLD_CPMA                    << MSCLP_MODE_SW_SEL_COMP_CPMA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_COMP_FLD_CPCA                    << MSCLP_MODE_SW_SEL_COMP_CPCA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_COMP_FLD_CPCB                    << MSCLP_MODE_SW_SEL_COMP_CPCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_COMP_FLD_CMCB                    << MSCLP_MODE_SW_SEL_COMP_CMCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_COMP_FLD_CPF                     << MSCLP_MODE_SW_SEL_COMP_CPF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_COMP_FLD_CMCS2                   << MSCLP_MODE_SW_SEL_COMP_CMCS2_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_COMP_FLD_CMCS4                   << MSCLP_MODE_SW_SEL_COMP_CMCS4_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_COMP_FLD_CMV                     << MSCLP_MODE_SW_SEL_COMP_CMV_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_COMP_FLD_CMG                     << MSCLP_MODE_SW_SEL_COMP_CMG_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_COMP_FLD_CMF                     << MSCLP_MODE_SW_SEL_COMP_CMF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_COMP_FLD_HALF_WAVE_EN            << MSCLP_MODE_SW_SEL_COMP_HALF_WAVE_EN_Pos))

#define CY_CAPSENSE_MPSC_RM_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE10_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))

#define CY_CAPSENSE_MPSC_RM_SW_SEL_CMOD1 \
((CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD1_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD1_FLD_SW_C1CA                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CA_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD1_FLD_SW_C1CC                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CC_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD1_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD1_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD1_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD1_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD1_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD1_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD1_DDRV_EN_Pos))

#define CY_CAPSENSE_MPSC_RM_SW_SEL_CMOD2 \
((CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD2_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD2_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD2_FLD_SW_C2CB                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CB_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD2_FLD_SW_C2CD                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CD_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD2_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD2_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD2_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD2_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE10_SW_SEL_CMOD2_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD2_DDRV_EN_Pos))

/************************* MPSC RM  with CapDAC dithering register values *****************************/

#define CY_CAPSENSE_MPSC_RM_DITHER_SENSE_DUTY_CTL \
((CY_CAPSENSE_SM_REG_MODE11_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE11_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE11_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH2_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH2_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE11_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH3_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH3_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE11_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH0_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH0_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE11_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH1_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH1_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE11_SENSE_DUTY_CTL_FLD_PH_GAP_2CYCLE_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PH_GAP_2CYCLE_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE11_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE11_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE11_SENSE_DUTY_CTL_FLD_PHX_GAP_2CYCLE_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHX_GAP_2CYCLE_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE11_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_EN       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_SHIFT_EN_Pos)        | \
 (CY_CAPSENSE_SM_REG_MODE11_SENSE_DUTY_CTL_FLD_PHASE_MODE_SEL       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_MODE_SEL_Pos))

#define CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_CDAC_FL \
((CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CDAC_FL_FLD_SW_FLTCA             << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTCA_Pos)              | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CDAC_FL_FLD_SW_FLCB              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLCB_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CDAC_FL_FLD_SW_FLTV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CDAC_FL_FLD_SW_FLTG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CDAC_FL_FLD_SW_FLBV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CDAC_FL_FLD_SW_FLBG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CDAC_FL_FLD_ACTIVATION_MODE      << MSCLP_MODE_SW_SEL_CDAC_FL_ACTIVATION_MODE_Pos))

#define CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE11_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_COMP \
((CY_CAPSENSE_SM_REG_MODE11_SW_SEL_COMP_FLD_CPCS1                   << MSCLP_MODE_SW_SEL_COMP_CPCS1_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_COMP_FLD_CPCS3                   << MSCLP_MODE_SW_SEL_COMP_CPCS3_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_COMP_FLD_CPMA                    << MSCLP_MODE_SW_SEL_COMP_CPMA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_COMP_FLD_CPCA                    << MSCLP_MODE_SW_SEL_COMP_CPCA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_COMP_FLD_CPCB                    << MSCLP_MODE_SW_SEL_COMP_CPCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_COMP_FLD_CMCB                    << MSCLP_MODE_SW_SEL_COMP_CMCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_COMP_FLD_CPF                     << MSCLP_MODE_SW_SEL_COMP_CPF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_COMP_FLD_CMCS2                   << MSCLP_MODE_SW_SEL_COMP_CMCS2_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_COMP_FLD_CMCS4                   << MSCLP_MODE_SW_SEL_COMP_CMCS4_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_COMP_FLD_CMV                     << MSCLP_MODE_SW_SEL_COMP_CMV_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_COMP_FLD_CMG                     << MSCLP_MODE_SW_SEL_COMP_CMG_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_COMP_FLD_CMF                     << MSCLP_MODE_SW_SEL_COMP_CMF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_COMP_FLD_HALF_WAVE_EN            << MSCLP_MODE_SW_SEL_COMP_HALF_WAVE_EN_Pos))

#define CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE11_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))

#define CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_CMOD1 \
((CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD1_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD1_FLD_SW_C1CA                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CA_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD1_FLD_SW_C1CC                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CC_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD1_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD1_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD1_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD1_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD1_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD1_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD1_DDRV_EN_Pos))

#define CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_CMOD2 \
((CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD2_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD2_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD2_FLD_SW_C2CB                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CB_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD2_FLD_SW_C2CD                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CD_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD2_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD2_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD2_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD2_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE11_SW_SEL_CMOD2_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD2_DDRV_EN_Pos))

/****************** ISX RM register values (internal VDDA/2) ******************/

#define CY_CAPSENSE_ISX_RM_INTERNAL_SENSE_DUTY_CTL \
((CY_CAPSENSE_SM_REG_MODE13_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE13_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE13_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH2_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH2_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE13_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH3_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH3_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE13_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH0_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH0_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE13_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH1_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH1_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE13_SENSE_DUTY_CTL_FLD_PH_GAP_2CYCLE_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PH_GAP_2CYCLE_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE13_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE13_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE13_SENSE_DUTY_CTL_FLD_PHX_GAP_2CYCLE_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHX_GAP_2CYCLE_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE13_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_EN       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_SHIFT_EN_Pos)        | \
 (CY_CAPSENSE_SM_REG_MODE13_SENSE_DUTY_CTL_FLD_PHASE_MODE_SEL       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_MODE_SEL_Pos))

#define CY_CAPSENSE_ISX_RM_INTERNAL_SW_SEL_CDAC_FL \
((CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CDAC_FL_FLD_SW_FLTCA             << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTCA_Pos)              | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CDAC_FL_FLD_SW_FLCB              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLCB_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CDAC_FL_FLD_SW_FLTV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CDAC_FL_FLD_SW_FLTG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CDAC_FL_FLD_SW_FLBV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CDAC_FL_FLD_SW_FLBG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CDAC_FL_FLD_ACTIVATION_MODE      << MSCLP_MODE_SW_SEL_CDAC_FL_ACTIVATION_MODE_Pos))

#define CY_CAPSENSE_ISX_RM_INTERNAL_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE13_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_ISX_RM_INTERNAL_SW_SEL_COMP \
((CY_CAPSENSE_SM_REG_MODE13_SW_SEL_COMP_FLD_CPCS1                   << MSCLP_MODE_SW_SEL_COMP_CPCS1_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_COMP_FLD_CPCS3                   << MSCLP_MODE_SW_SEL_COMP_CPCS3_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_COMP_FLD_CPMA                    << MSCLP_MODE_SW_SEL_COMP_CPMA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_COMP_FLD_CPCA                    << MSCLP_MODE_SW_SEL_COMP_CPCA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_COMP_FLD_CPCB                    << MSCLP_MODE_SW_SEL_COMP_CPCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_COMP_FLD_CMCB                    << MSCLP_MODE_SW_SEL_COMP_CMCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_COMP_FLD_CPF                     << MSCLP_MODE_SW_SEL_COMP_CPF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_COMP_FLD_CMCS2                   << MSCLP_MODE_SW_SEL_COMP_CMCS2_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_COMP_FLD_CMCS4                   << MSCLP_MODE_SW_SEL_COMP_CMCS4_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_COMP_FLD_CMV                     << MSCLP_MODE_SW_SEL_COMP_CMV_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_COMP_FLD_CMG                     << MSCLP_MODE_SW_SEL_COMP_CMG_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_COMP_FLD_CMF                     << MSCLP_MODE_SW_SEL_COMP_CMF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_COMP_FLD_HALF_WAVE_EN            << MSCLP_MODE_SW_SEL_COMP_HALF_WAVE_EN_Pos))

#define CY_CAPSENSE_ISX_RM_INTERNAL_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE13_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))

#define CY_CAPSENSE_ISX_RM_INTERNAL_SW_SEL_CMOD1 \
((CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD1_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD1_FLD_SW_C1CA                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CA_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD1_FLD_SW_C1CC                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CC_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD1_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD1_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD1_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD1_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD1_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD1_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD1_DDRV_EN_Pos))

#define CY_CAPSENSE_ISX_RM_INTERNAL_SW_SEL_CMOD2 \
((CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD2_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD2_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD2_FLD_SW_C2CB                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CB_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD2_FLD_SW_C2CD                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CD_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD2_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD2_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD2_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD2_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE13_SW_SEL_CMOD2_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD2_DDRV_EN_Pos))

/****************** ISX RM with CapDAC dithering register values (internal VDDA/2) */

#define CY_CAPSENSE_ISX_RM_DITHER_INTERNAL_SENSE_DUTY_CTL \
((CY_CAPSENSE_SM_REG_MODE14_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE14_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE14_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH2_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH2_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE14_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH3_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH3_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE14_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH0_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH0_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE14_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH1_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH1_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE14_SENSE_DUTY_CTL_FLD_PH_GAP_2CYCLE_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PH_GAP_2CYCLE_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE14_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE14_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE14_SENSE_DUTY_CTL_FLD_PHX_GAP_2CYCLE_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHX_GAP_2CYCLE_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE14_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_EN       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_SHIFT_EN_Pos)        | \
 (CY_CAPSENSE_SM_REG_MODE14_SENSE_DUTY_CTL_FLD_PHASE_MODE_SEL       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_MODE_SEL_Pos))

#define CY_CAPSENSE_ISX_RM_DITHER_INTERNAL_SW_SEL_CDAC_FL \
((CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CDAC_FL_FLD_SW_FLTCA             << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTCA_Pos)              | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CDAC_FL_FLD_SW_FLCB              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLCB_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CDAC_FL_FLD_SW_FLTV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CDAC_FL_FLD_SW_FLTG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CDAC_FL_FLD_SW_FLBV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CDAC_FL_FLD_SW_FLBG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CDAC_FL_FLD_ACTIVATION_MODE      << MSCLP_MODE_SW_SEL_CDAC_FL_ACTIVATION_MODE_Pos))

#define CY_CAPSENSE_ISX_RM_DITHER_INTERNAL_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE14_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_ISX_RM_DITHER_INTERNAL_SW_SEL_COMP \
((CY_CAPSENSE_SM_REG_MODE14_SW_SEL_COMP_FLD_CPCS1                   << MSCLP_MODE_SW_SEL_COMP_CPCS1_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_COMP_FLD_CPCS3                   << MSCLP_MODE_SW_SEL_COMP_CPCS3_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_COMP_FLD_CPMA                    << MSCLP_MODE_SW_SEL_COMP_CPMA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_COMP_FLD_CPCA                    << MSCLP_MODE_SW_SEL_COMP_CPCA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_COMP_FLD_CPCB                    << MSCLP_MODE_SW_SEL_COMP_CPCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_COMP_FLD_CMCB                    << MSCLP_MODE_SW_SEL_COMP_CMCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_COMP_FLD_CPF                     << MSCLP_MODE_SW_SEL_COMP_CPF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_COMP_FLD_CMCS2                   << MSCLP_MODE_SW_SEL_COMP_CMCS2_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_COMP_FLD_CMCS4                   << MSCLP_MODE_SW_SEL_COMP_CMCS4_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_COMP_FLD_CMV                     << MSCLP_MODE_SW_SEL_COMP_CMV_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_COMP_FLD_CMG                     << MSCLP_MODE_SW_SEL_COMP_CMG_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_COMP_FLD_CMF                     << MSCLP_MODE_SW_SEL_COMP_CMF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_COMP_FLD_HALF_WAVE_EN            << MSCLP_MODE_SW_SEL_COMP_HALF_WAVE_EN_Pos))

#define CY_CAPSENSE_ISX_RM_DITHER_INTERNAL_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE14_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))

#define CY_CAPSENSE_ISX_RM_DITHER_INTERNAL_SW_SEL_CMOD1 \
((CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD1_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD1_FLD_SW_C1CA                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CA_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD1_FLD_SW_C1CC                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CC_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD1_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD1_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD1_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD1_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD1_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD1_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD1_DDRV_EN_Pos))

#define CY_CAPSENSE_ISX_RM_DITHER_INTERNAL_SW_SEL_CMOD2 \
((CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD2_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD2_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD2_FLD_SW_C2CB                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CB_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD2_FLD_SW_C2CD                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CD_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD2_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD2_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD2_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD2_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE14_SW_SEL_CMOD2_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD2_DDRV_EN_Pos))

/************************* WBX register values *****************************/

#define CY_CAPSENSE_WBX_SENSE_DUTY_CTL \
((CY_CAPSENSE_SM_REG_MODE15_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE15_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE15_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH2_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH2_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE15_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH3_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH3_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE15_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH0_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH0_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE15_SENSE_DUTY_CTL_FLD_PHASE_GAP_FS2_PH1_EN << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_FS2_PH1_EN_Pos)  | \
 (CY_CAPSENSE_SM_REG_MODE15_SENSE_DUTY_CTL_FLD_PH_GAP_2CYCLE_EN     << MSCLP_MODE_SENSE_DUTY_CTL_PH_GAP_2CYCLE_EN_Pos)      | \
 (CY_CAPSENSE_SM_REG_MODE15_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH0X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH0X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE15_SENSE_DUTY_CTL_FLD_PHASE_GAP_PH1X_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_GAP_PH1X_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE15_SENSE_DUTY_CTL_FLD_PHX_GAP_2CYCLE_EN    << MSCLP_MODE_SENSE_DUTY_CTL_PHX_GAP_2CYCLE_EN_Pos)     | \
 (CY_CAPSENSE_SM_REG_MODE15_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_EN       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_SHIFT_EN_Pos)        | \
 (CY_CAPSENSE_SM_REG_MODE15_SENSE_DUTY_CTL_FLD_PHASE_MODE_SEL       << MSCLP_MODE_SENSE_DUTY_CTL_PHASE_MODE_SEL_Pos))

#define CY_CAPSENSE_WBX_SW_SEL_CDAC_FL \
((CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CDAC_FL_FLD_SW_FLTCA             << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTCA_Pos)              | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CDAC_FL_FLD_SW_FLCB              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLCB_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CDAC_FL_FLD_SW_FLTV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CDAC_FL_FLD_SW_FLTG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLTG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CDAC_FL_FLD_SW_FLBV              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBV_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CDAC_FL_FLD_SW_FLBG              << MSCLP_MODE_SW_SEL_CDAC_FL_SW_FLBG_Pos)               | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CDAC_FL_FLD_ACTIVATION_MODE      << MSCLP_MODE_SW_SEL_CDAC_FL_ACTIVATION_MODE_Pos))

#define CY_CAPSENSE_WBX_SW_SEL_TOP \
((CY_CAPSENSE_SM_REG_MODE15_SW_SEL_TOP_FLD_CACB                     << MSCLP_MODE_SW_SEL_TOP_CACB_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_TOP_FLD_CACC                     << MSCLP_MODE_SW_SEL_TOP_CACC_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_TOP_FLD_CBCD                     << MSCLP_MODE_SW_SEL_TOP_CBCD_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_TOP_FLD_AYA_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYA_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_TOP_FLD_AYA_EN                   << MSCLP_MODE_SW_SEL_TOP_AYA_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_TOP_FLD_AYB_CTL                  << MSCLP_MODE_SW_SEL_TOP_AYB_CTL_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_TOP_FLD_AYB_EN                   << MSCLP_MODE_SW_SEL_TOP_AYB_EN_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_TOP_FLD_BYB                      << MSCLP_MODE_SW_SEL_TOP_BYB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_TOP_FLD_BGRF                     << MSCLP_MODE_SW_SEL_TOP_BGRF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_TOP_FLD_RMF                      << MSCLP_MODE_SW_SEL_TOP_RMF_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_TOP_FLD_MBF                      << MSCLP_MODE_SW_SEL_TOP_MBF_Pos))

#define CY_CAPSENSE_WBX_SW_SEL_COMP \
((CY_CAPSENSE_SM_REG_MODE15_SW_SEL_COMP_FLD_CPCS1                   << MSCLP_MODE_SW_SEL_COMP_CPCS1_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_COMP_FLD_CPCS3                   << MSCLP_MODE_SW_SEL_COMP_CPCS3_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_COMP_FLD_CPMA                    << MSCLP_MODE_SW_SEL_COMP_CPMA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_COMP_FLD_CPCA                    << MSCLP_MODE_SW_SEL_COMP_CPCA_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_COMP_FLD_CPCB                    << MSCLP_MODE_SW_SEL_COMP_CPCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_COMP_FLD_CMCB                    << MSCLP_MODE_SW_SEL_COMP_CMCB_Pos)                     | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_COMP_FLD_CPF                     << MSCLP_MODE_SW_SEL_COMP_CPF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_COMP_FLD_CMCS2                   << MSCLP_MODE_SW_SEL_COMP_CMCS2_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_COMP_FLD_CMCS4                   << MSCLP_MODE_SW_SEL_COMP_CMCS4_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_COMP_FLD_CMV                     << MSCLP_MODE_SW_SEL_COMP_CMV_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_COMP_FLD_CMG                     << MSCLP_MODE_SW_SEL_COMP_CMG_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_COMP_FLD_CMF                     << MSCLP_MODE_SW_SEL_COMP_CMF_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_COMP_FLD_HALF_WAVE_EN            << MSCLP_MODE_SW_SEL_COMP_HALF_WAVE_EN_Pos))

#define CY_CAPSENSE_WBX_SW_SEL_SH \
((CY_CAPSENSE_SM_REG_MODE15_SW_SEL_SH_FLD_SOMB                      << MSCLP_MODE_SW_SEL_SH_SOMB_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_SH_FLD_CBSO                      << MSCLP_MODE_SW_SEL_SH_CBSO_Pos)                       | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_SH_FLD_SPCS1                     << MSCLP_MODE_SW_SEL_SH_SPCS1_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_SH_FLD_SPCS3                     << MSCLP_MODE_SW_SEL_SH_SPCS3_Pos)                      | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_SH_FLD_FSP                       << MSCLP_MODE_SW_SEL_SH_FSP_Pos)                        | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_SH_FLD_BUF_SEL                   << MSCLP_MODE_SW_SEL_SH_BUF_SEL_Pos)                    | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_SH_FLD_BUF_EN                    << MSCLP_MODE_SW_SEL_SH_BUF_EN_Pos))

#define CY_CAPSENSE_WBX_SW_SEL_CMOD1 \
((CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD1_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD1_FLD_SW_C1CA                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CA_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD1_FLD_SW_C1CC                << MSCLP_MODE_SW_SEL_CMOD1_SW_C1CC_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD1_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD1_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD1_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD1_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD1_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD1_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD1_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD1_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD1_DDRV_EN_Pos))

#define CY_CAPSENSE_WBX_SW_SEL_CMOD2 \
((CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD2_FLD_SW_AMUXA               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXA_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD2_FLD_SW_AMUXB               << MSCLP_MODE_SW_SEL_CMOD2_SW_AMUXB_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD2_FLD_SW_C2CB                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CB_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD2_FLD_SW_C2CD                << MSCLP_MODE_SW_SEL_CMOD2_SW_C2CD_Pos)                 | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD2_FLD_SW_PU                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PU_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD2_FLD_SW_PD                  << MSCLP_MODE_SW_SEL_CMOD2_SW_PD_Pos)                   | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD2_FLD_REF_MODE               << MSCLP_MODE_SW_SEL_CMOD2_REF_MODE_Pos)                | \
 (CY_CAPSENSE_SM_REG_MODE15_SW_SEL_CMOD2_FLD_DDRV_EN                << MSCLP_MODE_SW_SEL_CMOD2_DDRV_EN_Pos))


#define CY_CAPSENSE_CSD_RM_MODE \
    { \
        .senseDutyCtl = CY_CAPSENSE_CSD_RM_SENSE_DUTY_CTL,\
        .swSelCdacFl  = CY_CAPSENSE_CSD_RM_SW_SEL_CDAC_FL,\
        .swSelTop     = CY_CAPSENSE_CSD_RM_SW_SEL_TOP,    \
        .swSelComp    = CY_CAPSENSE_CSD_RM_SW_SEL_COMP,   \
        .swSelSh      = CY_CAPSENSE_CSD_RM_SW_SEL_SH,     \
        .swSelCmod1   = CY_CAPSENSE_CSD_RM_SW_SEL_CMOD1,  \
        .swSelCmod2   = CY_CAPSENSE_CSD_RM_SW_SEL_CMOD2,  \
    }

#define CY_CAPSENSE_CSX_RM_MODE \
    { \
        .senseDutyCtl = CY_CAPSENSE_CSX_RM_SENSE_DUTY_CTL,\
        .swSelCdacFl  = CY_CAPSENSE_CSX_RM_SW_SEL_CDAC_FL,\
        .swSelTop     = CY_CAPSENSE_CSX_RM_SW_SEL_TOP,    \
        .swSelComp    = CY_CAPSENSE_CSX_RM_SW_SEL_COMP,   \
        .swSelSh      = CY_CAPSENSE_CSX_RM_SW_SEL_SH,     \
        .swSelCmod1   = CY_CAPSENSE_CSX_RM_SW_SEL_CMOD1,  \
        .swSelCmod2   = CY_CAPSENSE_CSX_RM_SW_SEL_CMOD2,  \
    }

#define CY_CAPSENSE_ISX_RM_MODE \
    { \
        .senseDutyCtl = CY_CAPSENSE_ISX_RM_SENSE_DUTY_CTL,\
        .swSelCdacFl  = CY_CAPSENSE_ISX_RM_SW_SEL_CDAC_FL,\
        .swSelTop     = CY_CAPSENSE_ISX_RM_SW_SEL_TOP,    \
        .swSelComp    = CY_CAPSENSE_ISX_RM_SW_SEL_COMP,   \
        .swSelSh      = CY_CAPSENSE_ISX_RM_SW_SEL_SH,     \
        .swSelCmod1   = CY_CAPSENSE_ISX_RM_SW_SEL_CMOD1,  \
        .swSelCmod2   = CY_CAPSENSE_ISX_RM_SW_SEL_CMOD2,  \
    }

#define CY_CAPSENSE_MPSC_RM_MODE \
    { \
        .senseDutyCtl = CY_CAPSENSE_MPSC_RM_SENSE_DUTY_CTL,\
        .swSelCdacFl  = CY_CAPSENSE_MPSC_RM_SW_SEL_CDAC_FL,\
        .swSelTop     = CY_CAPSENSE_MPSC_RM_SW_SEL_TOP,    \
        .swSelComp    = CY_CAPSENSE_MPSC_RM_SW_SEL_COMP,   \
        .swSelSh      = CY_CAPSENSE_MPSC_RM_SW_SEL_SH,     \
        .swSelCmod1   = CY_CAPSENSE_MPSC_RM_SW_SEL_CMOD1,  \
        .swSelCmod2   = CY_CAPSENSE_MPSC_RM_SW_SEL_CMOD2,  \
    }

#define CY_CAPSENSE_CSD_RM_DITHER_MODE \
    { \
        .senseDutyCtl = CY_CAPSENSE_CSD_RM_DITHER_SENSE_DUTY_CTL,\
        .swSelCdacFl  = CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_CDAC_FL,\
        .swSelTop     = CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_TOP,    \
        .swSelComp    = CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_COMP,   \
        .swSelSh      = CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_SH,     \
        .swSelCmod1   = CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_CMOD1,  \
        .swSelCmod2   = CY_CAPSENSE_CSD_RM_DITHER_SW_SEL_CMOD2,  \
    }

#define CY_CAPSENSE_CSX_RM_DITHER_MODE \
    { \
        .senseDutyCtl = CY_CAPSENSE_CSX_RM_DITHER_SENSE_DUTY_CTL,\
        .swSelCdacFl  = CY_CAPSENSE_CSX_RM_DITHER_SW_SEL_CDAC_FL,\
        .swSelTop     = CY_CAPSENSE_CSX_RM_DITHER_SW_SEL_TOP,    \
        .swSelComp    = CY_CAPSENSE_CSX_RM_DITHER_SW_SEL_COMP,   \
        .swSelSh      = CY_CAPSENSE_CSX_RM_DITHER_SW_SEL_SH,     \
        .swSelCmod1   = CY_CAPSENSE_CSX_RM_DITHER_SW_SEL_CMOD1,  \
        .swSelCmod2   = CY_CAPSENSE_CSX_RM_DITHER_SW_SEL_CMOD2,  \
    }

#define CY_CAPSENSE_ISX_RM_DITHER_MODE \
    { \
        .senseDutyCtl = CY_CAPSENSE_ISX_RM_DITHER_SENSE_DUTY_CTL,\
        .swSelCdacFl  = CY_CAPSENSE_ISX_RM_DITHER_SW_SEL_CDAC_FL,\
        .swSelTop     = CY_CAPSENSE_ISX_RM_DITHER_SW_SEL_TOP,    \
        .swSelComp    = CY_CAPSENSE_ISX_RM_DITHER_SW_SEL_COMP,   \
        .swSelSh      = CY_CAPSENSE_ISX_RM_DITHER_SW_SEL_SH,     \
        .swSelCmod1   = CY_CAPSENSE_ISX_RM_DITHER_SW_SEL_CMOD1,  \
        .swSelCmod2   = CY_CAPSENSE_ISX_RM_DITHER_SW_SEL_CMOD2,  \
    }

#define CY_CAPSENSE_MPSC_DITHER_RM_MODE \
    { \
        .senseDutyCtl = CY_CAPSENSE_MPSC_RM_DITHER_SENSE_DUTY_CTL,\
        .swSelCdacFl  = CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_CDAC_FL,\
        .swSelTop     = CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_TOP,    \
        .swSelComp    = CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_COMP,   \
        .swSelSh      = CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_SH,     \
        .swSelCmod1   = CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_CMOD1,  \
        .swSelCmod2   = CY_CAPSENSE_MPSC_RM_DITHER_SW_SEL_CMOD2,  \
    }

#define CY_CAPSENSE_WBX_RM_MODE \
    { \
        .senseDutyCtl = CY_CAPSENSE_WBX_SENSE_DUTY_CTL,\
        .swSelCdacFl  = CY_CAPSENSE_WBX_SW_SEL_CDAC_FL,\
        .swSelTop     = CY_CAPSENSE_WBX_SW_SEL_TOP,    \
        .swSelComp    = CY_CAPSENSE_WBX_SW_SEL_COMP,   \
        .swSelSh      = CY_CAPSENSE_WBX_SW_SEL_SH,     \
        .swSelCmod1   = CY_CAPSENSE_WBX_SW_SEL_CMOD1,  \
        .swSelCmod2   = CY_CAPSENSE_WBX_SW_SEL_CMOD2,  \
    }

#define CY_CAPSENSE_SM_MODES_ARR \
    {CY_CAPSENSE_CSD_RM_MODE, CY_CAPSENSE_CSX_RM_MODE, CY_CAPSENSE_ISX_RM_MODE, \
     CY_CAPSENSE_CSD_RM_DITHER_MODE, CY_CAPSENSE_CSX_RM_DITHER_MODE, CY_CAPSENSE_ISX_RM_DITHER_MODE, \
     CY_CAPSENSE_WBX_RM_MODE}


/** Initialization of sensing method template variable */

#define CY_CAPSENSE_WBX_SW_SEL_CDAC_CO_DIRECT \
((CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COTCA                    << MSCLP_SW_SEL_CDAC_CO_SW_COTCA_Pos)                   | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COCB                     << MSCLP_SW_SEL_CDAC_CO_SW_COCB_Pos)                    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COTV                     << MSCLP_SW_SEL_CDAC_CO_SW_COTV_Pos)                    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COTG                     << MSCLP_SW_SEL_CDAC_CO_SW_COTG_Pos)                    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COBG                     << MSCLP_SW_SEL_CDAC_CO_SW_COBG_Pos)                    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COBV                     << MSCLP_SW_SEL_CDAC_CO_SW_COBV_Pos))

#define CY_CAPSENSE_WBX_SW_SEL_CDAC_CO_INVERTED \
((CY_CAPSENSE_SM_MPSC_REG_SW_SEL_CDAC_CO_FLD_SW_COTCA               << MSCLP_SW_SEL_CDAC_CO_SW_COTCA_Pos)                   | \
 (CY_CAPSENSE_SM_MPSC_REG_SW_SEL_CDAC_CO_FLD_SW_COCB                << MSCLP_SW_SEL_CDAC_CO_SW_COCB_Pos)                    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COTV                     << MSCLP_SW_SEL_CDAC_CO_SW_COTV_Pos)                    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COTG                     << MSCLP_SW_SEL_CDAC_CO_SW_COTG_Pos)                    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COBG                     << MSCLP_SW_SEL_CDAC_CO_SW_COBG_Pos)                    | \
 (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COBV                     << MSCLP_SW_SEL_CDAC_CO_SW_COBV_Pos))


#define CY_CAPSENSE_SENSING_METHOD_BASE_TEMPLATE \
    { \
        .ctl = \
                    ((CY_CAPSENSE_SM_REG_CTL_FLD_SENSE_EN << MSCLP_CTL_SENSE_EN_Pos)                                                        |\
                    (CY_CAPSENSE_SM_REG_CTL_FLD_MSCCMP_EN << MSCLP_CTL_MSCCMP_EN_Pos)                                                       |\
                    (CY_CAPSENSE_SM_REG_CTL_FLD_CLK_SYNC_EN << MSCLP_CTL_CLK_SYNC_EN_Pos)                                                   |\
                    (CY_CAPSENSE_SM_REG_CTL_FLD_EXT_FRAME_START_MODE << MSCLP_CTL_EXT_FRAME_START_MODE_Pos)                                 |\
                    (CY_CAPSENSE_SM_REG_CTL_FLD_CFG_OFFSET << MSCLP_CTL_CFG_OFFSET_Pos)                                                     |\
                    (CY_CAPSENSE_SM_REG_CTL_FLD_OPERATING_MODE << MSCLP_CTL_OPERATING_MODE_Pos)                                             |\
                    (CY_CAPSENSE_SM_REG_CTL_FLD_BUF_MODE << MSCLP_CTL_BUF_MODE_Pos)                                                         |\
                    (CY_CAPSENSE_SM_REG_CTL_FLD_CLK_MSC_RATIO << MSCLP_CTL_CLK_MSC_RATIO_Pos)                                               |\
                    (CY_CAPSENSE_SM_REG_CTL_FLD_DEBUG_EN << MSCLP_CTL_DEBUG_EN_Pos)                                                         |\
                    (CY_CAPSENSE_SM_REG_CTL_FLD_ENABLED << MSCLP_CTL_ENABLED_Pos)),                                                          \
        .scanCtl1 = \
                    ((CY_CAPSENSE_SM_REG_SCAN_CTL1_FLD_NUM_AUTO_RESAMPLE << MSCLP_SCAN_CTL1_NUM_AUTO_RESAMPLE_Pos)                          |\
                    (CY_CAPSENSE_SM_REG_SCAN_CTL1_FLD_RESCAN_DEBUG_MODE << MSCLP_SCAN_CTL1_RESCAN_DEBUG_MODE_Pos)                           |\
                    (CY_CAPSENSE_SM_REG_SCAN_CTL1_FLD_NUM_SAMPLES << MSCLP_SCAN_CTL1_NUM_SAMPLES_Pos)                                       |\
                    (CY_CAPSENSE_SM_REG_SCAN_CTL1_FLD_RAW_COUNT_MODE << MSCLP_SCAN_CTL1_RAW_COUNT_MODE_Pos)                                 |\
                    (CY_CAPSENSE_SM_REG_SCAN_CTL1_FLD_DEBUG_CONV_PH_SEL << MSCLP_SCAN_CTL1_DEBUG_CONV_PH_SEL_Pos)                           |\
                    (CY_CAPSENSE_SM_REG_SCAN_CTL1_FLD_FRAME_RES_START_ADDR << MSCLP_SCAN_CTL1_FRAME_RES_START_ADDR_Pos)                     |\
                    (CY_CAPSENSE_SM_REG_SCAN_CTL1_FLD_RC_STORE_EN << MSCLP_SCAN_CTL1_RC_STORE_EN_Pos)                                       |\
                    (CY_CAPSENSE_SM_REG_SCAN_CTL1_FLD_RC_STORE_MODE << MSCLP_SCAN_CTL1_RC_STORE_MODE_Pos)),                                  \
        .scanCtl2 = \
                    ((CY_CAPSENSE_SM_REG_SCAN_CTL2_FLD_NUM_EPI_KREF_DELAY_PRS << MSCLP_SCAN_CTL2_NUM_EPI_KREF_DELAY_PRS_Pos)                |\
                    (CY_CAPSENSE_SM_REG_SCAN_CTL2_FLD_NUM_EPI_KREF_DELAY << MSCLP_SCAN_CTL2_NUM_EPI_KREF_DELAY_Pos)                         |\
                    (CY_CAPSENSE_SM_REG_SCAN_CTL2_FLD_CHOP_POL << MSCLP_SCAN_CTL2_CHOP_POL_Pos)                                             |\
                    (CY_CAPSENSE_SM_REG_SCAN_CTL2_FLD_FRAME_CFG_START_ADDR << MSCLP_SCAN_CTL2_FRAME_CFG_START_ADDR_Pos)                     |\
                    (CY_CAPSENSE_SM_REG_SCAN_CTL2_FLD_EXT_REF_CLK_EN << MSCLP_SCAN_CTL2_EXT_REF_CLK_EN_Pos)                                 |\
                    (CY_CAPSENSE_SM_REG_SCAN_CTL2_FLD_INFINITE_SCAN_MODE << MSCLP_SCAN_CTL2_INFINITE_SCAN_MODE_Pos)),                        \
        .initCtl1 = \
                    ((CY_CAPSENSE_SM_REG_INIT_CTL1_FLD_NUM_INIT_CMOD_12_RAIL_CYCLES << MSCLP_INIT_CTL1_NUM_INIT_CMOD_12_RAIL_CYCLES_Pos)    |\
                    (CY_CAPSENSE_SM_REG_INIT_CTL1_FLD_NUM_INIT_CMOD_12_SHORT_CYCLES << MSCLP_INIT_CTL1_NUM_INIT_CMOD_12_SHORT_CYCLES_Pos)   |\
                    (CY_CAPSENSE_SM_REG_INIT_CTL1_FLD_PER_SAMPLE << MSCLP_INIT_CTL1_PER_SAMPLE_Pos)),                                        \
        .initCtl2 = \
                    (0u),                                                                                                                    \
        .initCtl3 = \
                    ((CY_CAPSENSE_SM_REG_INIT_CTL3_FLD_NUM_PRO_OFFSET_CYCLES << MSCLP_INIT_CTL3_NUM_PRO_OFFSET_CYCLES_Pos)                  |\
                    (CY_CAPSENSE_SM_REG_INIT_CTL3_FLD_NUM_PRO_OFFSET_TRIPS << MSCLP_INIT_CTL3_NUM_PRO_OFFSET_TRIPS_Pos)                     |\
                    (CY_CAPSENSE_SM_REG_INIT_CTL3_FLD_CMOD_SEL << MSCLP_INIT_CTL3_CMOD_SEL_Pos)                                             |\
                    (CY_CAPSENSE_SM_REG_INIT_CTL3_FLD_INIT_MODE << MSCLP_INIT_CTL3_INIT_MODE_Pos)),                                          \
        .initCtl4 = \
                    ((CY_CAPSENSE_SM_REG_INIT_CTL4_FLD_NUM_PRO_DUMMY_SUB_CONVS << MSCLP_INIT_CTL4_NUM_PRO_DUMMY_SUB_CONVS_Pos)              |\
                    (CY_CAPSENSE_SM_REG_INIT_CTL4_FLD_NUM_PRO_WAIT_KREF_DELAY_PRS << MSCLP_INIT_CTL4_NUM_PRO_WAIT_KREF_DELAY_PRS_Pos)       |\
                    (CY_CAPSENSE_SM_REG_INIT_CTL4_FLD_NUM_PRO_WAIT_KREF_DELAY << MSCLP_INIT_CTL4_NUM_PRO_WAIT_KREF_DELAY_Pos)               |\
                    (CY_CAPSENSE_SM_REG_INIT_CTL4_FLD_PRO_BYPASS << MSCLP_INIT_CTL4_PRO_BYPASS_Pos)),                                        \
        .senseDutyCtl = \
                    ((CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_WIDTH << MSCLP_SENSE_DUTY_CTL_PHASE_WIDTH_Pos)                            |\
                    (CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_SHIFT_CYCLES << MSCLP_SENSE_DUTY_CTL_PHASE_SHIFT_CYCLES_Pos)               |\
                    (CY_CAPSENSE_SM_REG_SENSE_DUTY_CTL_FLD_PHASE_WIDTH_SEL << MSCLP_SENSE_DUTY_CTL_PHASE_WIDTH_SEL_Pos)),                    \
        .sensePeriodCtl = \
                    ((CY_CAPSENSE_SM_REG_SENSE_PERIOD_CTL_FLD_LFSR_POLY << MSCLP_SENSE_PERIOD_CTL_LFSR_POLY_Pos)                            |\
                    (CY_CAPSENSE_SM_REG_SENSE_PERIOD_CTL_FLD_LFSR_SCALE << MSCLP_SENSE_PERIOD_CTL_LFSR_SCALE_Pos)),                          \
        .filterCtl = \
                    ((CY_CAPSENSE_SM_REG_FILTER_CTL_FLD_BIT_FORMAT << MSCLP_FILTER_CTL_BIT_FORMAT_Pos)                                      |\
                    (CY_CAPSENSE_SM_REG_FILTER_CTL_FLD_FILTER_MODE << MSCLP_FILTER_CTL_FILTER_MODE_Pos)),                                    \
        .ccompCdacCtl = \
                    ((CY_CAPSENSE_SM_REG_CCOMP_CDAC_CTL_FLD_SEL_CO_PRO_OFFSET << MSCLP_CCOMP_CDAC_CTL_SEL_CO_PRO_OFFSET_Pos)                |\
                    (CY_CAPSENSE_SM_REG_CCOMP_CDAC_CTL_FLD_COMP_BLANKING_MODE << MSCLP_CCOMP_CDAC_CTL_COMP_BLANKING_MODE_Pos)               |\
                    (CY_CAPSENSE_SM_REG_CCOMP_CDAC_CTL_FLD_EPILOGUE_EN << MSCLP_CCOMP_CDAC_CTL_EPILOGUE_EN_Pos)),                            \
        .ditherCdacCtl = \
                    ((CY_CAPSENSE_SM_REG_DITHER_CDAC_CTL_FLD_SEL_FL << MSCLP_DITHER_CDAC_CTL_SEL_FL_Pos)                                    |\
                    (CY_CAPSENSE_SM_REG_DITHER_CDAC_CTL_FLD_LFSR_POLY_FL << MSCLP_DITHER_CDAC_CTL_LFSR_POLY_FL_Pos)),                        \
        .mscCmpCtl = \
                    ((CY_CAPSENSE_SM_REG_MSCCMP_CTL_FLD_PWR << MSCLP_MSCCMP_CTL_PWR_Pos)                                                    |\
                    (CY_CAPSENSE_SM_REG_MSCCMP_CTL_FLD_FILT << MSCLP_MSCCMP_CTL_FILT_Pos)),                                                  \
        .obsCtl = \
                    (0u),                                                                                                                    \
        .aosCtl = \
                    ((CY_CAPSENSE_SM_REG_AOS_CTL_FLD_WAKEUP_TIMER << MSCLP_AOS_CTL_WAKEUP_TIMER_Pos)                                        |\
                     (CY_CAPSENSE_SM_REG_AOS_CTL_FLD_FR_TIMEOUT_INTERVAL << MSCLP_AOS_CTL_FR_TIMEOUT_INTERVAL_Pos)                          |\
                     (CY_CAPSENSE_SM_REG_AOS_CTL_FLD_STOP_ON_SD << MSCLP_AOS_CTL_STOP_ON_SD_Pos)                                            |\
                     (CY_CAPSENSE_SM_REG_AOS_CTL_FLD_MRSS_PWR_CYCLE_EN << MSCLP_AOS_CTL_MRSS_PWR_CYCLE_EN_Pos)),                             \
        .ceCtl = \
                    ((CY_CAPSENSE_SM_REG_CE_CTL_FLD_RCF_EN << MSCLP_CE_CTL_RCF_EN_Pos)                                                      |\
                     (CY_CAPSENSE_SM_REG_CE_CTL_FLD_BLSD_EN << MSCLP_CE_CTL_BLSD_EN_Pos)                                                    |\
                     (CY_CAPSENSE_SM_REG_CE_CTL_FLD_CE_TEST_MODE << MSCLP_CE_CTL_CE_TEST_MODE_Pos)                                          |\
                     (CY_CAPSENSE_SM_REG_CE_CTL_FLD_ENABLED << MSCLP_CE_CTL_ENABLED_Pos)),                                                   \
        .pumpCtl = \
                    (CY_CAPSENSE_SM_REG_PUMP_CTL_FLD_PUMP_MODE << MSCLP_PUMP_CTL_PUMP_MODE_Pos),                                             \
        .intr = \
                    ((CY_CAPSENSE_SM_REG_INTR_FLD_SUB_SAMPLE << MSCLP_INTR_SUB_SAMPLE_Pos)                                                  |\
                     (CY_CAPSENSE_SM_REG_INTR_FLD_SAMPLE << MSCLP_INTR_SAMPLE_Pos)                                                          |\
                     (CY_CAPSENSE_SM_REG_INTR_FLD_SCAN << MSCLP_INTR_SCAN_Pos)                                                              |\
                     (CY_CAPSENSE_SM_REG_INTR_FLD_INIT << MSCLP_INTR_INIT_Pos)                                                              |\
                     (CY_CAPSENSE_SM_REG_INTR_FLD_FRAME << MSCLP_INTR_FRAME_Pos)                                                            |\
                     (CY_CAPSENSE_SM_REG_INTR_FLD_CONFIG_REQ << MSCLP_INTR_CONFIG_REQ_Pos)                                                  |\
                     (CY_CAPSENSE_SM_REG_INTR_FLD_FIFO_UNDERFLOW << MSCLP_INTR_FIFO_UNDERFLOW_Pos)                                          |\
                     (CY_CAPSENSE_SM_REG_INTR_FLD_FIFO_OVERFLOW << MSCLP_INTR_FIFO_OVERFLOW_Pos)),                                           \
        .intrSet = \
                    ((CY_CAPSENSE_SM_REG_INTR_SET_FLD_SUB_SAMPLE << MSCLP_INTR_SET_SUB_SAMPLE_Pos)                                          |\
                     (CY_CAPSENSE_SM_REG_INTR_SET_FLD_SAMPLE << MSCLP_INTR_SET_SAMPLE_Pos)                                                  |\
                     (CY_CAPSENSE_SM_REG_INTR_SET_FLD_SCAN << MSCLP_INTR_SET_SCAN_Pos)                                                      |\
                     (CY_CAPSENSE_SM_REG_INTR_SET_FLD_INIT << MSCLP_INTR_SET_INIT_Pos)                                                      |\
                     (CY_CAPSENSE_SM_REG_INTR_SET_FLD_FRAME << MSCLP_INTR_SET_FRAME_Pos)                                                    |\
                     (CY_CAPSENSE_SM_REG_INTR_SET_FLD_CONFIG_REQ << MSCLP_INTR_SET_CONFIG_REQ_Pos)                                          |\
                     (CY_CAPSENSE_SM_REG_INTR_SET_FLD_FIFO_UNDERFLOW << MSCLP_INTR_SET_FIFO_UNDERFLOW_Pos)                                  |\
                     (CY_CAPSENSE_SM_REG_INTR_SET_FLD_FIFO_OVERFLOW << MSCLP_INTR_SET_FIFO_OVERFLOW_Pos)),                                   \
        .intrMask = \
                    (0u),                                                                                                                    \
        .intrLp = \
                    ((CY_CAPSENSE_SM_REG_INTR_LP_FLD_SIG_DET << MSCLP_INTR_LP_SIG_DET_Pos)                                                  |\
                     (CY_CAPSENSE_SM_REG_INTR_LP_FLD_FR_TIMEOUT << MSCLP_INTR_LP_FR_TIMEOUT_Pos)                                            |\
                     (CY_CAPSENSE_SM_REG_INTR_LP_FLD_FRAME << MSCLP_INTR_LP_FRAME_Pos)                                                      |\
                     (CY_CAPSENSE_SM_REG_INTR_LP_FLD_CE_DONE << MSCLP_INTR_LP_CE_DONE_Pos)                                                  |\
                     (CY_CAPSENSE_SM_REG_INTR_LP_FLD_IMO_UP << MSCLP_INTR_LP_IMO_UP_Pos)),                                                   \
        .intrLpSet = \
                    ((CY_CAPSENSE_SM_REG_INTR_LP_SET_FLD_SIG_DET << MSCLP_INTR_LP_SET_SIG_DET_Pos)                                          |\
                     (CY_CAPSENSE_SM_REG_INTR_LP_SET_FLD_FR_TIMEOUT << MSCLP_INTR_LP_SET_FR_TIMEOUT_Pos)                                    |\
                     (CY_CAPSENSE_SM_REG_INTR_LP_SET_FLD_FRAME << MSCLP_INTR_LP_SET_FRAME_Pos)                                              |\
                     (CY_CAPSENSE_SM_REG_INTR_LP_SET_FLD_CE_DONE << MSCLP_INTR_LP_SET_CE_DONE_Pos)                                          |\
                     (CY_CAPSENSE_SM_REG_INTR_LP_SET_FLD_IMO_UP << MSCLP_INTR_LP_SET_IMO_UP_Pos)),                                           \
        .intrLpMask = \
                    (0u),                                                                                                                    \
        .swSelCdacRe = \
                    ((CY_CAPSENSE_SM_REG_SW_SEL_CDAC_RE_FLD_SW_RETCC << MSCLP_SW_SEL_CDAC_RE_SW_RETCC_Pos)                                  |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_RE_FLD_SW_RECD << MSCLP_SW_SEL_CDAC_RE_SW_RECD_Pos)                                    |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_RE_FLD_SW_RETV << MSCLP_SW_SEL_CDAC_RE_SW_RETV_Pos)                                    |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_RE_FLD_SW_RETG << MSCLP_SW_SEL_CDAC_RE_SW_RETG_Pos)                                    |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_RE_FLD_SW_REBV << MSCLP_SW_SEL_CDAC_RE_SW_REBV_Pos)                                    |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_RE_FLD_SW_REBG << MSCLP_SW_SEL_CDAC_RE_SW_REBG_Pos)),                                   \
        .swSelCdacCo = \
                    ((CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COTCA << MSCLP_SW_SEL_CDAC_CO_SW_COTCA_Pos)                                  |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COCB << MSCLP_SW_SEL_CDAC_CO_SW_COCB_Pos)                                    |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COTV << MSCLP_SW_SEL_CDAC_CO_SW_COTV_Pos)                                    |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COTG << MSCLP_SW_SEL_CDAC_CO_SW_COTG_Pos)                                    |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COBV << MSCLP_SW_SEL_CDAC_CO_SW_COBV_Pos)                                    |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CO_FLD_SW_COBG << MSCLP_SW_SEL_CDAC_CO_SW_COBG_Pos)),                                   \
        .swSelCdacCf = \
                    ((CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CF_FLD_SW_CFTCA << MSCLP_SW_SEL_CDAC_CF_SW_CFTCA_Pos)                                  |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CF_FLD_SW_CFTCB << MSCLP_SW_SEL_CDAC_CF_SW_CFTCB_Pos)                                  |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CF_FLD_SW_CFTV << MSCLP_SW_SEL_CDAC_CF_SW_CFTV_Pos)                                    |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CF_FLD_SW_CFTG << MSCLP_SW_SEL_CDAC_CF_SW_CFTG_Pos)                                    |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CF_FLD_SW_CFBV << MSCLP_SW_SEL_CDAC_CF_SW_CFBV_Pos)                                    |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_CDAC_CF_FLD_SW_CFBG << MSCLP_SW_SEL_CDAC_CF_SW_CFBG_Pos)),                                   \
        .swSelBgr = \
                    ((CY_CAPSENSE_SM_REG_SW_SEL_BGR_FLD_SW_BGRCM << MSCLP_SW_SEL_BGR_SW_BGRCM_Pos)                                          |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_BGR_FLD_SW_IGMA << MSCLP_SW_SEL_BGR_SW_IGMA_Pos)                                            |\
                     (CY_CAPSENSE_SM_REG_SW_SEL_BGR_FLD_SW_BGRMA << MSCLP_SW_SEL_BGR_SW_BGRMA_Pos)),                                         \
        .swSelCswFunc = \
        { \
            [0u] = 0u,                                                                                                                       \
            [1u] = 0u,                                                                                                                       \
            [2u] = 0u,                                                                                                                       \
            [3u] = 0u,                                                                                                                       \
            [4u] = 0u,                                                                                                                       \
            [5u] = 0u,                                                                                                                       \
            [6u] = 0u,                                                                                                                       \
            [7u] = 0u,                                                                                                                       \
        }, \
        .mode = \
        { \
            [0u] = \
            { \
                .senseDutyCtl = 0u,                                                                                                          \
                .swSelCdacFl = 0u,                                                                                                           \
                .swSelTop = 0u,                                                                                                              \
                .swSelComp = 0u,                                                                                                             \
                .swSelSh = 0u,                                                                                                               \
                .swSelCmod1 = 0u,                                                                                                            \
                .swSelCmod2 = 0u,                                                                                                            \
            }, \
            [1u] = \
            { \
                .senseDutyCtl = 0u,                                                                                                          \
                .swSelCdacFl = 0u,                                                                                                           \
                .swSelTop = 0u,                                                                                                              \
                .swSelComp = 0u,                                                                                                             \
                .swSelSh = 0u,                                                                                                               \
                .swSelCmod1 = 0u,                                                                                                            \
                .swSelCmod2 = 0u,                                                                                                            \
            }, \
            [2u] = \
            { \
                .senseDutyCtl = 0u,                                                                                                          \
                .swSelCdacFl = 0u,                                                                                                           \
                .swSelTop = 0u,                                                                                                              \
                .swSelComp = 0u,                                                                                                             \
                .swSelSh = 0u,                                                                                                               \
                .swSelCmod1 = 0u,                                                                                                            \
                .swSelCmod2 = 0u,                                                                                                            \
            }, \
            [3u] = \
            { \
                .senseDutyCtl = 0u,                                                                                                          \
                .swSelCdacFl = 0u,                                                                                                           \
                .swSelTop = 0u,                                                                                                              \
                .swSelComp = 0u,                                                                                                             \
                .swSelSh = 0u,                                                                                                               \
                .swSelCmod1 = 0u,                                                                                                            \
                .swSelCmod2 = 0u,                                                                                                            \
            }, \
        }, \
    }




/** \cond SECTION_CAPSENSE_INTERNAL */
    /** The Sensor Frame types, to be used with \ref Cy_CapSense_GenerateSensorConfig and \ref Cy_CapSense_GenerateAllSensorConfig */
    #define CY_CAPSENSE_SNS_FRAME_ACTIVE     (0u) /**<  - Sensor frame for Active slot    */
    #define CY_CAPSENSE_SNS_FRAME_LOW_POWER  (1u) /**<  - Sensor frame for Low Power slot */
/** \endcond */

#if defined(__cplusplus)
}
#endif

#endif /* CY_IP_M0S8MSCV3LP */

#endif /* CY_CAPSENSE_GENERATOR_LP_H */


/* [] END OF FILE */
