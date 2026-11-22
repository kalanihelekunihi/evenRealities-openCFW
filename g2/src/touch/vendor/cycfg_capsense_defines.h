/* SPDX-License-Identifier: MIT
 * CapSense configurator defines for G2 touch (PSoC 4000T / MSCLP LP).
 * Product cardinalities match the locked reset-copied common configuration,
 * three widget records, nine sensor contexts, and five active/four LP slots.
 * Other feature defaults still require generated-design validation.
 * Platform selection comes from CY_IP_M0S8MSCV3LP in the device header.
 */
#ifndef CYCFG_CAPSENSE_DEFINES_H
#define CYCFG_CAPSENSE_DEFINES_H

#include <stdint.h>

#define CY_CAPSENSE_TOTAL_WIDGET_COUNT          (3u)
#define CY_CAPSENSE_WIDGET_COUNT                CY_CAPSENSE_TOTAL_WIDGET_COUNT
#define CY_CAPSENSE_SENSOR_COUNT                (9u)
#define CY_CAPSENSE_PIN_COUNT                   (5u)
#define CY_CAPSENSE_SHIELD_PIN_COUNT            (2u)
#define CY_CAPSENSE_SLOT_COUNT                  (5u)
#define CY_CAPSENSE_LP_SLOT_COUNT               (4u)
#define CY_CAPSENSE_TOUCHPAD_SENSOR_COUNT       (0u)
#define CY_CAPSENSE_CSD_WIDGET_COUNT            (CY_CAPSENSE_TOTAL_WIDGET_COUNT)
#define CY_CAPSENSE_CSX_WIDGET_COUNT            (0u)
#define CY_CAPSENSE_ISX_WIDGET_COUNT            (0u)
#define CY_CAPSENSE_POSITION_FILTER_MODES_MASK  (0u)
#define CY_CAPSENSE_RAW_FILTER_MODES_MASK       (0u)
#define CY_CAPSENSE_SCAN_MODE                   (0u)
#define CY_CAPSENSE_TOTAL_WIRE_COUNT            (CY_CAPSENSE_PIN_COUNT)
#define CY_CAPSENSE_MAX_SENSORS_COUNT           (4u)
#define CY_CAPSENSE_TOTAL_CH_NUMBER             (1u)
#define CY_CAPSENSE_SENSOR_FRAME_SIZE           (8u)
#define CY_CAPSENSE_RAW_HISTORY_SIZE            (2u)
#define CY_CAPSENSE_IIR_HISTORY_LOW_SIZE        (1u)
#define CY_CAPSENSE_IIR_COEFF_LP                (1u)
#define CY_CAPSENSE_BSLN_COEFF_SLOW             (1u)
#define CY_CAPSENSE_BSLN_COEFF_FAST             (3u)
#define CY_CAPSENSE_BSLN_UPDATE_DELAY             (5u)
#define CY_CAPSENSE_LFSR_POLY                   (0x00000000u)
#define CY_CAPSENSE_LFSR_SCALE                  (0u)
#define CY_CAPSENSE_CDAC_DITHER_SEED            (0u)
#define CY_CAPSENSE_CDAC_DITHER_POLY            (0u)
#define CY_CAPSENSE_MODCLK_DIV                  (1u)
#define CY_CAPSENSE_NUM_FINE_INIT_CYCLES        (0u)
#define CY_CAPSENSE_CSD_CDAC_DITHER_EN          (0u)
#define CY_CAPSENSE_CSX_CDAC_DITHER_EN          (0u)
#define CY_CAPSENSE_ISX_CDAC_DITHER_EN          (0u)
#define CY_CAPSENSE_WOT_SCAN_INTERVAL           (0u)
#define CY_CAPSENSE_WOT_TIMEOUT                 (0u)


/* Feature enables — product defaults for G2 touch (MSCLP LP, CSD widgets). */
#ifndef CY_CAPSENSE_ENABLE
#define CY_CAPSENSE_ENABLE                      (1u)
#endif
#ifndef CY_CAPSENSE_DISABLE
#define CY_CAPSENSE_DISABLE                     (0u)
#endif
#define CY_CAPSENSE_LP_EN                       (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_EXT_FRM_START_EN            (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_LP_RC_IIR_FILTER_EN         (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_MULTI_PHASE_SELF_ENABLED    (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_CSD_CALIBRATION_EN          (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_CSX_CALIBRATION_EN          (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_ISX_CALIBRATION_EN          (CY_CAPSENSE_DISABLE)
/* Locked widget CDAC settings 0x1AA/0x1A1 use automatic reference, fine,
 * compensation and compensation-divider modes. The stock calibration path
 * contains all four corresponding branches. */
#define CY_CAPSENSE_CSD_CDAC_COMP_EN            (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_CSD_CDAC_COMP_DIV_AUTO_EN   (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_CSD_CDAC_REF_AUTO_EN        (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_CSD_CDAC_FINE_EN            (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_CDAC_REF_AUTO_EN            (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_CDAC_FINE_AUTO_EN           (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_CDAC_COMP_AUTO_EN           (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_CDAC_COMP_DIV_AUTO_EN       (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_CDAC_AUTO_DITHER_EN         (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_SMARTSENSE_FULL_EN          (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_SMARTSENSE_HW_EN            (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_CSD_EN                      (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_CSX_EN                      (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_ISX_EN                      (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_GESTURE_EN                  (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_CENTROID_3X3_CSD_EN         (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_CENTROID_5X5_CSD_EN         (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_BALLISTIC_MULTIPLIER_EN     (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_ADVANCED_CENTROID_5X5_EN    (CY_CAPSENSE_DISABLE)
/* The locked common config selects active shield mode with two shield pins. */
#define CY_CAPSENSE_CSD_SHIELD_EN               (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_SHIELD_ACTIVE_EN            (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_SHIELD_PASSIVE_EN           (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_CSD_SHIELD_TANK_EN          (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_TX_VOLTAGE_EN               (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_TUNER_ENABLE                (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_CI_EN                       (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_BIST_SUPPORTED              (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_RAWCOUNT_FILTER_EN          (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_POSITION_FILTER_EN          (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_MPSC_EN                     (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_WBX_EN                      (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_CSD_AUTODAC_EN              (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_CSX_AUTODAC_EN              (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_ISX_AUTODAC_EN              (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_CDAC_COMP_USAGE_EN          (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_CDAC_REF_USAGE_EN           (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_CDAC_FINE_USAGE_EN          (CY_CAPSENSE_ENABLE)
#define CY_CAPSENSE_PERCENTAGE_100              (100u)


#define CY_CAPSENSE_SLOT_LP_COUNT               (CY_CAPSENSE_LP_SLOT_COUNT)
#define CY_CAPSENSE_CIC2_FILTER_EN              (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_REGULAR_RC_HW_IIR_FILTER_EN (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_REGULAR_RC_IIR_FILTER_EN    (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_REGULAR_RC_MEDIAN_FILTER_EN (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_REGULAR_RC_AVERAGE_FILTER_EN (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_LP_RC_MEDIAN_FILTER_EN      (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_LP_RC_AVERAGE_FILTER_EN     (CY_CAPSENSE_DISABLE)
#define CY_CAPSENSE_FIFO_SNS_LP_MAX_NUM         (16u)
#define CY_CAPSENSE_FIFO_SNS_MAX_NUM            (32u)
#define CY_CAPSENSE_LP_SENSOR_FRAME_SIZE        (CY_CAPSENSE_SENSOR_FRAME_SIZE)
#define CY_CAPSENSE_MAX_CH_NUM                  (1u)
#define CY_CAPSENSE_TOTAL_ELTD_COUNT            (CY_CAPSENSE_SENSOR_COUNT)


#define CY_CAPSENSE_NUM_EPI_KREF_DELAY          (0u)
#define CY_CAPSENSE_NUM_EPI_KREF_DELAY_PRS      (0u)

#endif /* CYCFG_CAPSENSE_DEFINES_H */
