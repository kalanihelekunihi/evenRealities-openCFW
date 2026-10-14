typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef signed short int16_t;
typedef unsigned int uint32_t;
typedef struct cy_stc_capsense_ballistic_context_t cy_stc_capsense_ballistic_context_t;
typedef struct cy_stc_capsense_csx_touch_buffer_t cy_stc_capsense_csx_touch_buffer_t;
typedef struct cy_stc_capsense_csx_touch_history_t cy_stc_capsense_csx_touch_history_t;
typedef struct cy_stc_capsense_electrode_config_t cy_stc_capsense_electrode_config_t;
typedef struct cy_stc_capsense_gesture_config_t cy_stc_capsense_gesture_config_t;
typedef struct cy_stc_capsense_gesture_context_t cy_stc_capsense_gesture_context_t;
typedef struct cy_stc_capsense_mp_table_t cy_stc_capsense_mp_table_t;
typedef struct cy_stc_capsense_sensor_context_t cy_stc_capsense_sensor_context_t;
typedef struct cy_stc_capsense_smartsense_csd_noise_envelope_t cy_stc_capsense_smartsense_csd_noise_envelope_t;
typedef struct cy_stc_capsense_touch_t cy_stc_capsense_touch_t;
typedef struct cy_stc_capsense_widget_context_t cy_stc_capsense_widget_context_t;
#define CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN 1
#define CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP 1
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
    uint32_t centroidConfig;                                    /**< Configuration of centroids */
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

    cy_stc_capsense_ballistic_config_t ballisticConfig;         /**< The configuration data for position ballistic filter. */
    cy_stc_capsense_ballistic_context_t * ptrBallisticContext;  /**< Pointer to Ballistic filter context structure */

    cy_stc_capsense_adaptive_filter_config_t aiirConfig;        /**< The configuration of position adaptive filter. */
    cy_stc_capsense_advanced_touchpad_config_t advConfig;       /**< The configuration of CSD advanced touchpad */

    uint32_t posFilterConfig;                                   /**< Position filters configuration */
    uint16_t rawFilterConfig;                                   /**< Raw count filters configuration */

    uint16_t alpOnThreshold;                                    /**< ALP Filter ON threshold */
    uint16_t alpOffThreshold;                                   /**< ALP Filter OFF threshold */

    uint8_t senseMethod;                                        /**< Specifies the widget sensing method:
                                                                    * * 0 - UNDEFINED   (CY_CAPSENSE_UNDEFINED_GROUP)
                                                                    * * 1 - CSD         (CY_CAPSENSE_CSD_GROUP)
                                                                    * * 2 - CSX         (CY_CAPSENSE_CSX_GROUP)
                                                                    * * 3 - ISX         (CY_CAPSENSE_ISX_GROUP) */
    uint8_t wdType;                                             /**< Specifies the widget type */

    #if ((CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN) || (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP))
        cy_stc_capsense_mp_table_t * ptrMpTable;                /**< Pointer to the multi-phase vector and de-convolution coefficients
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint16_t firstSlotId;                                   /**< The slot ID in the widget to start scan from
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
        uint16_t numSlots;                                      /**< The number of slots in the widget
                                                                 * \note This field is available for the fifth-generation CAPSENSE&trade; and fifth-generation low power CAPSENSE&trade;.
                                                                 */
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
        uint8_t mfsConfig;                                      /**< Multi-frequency Scan (MFS) widget configuration.
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
    #endif

    #if (CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP)
        uint8_t iirCoeffHw;                                     /**< Raw count HW IIR filter coefficient. Smaller value leads to lower filtering.
                                                                * \note This field is available only for the fifth-generation low power CAPSENSE&trade;.
                                                                */
    #endif
    
} cy_stc_capsense_widget_config_t;
unsigned char widget_size_probe[sizeof(cy_stc_capsense_widget_config_t)];
