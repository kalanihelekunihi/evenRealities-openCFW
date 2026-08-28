/* SPDX-License-Identifier: MIT */
#include "pt_protocol_board_leaf_candidates.h"

#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_PT_SYSTEM_RESET_INNER
#define OPEN_CFW_PT_SYSTEM_RESET_INNER \
    open_cfw_pt_system_reset_inner
#endif
#ifndef OPEN_CFW_PT_SYSTEM_RESET_CONTROL
#define OPEN_CFW_PT_SYSTEM_RESET_CONTROL \
    ((volatile uint32_t *)(uintptr_t)0xE000ED0CU)
#endif
#ifndef OPEN_CFW_PT_SYSTEM_RESET_BARRIER
#define OPEN_CFW_PT_SYSTEM_RESET_BARRIER() __sync_synchronize()
#endif
#ifndef OPEN_CFW_PT_SYSTEM_RESET_WAIT
#define OPEN_CFW_PT_SYSTEM_RESET_WAIT() \
    do { for (;;) { } } while (0)
#endif

#ifndef OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_0
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_0 \
    open_cfw_pt_display_postprocess_state_0
#endif
#ifndef OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_1
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_1 \
    open_cfw_pt_display_postprocess_state_1
#endif
#ifndef OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_2
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_2 \
    open_cfw_pt_display_postprocess_state_2
#endif

#ifndef OPEN_CFW_PT_DISPLAY_POSTPROCESS_READY
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_READY \
    ((const volatile uint8_t *)(uintptr_t)0x20074F2CU)
#endif
#ifndef OPEN_CFW_PT_DISPLAY_POSTPROCESS_ACTIVE
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_ACTIVE \
    ((const volatile uint32_t *)(uintptr_t)0x200744E0U)
#endif
#ifndef OPEN_CFW_PT_DISPLAY_POSTPROCESS_PRIMARY
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_PRIMARY \
    ((const volatile uint32_t *)(uintptr_t)0x200744D8U)
#endif
#ifndef OPEN_CFW_PT_DISPLAY_POSTPROCESS_MODE
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_MODE \
    ((const volatile uint32_t *)(uintptr_t)0x200744DCU)
#endif
#ifndef OPEN_CFW_PT_DISPLAY_POSTPROCESS_SEND
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_SEND \
    ((void (*)(uint32_t, uint32_t, uint32_t, uint32_t)) \
        (uintptr_t)0x00464C37U)
#endif
#ifndef OPEN_CFW_PT_DISPLAY_POSTPROCESS_REFRESH
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_REFRESH \
    ((void (*)(void))(uintptr_t)0x004D9A85U)
#endif
#ifndef OPEN_CFW_PT_DISPLAY_POSTPROCESS_ONBOARDING
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_ONBOARDING \
    ((int (*)(uint8_t, const uint8_t *))(uintptr_t)0x004A7821U)
#endif
#ifndef OPEN_CFW_PT_DISPLAY_POSTPROCESS_REMOVE
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_REMOVE \
    ((int (*)(const void *))(uintptr_t)0x0047498DU)
#endif
#ifndef OPEN_CFW_PT_DISPLAY_POSTPROCESS_PATH
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_PATH \
    ((const void *)(uintptr_t)0x0076F518U)
#endif
#ifndef OPEN_CFW_PT_DISPLAY_POSTPROCESS_COMMIT
#define OPEN_CFW_PT_DISPLAY_POSTPROCESS_COMMIT \
    open_cfw_pt_display_postprocess_commit
#endif
#ifndef OPEN_CFW_PT_MRAM_DELETE_ALL_RECORDS
#define OPEN_CFW_PT_MRAM_DELETE_ALL_RECORDS \
    ((void (*)(void))(uintptr_t)0x0047ACF9U)
#endif
#ifndef OPEN_CFW_PT_PRIVACY_CLEAR
#define OPEN_CFW_PT_PRIVACY_CLEAR \
    ((void (*)(void))(uintptr_t)0x004D28B1U)
#endif
#ifndef OPEN_CFW_PT_PAIRING_FLAG_0
#define OPEN_CFW_PT_PAIRING_FLAG_0 \
    ((volatile uint8_t *)(uintptr_t)0x20071A34U)
#endif
#ifndef OPEN_CFW_PT_PAIRING_WORD
#define OPEN_CFW_PT_PAIRING_WORD \
    ((volatile uint32_t *)(uintptr_t)0x20071A38U)
#endif
#ifndef OPEN_CFW_PT_PAIRING_FLAG_1
#define OPEN_CFW_PT_PAIRING_FLAG_1 \
    ((volatile uint8_t *)(uintptr_t)0x20071A3CU)
#endif
#ifndef OPEN_CFW_PT_FONT_0_BASE
#define OPEN_CFW_PT_FONT_0_BASE UINT32_C(0x80100000)
#endif
#ifndef OPEN_CFW_PT_FONT_1_BASE
#define OPEN_CFW_PT_FONT_1_BASE UINT32_C(0x80700000)
#endif
#ifndef OPEN_CFW_PT_FONT_XIP_START
#define OPEN_CFW_PT_FONT_XIP_START UINT32_C(0x80000000)
#endif
#ifndef OPEN_CFW_PT_FONT_XIP_END
#define OPEN_CFW_PT_FONT_XIP_END UINT32_C(0x82000000)
#endif
#ifndef OPEN_CFW_PT_FONT_XIP_ACQUIRE
#define OPEN_CFW_PT_FONT_XIP_ACQUIRE \
    open_cfw_pt_font_xip_acquire
#endif
#ifndef OPEN_CFW_PT_FONT_XIP_RELEASE
#define OPEN_CFW_PT_FONT_XIP_RELEASE \
    open_cfw_pt_font_xip_release
#endif
#ifndef OPEN_CFW_PT_FONT_XIP_CONFIGURATION_FLAG
#define OPEN_CFW_PT_FONT_XIP_CONFIGURATION_FLAG \
    ((const volatile uint8_t *)(uintptr_t)0x20074FB8U)
#endif
#ifndef OPEN_CFW_PT_FONT_XIP_ACTIVE
#define OPEN_CFW_PT_FONT_XIP_ACTIVE \
    ((volatile uint8_t *)(uintptr_t)0x20074FB9U)
#endif
#ifndef OPEN_CFW_PT_FONT_XIP_MUTEX_LINK
#define OPEN_CFW_PT_FONT_XIP_MUTEX_LINK \
    ((void *const volatile *)(uintptr_t)0x20074548U)
#endif
#ifndef OPEN_CFW_PT_FONT_XIP_DEVICE_LINK
#define OPEN_CFW_PT_FONT_XIP_DEVICE_LINK \
    ((void *const volatile *)(uintptr_t)0x20074544U)
#endif
#ifndef OPEN_CFW_PT_MSPI_CONTROL
#define OPEN_CFW_PT_MSPI_CONTROL \
    ((int32_t (*)(void *, uint32_t, uint32_t))(uintptr_t)0x004C26E1U)
#endif
#ifndef OPEN_CFW_PT_FONT_XIP_READ
static void open_cfw_pt_font_xip_read_default(uint32_t address,
                                               uint8_t *destination,
                                               uint32_t length)
{
    const volatile uint8_t *source =
        (const volatile uint8_t *)(uintptr_t)address;
    uint32_t index;

    OPEN_CFW_PT_FONT_XIP_ACQUIRE();
    for (index = 0U; index < length; ++index)
        destination[index] = source[index];
    OPEN_CFW_PT_FONT_XIP_RELEASE();
}
#define OPEN_CFW_PT_FONT_XIP_READ(address, destination, length) \
    open_cfw_pt_font_xip_read_default((address), (destination), (length))
#endif


#ifndef OPEN_CFW_PT_DISPLAY_STATE
#define OPEN_CFW_PT_DISPLAY_STATE \
    ((const uint8_t *)(uintptr_t)0x20074F2CU)
#endif

#ifndef OPEN_CFW_PT_CODEC_IDENTIFIER_WORD
#define OPEN_CFW_PT_CODEC_IDENTIFIER_WORD \
    ((const volatile uint32_t *)(uintptr_t)0x20074224U)
#endif

#ifndef OPEN_CFW_PT_INPUT_MESSAGE_SEND
#define OPEN_CFW_PT_INPUT_MESSAGE_SEND \
    open_cfw_pt_input_message_send
#endif
#ifndef OPEN_CFW_PT_INPUT_THREAD_LINK
#define OPEN_CFW_PT_INPUT_THREAD_LINK \
    ((void *const volatile *)(uintptr_t)0x20004094U)
#endif
#ifndef OPEN_CFW_PT_INPUT_QUEUE_LINK
#define OPEN_CFW_PT_INPUT_QUEUE_LINK \
    ((void *const volatile *)(uintptr_t)0x20004098U)
#endif

#ifndef OPEN_CFW_PT_BUZZER_PREPARE
#define OPEN_CFW_PT_BUZZER_PREPARE \
    ((void (*)(void))(uintptr_t)0x00502AC5U)
#endif

#ifndef OPEN_CFW_PT_BUZZER_ROUTE_WORD
#define OPEN_CFW_PT_BUZZER_ROUTE_WORD \
    ((const volatile uint32_t *)(uintptr_t)0x20000724U)
#endif

#ifndef OPEN_CFW_PT_BUZZER_APPLY
#define OPEN_CFW_PT_BUZZER_APPLY \
    ((void (*)(uint32_t, uint8_t))(uintptr_t)0x005027FDU)
#endif

#ifndef OPEN_CFW_PT_BUZZER_DISABLE
#define OPEN_CFW_PT_BUZZER_DISABLE \
    ((void (*)(uint32_t))(uintptr_t)0x0050280BU)
#endif

#ifndef OPEN_CFW_PT_HARDWARE_IDENTIFIER_READ
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_READ \
    ((void (*)(uint32_t, uint32_t *))(uintptr_t)0x00480D73U)
#endif

#ifndef OPEN_CFW_PT_HARDWARE_IDENTIFIER_2_READ
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_2_READ \
    ((int32_t (*)(const void *, uint32_t, uint8_t *, uint32_t)) \
        (uintptr_t)0x0055FC39U)
#endif

#ifndef OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_STATE
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_STATE \
    ((const volatile uint32_t *)(uintptr_t)0x20074544U)
#endif

#ifndef OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_INITIALIZE
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_INITIALIZE \
    ((int (*)(void))(uintptr_t)0x0046FE39U)
#endif

#ifndef OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_ACQUIRE
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_ACQUIRE \
    open_cfw_pt_font_xip_acquire
#endif

#ifndef OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_PREPARE
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_PREPARE \
    ((void (*)(void))(uintptr_t)0x00470F69U)
#endif

#ifndef OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_READ
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_READ \
    ((int (*)(uint32_t *))(uintptr_t)0x00470029U)
#endif

#ifndef OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_FINISH
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_FINISH \
    ((void (*)(void))(uintptr_t)0x00470E91U)
#endif

#ifndef OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_RELEASE
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_RELEASE \
    open_cfw_pt_font_xip_release
#endif

#ifndef OPEN_CFW_PT_HARDWARE_IDENTIFIER_2_DEVICE
#define OPEN_CFW_PT_HARDWARE_IDENTIFIER_2_DEVICE \
    ((const void *)(uintptr_t)0x20074068U)
#endif

#ifndef OPEN_CFW_PT_CHARGER_OPEN
#define OPEN_CFW_PT_CHARGER_OPEN \
    ((void *(*)(const void *, uint32_t))(uintptr_t)0x0055EFF1U)
#endif

#ifndef OPEN_CFW_PT_CHARGER_DEVICE
#define OPEN_CFW_PT_CHARGER_DEVICE \
    ((const void *)(uintptr_t)0x20070F78U)
#endif

#ifndef OPEN_CFW_PT_CHARGER_DISABLE
#define OPEN_CFW_PT_CHARGER_DISABLE \
    ((int32_t (*)(void *, uint32_t))(uintptr_t)0x0055F0D9U)
#endif

#ifndef OPEN_CFW_PT_CHARGER_ENABLE
#define OPEN_CFW_PT_CHARGER_ENABLE \
    ((int32_t (*)(void *, uint32_t))(uintptr_t)0x0055F07BU)
#endif

#define OPEN_CFW_PT_PLATFORM_SUCCESS ((int32_t)0x2BAD0000U)

#ifndef OPEN_CFW_PT_UART_WRITE
#define OPEN_CFW_PT_UART_WRITE \
    ((int (*)(const uint8_t *, uint32_t, uint32_t)) \
        (uintptr_t)0x00584C99U)
#endif

#ifndef OPEN_CFW_PT_AUDIO_STATUS_BASE
#define OPEN_CFW_PT_AUDIO_STATUS_BASE \
    ((const uint8_t *)(uintptr_t)0x20074368U)
#endif

#ifndef OPEN_CFW_PT_CODEC_ROUTE_SET
#define OPEN_CFW_PT_CODEC_ROUTE_SET \
    ((int (*)(uint32_t, uint8_t))(uintptr_t)0x00480FD7U)
#endif

#ifndef OPEN_CFW_PT_AUDIO_CAPTURE_ACTIVE
#define OPEN_CFW_PT_AUDIO_CAPTURE_ACTIVE \
    ((volatile uint32_t *)(uintptr_t)0x20074890U)
#endif

#ifndef OPEN_CFW_PT_AUDIO_REGISTER
#define OPEN_CFW_PT_AUDIO_REGISTER \
    open_cfw_pt_audio_register
#endif

#ifndef OPEN_CFW_PT_AUDIO_REMOVE
#define OPEN_CFW_PT_AUDIO_REMOVE \
    open_cfw_pt_audio_remove
#endif
#ifndef OPEN_CFW_PT_AUDIO_REGISTRATION_TABLE
#define OPEN_CFW_PT_AUDIO_REGISTRATION_TABLE \
    ((volatile struct open_cfw_pt_audio_registration *)(uintptr_t)0x20073C20U)
#endif

#ifndef OPEN_CFW_PT_AUDIO_SINGLE_CALLBACK
#define OPEN_CFW_PT_AUDIO_SINGLE_CALLBACK \
    ((const void *)(uintptr_t)0x0058F5E1U)
#endif

#ifndef OPEN_CFW_PT_AUDIO_STEREO_CALLBACK
#define OPEN_CFW_PT_AUDIO_STEREO_CALLBACK \
    ((const void *)(uintptr_t)0x0058F4E5U)
#endif

#ifndef OPEN_CFW_PT_CODEC_MIC_ENABLE
#define OPEN_CFW_PT_CODEC_MIC_ENABLE \
    open_cfw_pt_codec_mic_enable
#endif

#ifndef OPEN_CFW_PT_PDM_MIC_ENABLE
#define OPEN_CFW_PT_PDM_MIC_ENABLE \
    open_cfw_pt_pdm_mic_enable
#endif
#ifndef OPEN_CFW_PT_AUDIO_THREAD_LINK
#define OPEN_CFW_PT_AUDIO_THREAD_LINK \
    ((void *const volatile *)(uintptr_t)0x20003FA0U)
#endif
#ifndef OPEN_CFW_PT_AUDIO_QUEUE_LINK
#define OPEN_CFW_PT_AUDIO_QUEUE_LINK \
    ((void *const volatile *)(uintptr_t)0x20003FA4U)
#endif

#ifndef OPEN_CFW_PT_PCM_ROUTE
#define OPEN_CFW_PT_PCM_ROUTE \
    ((void (*)(uint32_t))(uintptr_t)0x0057B12DU)
#endif

#ifndef OPEN_CFW_PT_AUDIO_UNREGISTER
#define OPEN_CFW_PT_AUDIO_UNREGISTER \
    open_cfw_pt_audio_unregister
#endif

#ifndef OPEN_CFW_PT_AUDIO_RELEASE
#define OPEN_CFW_PT_AUDIO_RELEASE \
    ((void (*)(void *))(uintptr_t)0x0057A927U)
#endif

#ifndef OPEN_CFW_PT_AUDIO_CODEC_BUFFER_0
#define OPEN_CFW_PT_AUDIO_CODEC_BUFFER_0 \
    ((void *)(uintptr_t)0x20106A7CU)
#endif

#ifndef OPEN_CFW_PT_AUDIO_CODEC_BUFFER_1
#define OPEN_CFW_PT_AUDIO_CODEC_BUFFER_1 \
    ((void *)(uintptr_t)0x201074C0U)
#endif

#ifndef OPEN_CFW_PT_AUDIO_PDM_BUFFER
#define OPEN_CFW_PT_AUDIO_PDM_BUFFER \
    ((void *)(uintptr_t)0x20107F04U)
#endif

#ifndef OPEN_CFW_PT_DISPLAY_STAGE_1_WORD
#define OPEN_CFW_PT_DISPLAY_STAGE_1_WORD \
    ((volatile uint32_t *)(uintptr_t)0x2000064CU)
#endif

#ifndef OPEN_CFW_PT_DISPLAY_STAGE_3_WORD
#define OPEN_CFW_PT_DISPLAY_STAGE_3_WORD \
    ((volatile uint32_t *)(uintptr_t)0x20000648U)
#endif

#ifndef OPEN_CFW_PT_DISPLAY_STAGE_2_FIRST_WORD
#define OPEN_CFW_PT_DISPLAY_STAGE_2_FIRST_WORD \
    ((volatile uint32_t *)(uintptr_t)0x20000650U)
#endif

#ifndef OPEN_CFW_PT_DISPLAY_STAGE_2_SECOND_WORD
#define OPEN_CFW_PT_DISPLAY_STAGE_2_SECOND_WORD \
    ((volatile uint32_t *)(uintptr_t)0x200744C8U)
#endif

#ifndef OPEN_CFW_PT_DISPLAY_REINITIALIZE
#define OPEN_CFW_PT_DISPLAY_REINITIALIZE \
    ((void (*)(void))(uintptr_t)0x0047381FU)
#endif

struct open_cfw_pt_uled_operations {
    void (*terminate)(void);
    int (*read_chip_id)(uint16_t *identifier);
    void (*mspi_initialize)(void);
    void (*panel_initialize)(void);
    void (*power_up)(void);
    void (*power_down)(void);
    int (*set_brightness)(uint32_t delay, uint32_t period,
                          uint32_t brightness);
    void (*clear_screen)(void);
    void (*set_current)(void);
    int (*set_display_offset)(uint8_t first, uint8_t second);
};

#ifndef OPEN_CFW_PT_ULED_OPERATIONS_LINK
#define OPEN_CFW_PT_ULED_OPERATIONS_LINK \
    ((const struct open_cfw_pt_uled_operations *const volatile *) \
        (uintptr_t)0x20074530U)
#endif

#ifndef OPEN_CFW_PT_DISPLAY_APPLY
#define OPEN_CFW_PT_DISPLAY_APPLY \
    ((void (*)(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t)) \
        (uintptr_t)0x00474067U)
#endif

#ifndef OPEN_CFW_PT_DISPLAY_MUTEX_LINK
#define OPEN_CFW_PT_DISPLAY_MUTEX_LINK \
    ((void *const volatile *)(uintptr_t)0x200744E8U)
#endif

#ifndef OPEN_CFW_PT_DISPLAY_QUEUE_LINK
#define OPEN_CFW_PT_DISPLAY_QUEUE_LINK \
    ((void *const volatile *)(uintptr_t)0x200744E4U)
#endif

#ifndef OPEN_CFW_PT_DISPLAY_BUFFER
#define OPEN_CFW_PT_DISPLAY_BUFFER \
    ((void *)(uintptr_t)0x20073B60U)
#endif

#ifndef OPEN_CFW_PT_MUTEX_ACQUIRE
#define OPEN_CFW_PT_MUTEX_ACQUIRE \
    ((int (*)(void *, uint32_t))(uintptr_t)0x004497B7U)
#endif

#ifndef OPEN_CFW_PT_MUTEX_RELEASE
#define OPEN_CFW_PT_MUTEX_RELEASE \
    ((int (*)(void *))(uintptr_t)0x0044981DU)
#endif

#ifndef OPEN_CFW_PT_DISPLAY_BUFFER_WRITE
#define OPEN_CFW_PT_DISPLAY_BUFFER_WRITE \
    open_cfw_pt_display_buffer_write
#endif

#ifndef OPEN_CFW_PT_QUEUE_SEND
#define OPEN_CFW_PT_QUEUE_SEND \
    ((int (*)(void *, const void *, uint32_t, uint32_t)) \
        (uintptr_t)0x00449ABFU)
#endif

#ifndef OPEN_CFW_PT_FAIL_STOP
#define OPEN_CFW_PT_FAIL_STOP \
    ((void (*)(void))(uintptr_t)0x005FA0A5U)
#endif

#ifndef OPEN_CFW_PT_LENS_SYNC_QUEUE_LINK
#define OPEN_CFW_PT_LENS_SYNC_QUEUE_LINK \
    ((void *const volatile *)(uintptr_t)0x200749CCU)
#endif

#ifndef OPEN_CFW_PT_LENS_SYNC_EVENT_LINK
#define OPEN_CFW_PT_LENS_SYNC_EVENT_LINK \
    ((void *const volatile *)(uintptr_t)0x20074B10U)
#endif

#ifndef OPEN_CFW_PT_LENS_SYNC_ALLOCATE
#define OPEN_CFW_PT_LENS_SYNC_ALLOCATE \
    open_cfw_pt_lens_sync_allocate
#endif
#ifndef OPEN_CFW_PT_FILE_HEAP_ALLOCATE
#define OPEN_CFW_PT_FILE_HEAP_ALLOCATE \
    ((void *(*)(uint32_t))(uintptr_t)0x00474CD3U)
#endif

#ifndef OPEN_CFW_PT_LENS_SYNC_RELEASE
#define OPEN_CFW_PT_LENS_SYNC_RELEASE \
    ((void (*)(void *))(uintptr_t)0x00474D17U)
#endif

#ifndef OPEN_CFW_PT_EVENT_FLAGS_SET
#define OPEN_CFW_PT_EVENT_FLAGS_SET \
    ((uint32_t (*)(void *, uint32_t))(uintptr_t)0x004495E5U)
#endif

#ifndef OPEN_CFW_PT_THREAD_FLAGS_SET
#define OPEN_CFW_PT_THREAD_FLAGS_SET \
    ((uint32_t (*)(void *, uint32_t))(uintptr_t)0x00449239U)
#endif

#ifndef OPEN_CFW_PT_AUDIO_PATH_TABLE
#define OPEN_CFW_PT_AUDIO_PATH_TABLE \
    ((const uint8_t *)(uintptr_t)0x20073C08U)
#endif

#ifndef OPEN_CFW_PT_AUDIO_PATH_FORMAT_PROVIDER
#define OPEN_CFW_PT_AUDIO_PATH_FORMAT_PROVIDER \
    open_cfw_pt_audio_path_format_provider
#endif
#ifndef OPEN_CFW_PT_AUDIO_NAME_TABLE
#define OPEN_CFW_PT_AUDIO_NAME_TABLE \
    ((const char *const volatile *)(uintptr_t)0x200036D0U)
#endif
#ifndef OPEN_CFW_PT_AUDIO_RECORDER_TABLE
#define OPEN_CFW_PT_AUDIO_RECORDER_TABLE \
    ((volatile struct open_cfw_pt_audio_recorder *)(uintptr_t)0x20073C08U)
#endif
#ifndef OPEN_CFW_PT_FILE_CLOSE
#define OPEN_CFW_PT_FILE_CLOSE \
    ((int (*)(void *))(uintptr_t)0x004745F5U)
#endif

#ifndef OPEN_CFW_PT_TIME_READ
#define OPEN_CFW_PT_TIME_READ \
    ((void (*)(void *))(uintptr_t)0x0047EF11U)
#endif

#ifndef OPEN_CFW_PT_SECONDS_TO_TIME
#define OPEN_CFW_PT_SECONDS_TO_TIME \
    open_cfw_pt_seconds_to_time
#endif

#ifndef OPEN_CFW_PT_RTC_SET_TIME
#define OPEN_CFW_PT_RTC_SET_TIME \
    ((void (*)(const void *))(uintptr_t)0x0047EE79U)
#endif

#ifndef OPEN_CFW_PT_TIME_TO_SECONDS
#define OPEN_CFW_PT_TIME_TO_SECONDS \
    open_cfw_pt_time_to_seconds
#endif

#ifndef OPEN_CFW_PT_TIME_OUTPUT
#define OPEN_CFW_PT_TIME_OUTPUT \
    open_cfw_pt_time_output
#endif

#ifndef OPEN_CFW_PT_TIME_FORMAT_WORD
#define OPEN_CFW_PT_TIME_FORMAT_WORD \
    ((const volatile uint32_t *)(uintptr_t)0x200736ECU)
#endif

#ifndef OPEN_CFW_PT_TIME_CONFIGURATION_LINK
#define OPEN_CFW_PT_TIME_CONFIGURATION_LINK \
    ((const uint8_t *const volatile *)(uintptr_t)0x200036FCU)
#endif

#ifndef OPEN_CFW_PT_AMBIENT_ASSIGN
#define OPEN_CFW_PT_AMBIENT_ASSIGN \
    open_cfw_pt_ambient_assign
#endif

#ifndef OPEN_CFW_PT_AMBIENT_SAMPLE
#define OPEN_CFW_PT_AMBIENT_SAMPLE \
    open_cfw_pt_ambient_sample
#endif

#ifndef OPEN_CFW_PT_AMBIENT_RAW_READ
#define OPEN_CFW_PT_AMBIENT_RAW_READ \
    open_cfw_pt_ambient_raw_read
#endif
#ifndef OPEN_CFW_PT_AMBIENT_BUS_READ
#define OPEN_CFW_PT_AMBIENT_BUS_READ \
    ((int (*)(uint32_t, uint32_t, const void *, uint32_t, void *, uint32_t)) \
        (uintptr_t)0x0050436FU)
#endif
#ifndef OPEN_CFW_PT_AMBIENT_BUS_WRITE
#define OPEN_CFW_PT_AMBIENT_BUS_WRITE \
    ((int (*)(uint32_t, uint32_t, const void *, uint32_t, const void *, \
              uint32_t))(uintptr_t)0x005044B5U)
#endif

#ifndef OPEN_CFW_PT_LENS_SIDE
#define OPEN_CFW_PT_LENS_SIDE \
    ((uint8_t (*)(void))(uintptr_t)0x0045A569U)
#endif

#ifndef OPEN_CFW_PT_AUDIO_CODEC_ROUTE
#define OPEN_CFW_PT_AUDIO_CODEC_ROUTE \
    ((void (*)(uint32_t, uint32_t))(uintptr_t)0x00480F0DU)
#endif

#ifndef OPEN_CFW_PT_DELAY_TICKS
#define OPEN_CFW_PT_DELAY_TICKS \
    ((int (*)(uint32_t))(uintptr_t)0x00449377U)
#endif

#ifndef OPEN_CFW_PT_AMBIENT_ROUTE_WORD
#define OPEN_CFW_PT_AMBIENT_ROUTE_WORD \
    ((const volatile uint32_t *)(uintptr_t)0x0078EE40U)
#endif

#ifndef OPEN_CFW_PT_AMBIENT_INIT_REGISTER
#define OPEN_CFW_PT_AMBIENT_INIT_REGISTER \
    ((volatile uint32_t *)(uintptr_t)0x4001044CU)
#endif

#ifndef OPEN_CFW_PT_AMBIENT_RESET_REGISTER
#define OPEN_CFW_PT_AMBIENT_RESET_REGISTER \
    ((volatile uint32_t *)(uintptr_t)0x40010468U)
#endif


uint8_t open_cfw_pt_display_postprocess_state_0(void)
{
    return *OPEN_CFW_PT_DISPLAY_POSTPROCESS_READY == 1U ? 1U : 0U;
}


uint8_t open_cfw_pt_display_postprocess_state_1(void)
{
    return *OPEN_CFW_PT_DISPLAY_POSTPROCESS_ACTIVE != 0U ? 1U : 0U;
}


uint8_t open_cfw_pt_display_postprocess_state_2(void)
{
    return (*OPEN_CFW_PT_DISPLAY_POSTPROCESS_PRIMARY != 0U &&
            *OPEN_CFW_PT_DISPLAY_POSTPROCESS_MODE == 1U) ? 1U : 0U;
}


static uint32_t open_cfw_pt_unsigned_divide(uint32_t numerator,
                                            uint32_t denominator,
                                            uint32_t *remainder_output)
{
    uint32_t quotient = 0U;
    uint32_t remainder = 0U;
    uint32_t bit;

    if (denominator == 0U) {
        if (remainder_output != NULL) *remainder_output = numerator;
        return 0U;
    }
    for (bit = 0U; bit < 32U; ++bit) {
        remainder = (remainder << 1U) | (numerator >> 31U);
        numerator <<= 1U;
        quotient <<= 1U;
        if (remainder >= denominator) {
            remainder -= denominator;
            quotient |= 1U;
        }
    }
    if (remainder_output != NULL) *remainder_output = remainder;
    return quotient;
}


static uint8_t open_cfw_pt_is_leap_year(uint32_t year)
{
    uint32_t remainder;

    (void)open_cfw_pt_unsigned_divide(year, 4U, &remainder);
    if (remainder != 0U) return 0U;
    (void)open_cfw_pt_unsigned_divide(year, 100U, &remainder);
    if (remainder != 0U) return 1U;
    (void)open_cfw_pt_unsigned_divide(year, 400U, &remainder);
    return remainder == 0U ? 1U : 0U;
}


static uint32_t open_cfw_pt_month_days(uint32_t year, uint32_t month)
{
    static const uint8_t days[12] = {
        31U, 28U, 31U, 30U, 31U, 30U,
        31U, 31U, 30U, 31U, 30U, 31U
    };
    if (month == 0U || month > 12U) return 0U;
    if (month == 2U && open_cfw_pt_is_leap_year(year) != 0U) return 29U;
    return days[month - 1U];
}


void open_cfw_pt_seconds_to_time(uint32_t seconds, void *output)
{
    enum {
        OPEN_CFW_PT_SECONDS_PER_DAY = 86400U,
        OPEN_CFW_PT_EPOCH_2000 = 946684800U
    };
    open_cfw_pt_time_record *record = output;
    uint32_t day_count;
    uint32_t day_seconds;
    uint32_t year = 2000U;
    uint32_t month = 1U;

    if (record == NULL) return;
    if (seconds < OPEN_CFW_PT_EPOCH_2000) {
        day_count = 0U;
        day_seconds = 0U;
    } else {
        uint32_t since_2000 = seconds - OPEN_CFW_PT_EPOCH_2000;
        day_count = open_cfw_pt_unsigned_divide(
            since_2000, OPEN_CFW_PT_SECONDS_PER_DAY, &day_seconds);
    }

    record->read_error = 0U;
    (void)open_cfw_pt_unsigned_divide(day_count + 6U, 7U,
                                      &record->weekday);
    record->century_bit = 0U;
    while (day_count >= (open_cfw_pt_is_leap_year(year) != 0U ? 366U : 365U)) {
        day_count -= open_cfw_pt_is_leap_year(year) != 0U ? 366U : 365U;
        ++year;
    }
    while (day_count >= open_cfw_pt_month_days(year, month)) {
        day_count -= open_cfw_pt_month_days(year, month);
        ++month;
    }
    record->year = year - 2000U;
    record->month = month;
    record->day = day_count + 1U;
    record->hour = open_cfw_pt_unsigned_divide(day_seconds, 3600U, NULL);
    record->minute = open_cfw_pt_unsigned_divide(day_seconds, 60U,
                                                  &record->second);
    (void)open_cfw_pt_unsigned_divide(record->minute, 60U,
                                      &record->minute);
    record->hundredths = 0U;
}


int32_t open_cfw_pt_time_to_seconds(const void *input)
{
    enum {
        OPEN_CFW_PT_SECONDS_PER_DAY = 86400U,
        OPEN_CFW_PT_EPOCH_2000 = 946684800U
    };
    const open_cfw_pt_time_record *record = input;
    uint32_t year;
    uint32_t month;
    uint32_t days = 0U;
    uint32_t seconds;

    if (record == NULL || record->year > 99U ||
            record->month == 0U || record->month > 12U ||
            record->day == 0U ||
            record->day > open_cfw_pt_month_days(2000U + record->year,
                                                  record->month) ||
            record->hour > 23U || record->minute > 59U ||
            record->second > 59U)
        return -1;
    for (year = 2000U; year < 2000U + record->year; ++year)
        days += open_cfw_pt_is_leap_year(year) != 0U ? 366U : 365U;
    for (month = 1U; month < record->month; ++month)
        days += open_cfw_pt_month_days(2000U + record->year, month);
    days += record->day - 1U;
    seconds = OPEN_CFW_PT_EPOCH_2000 + days * OPEN_CFW_PT_SECONDS_PER_DAY +
        record->hour * 3600U + record->minute * 60U + record->second;
    if (record->hundredths >= 50U) ++seconds;
    return (int32_t)seconds;
}


void open_cfw_pt_time_output(int32_t seconds, void *output)
{
    open_cfw_pt_time_record *record = output;
    open_cfw_pt_seconds_to_time((uint32_t)seconds, output);
    if (record != NULL && *OPEN_CFW_PT_TIME_FORMAT_WORD == 1U) {
        (void)open_cfw_pt_unsigned_divide(record->hour, 12U,
                                          &record->hour);
        if (record->hour == 0U) record->hour = 12U;
    }
}


void open_cfw_pt_system_reset_inner(void)
{
    uint32_t control;
    OPEN_CFW_PT_SYSTEM_RESET_BARRIER();
    control = *OPEN_CFW_PT_SYSTEM_RESET_CONTROL;
    *OPEN_CFW_PT_SYSTEM_RESET_CONTROL =
        (control & UINT32_C(0x00000700)) | UINT32_C(0x05FA0004);
    OPEN_CFW_PT_SYSTEM_RESET_BARRIER();
    OPEN_CFW_PT_SYSTEM_RESET_WAIT();
}


void open_cfw_pt_display_buffer_write(void *destination, uintptr_t source,
                                      uint32_t length)
{
    uint8_t *output = destination;
    const uint8_t *input = (const uint8_t *)source;
    uint32_t index;
    if (output == NULL || input == NULL || length == 0U) return;
    if ((uintptr_t)output <= source ||
            (uintptr_t)output - source >= (uintptr_t)length) {
        for (index = 0U; index < length; ++index) output[index] = input[index];
    } else {
        for (index = length; index != 0U; --index)
            output[index - 1U] = input[index - 1U];
    }
}


void *open_cfw_pt_lens_sync_allocate(uint32_t size)
{
    void *allocation = NULL;
    uint32_t delay = 1U;
    uint32_t attempt;
    for (attempt = 0U; attempt < 10U; ++attempt) {
        allocation = OPEN_CFW_PT_FILE_HEAP_ALLOCATE(size);
        if (allocation != NULL) break;
        (void)OPEN_CFW_PT_DELAY_TICKS(delay);
        delay <<= 1U;
    }
    return allocation;
}


void open_cfw_pt_input_message_send(const void *message)
{
    void *queue;
    void *thread;
    if (message == NULL) return;
    queue = *OPEN_CFW_PT_INPUT_QUEUE_LINK;
    thread = *OPEN_CFW_PT_INPUT_THREAD_LINK;
    if (queue != NULL && OPEN_CFW_PT_QUEUE_SEND(
            queue, message, 0U, 0U) == 0 && thread != NULL)
        (void)OPEN_CFW_PT_THREAD_FLAGS_SET(thread, UINT32_C(0x00400000));
}


static void open_cfw_pt_audio_enable_send(uint32_t type, uint32_t enabled)
{
    uint32_t message[4] = {type, 1U, enabled & UINT32_C(0xFF), 0U};
    void *queue = *OPEN_CFW_PT_AUDIO_QUEUE_LINK;
    void *thread = *OPEN_CFW_PT_AUDIO_THREAD_LINK;
    if (queue != NULL && OPEN_CFW_PT_QUEUE_SEND(
            queue, message, 0U, 0U) == 0 && thread != NULL)
        (void)OPEN_CFW_PT_THREAD_FLAGS_SET(thread, UINT32_C(0x00400000));
}


void open_cfw_pt_codec_mic_enable(uint32_t enabled)
{
    open_cfw_pt_audio_enable_send(0U, enabled);
}


void open_cfw_pt_pdm_mic_enable(uint32_t enabled)
{
    open_cfw_pt_audio_enable_send(1U, enabled);
}


struct open_cfw_pt_audio_registration {
    uint32_t listener;
    uint8_t mode;
    uint8_t reserved[3];
    const void *callback;
};


struct open_cfw_pt_audio_recorder {
    void *file;
    uint32_t byte_count;
    uint16_t identifier;
    uint8_t active;
    uint8_t initialized;
};


static void open_cfw_pt_zero_bytes(volatile void *destination, uint32_t length)
{
    volatile uint8_t *bytes = destination;
    uint32_t index;
    for (index = 0U; index < length; ++index) bytes[index] = 0U;
}


static void open_cfw_pt_path_append(char *path, uint32_t capacity,
                                    uint32_t *length, const char *text)
{
    if (text == NULL) return;
    while (*text != '\0') {
        if (*length + 1U < capacity) path[*length] = *text;
        ++*length;
        ++text;
    }
}


static uint32_t open_cfw_pt_divide_by_10(uint32_t value,
                                        uint32_t *remainder)
{
    uint32_t quotient = (value >> 1U) + (value >> 2U);
    uint32_t rest;
    quotient += quotient >> 4U;
    quotient += quotient >> 8U;
    quotient += quotient >> 16U;
    quotient >>= 3U;
    rest = value - quotient * 10U;
    if (rest > 9U) {
        ++quotient;
        rest -= 10U;
    }
    *remainder = rest;
    return quotient;
}


void open_cfw_pt_audio_path_format_provider(uint8_t selector,
                                            uint16_t identifier,
                                            char *path, uint32_t capacity)
{
    char digits[5];
    uint32_t count = 0U;
    uint32_t length = 0U;
    uint32_t value = identifier;
    const char *name;
    if (path == NULL || capacity == 0U || selector >= 2U) return;
    name = OPEN_CFW_PT_AUDIO_NAME_TABLE[selector];
    open_cfw_pt_path_append(path, capacity, &length, "/audio/");
    open_cfw_pt_path_append(path, capacity, &length, name);
    open_cfw_pt_path_append(path, capacity, &length, "_");
    do {
        uint32_t remainder;
        value = open_cfw_pt_divide_by_10(value, &remainder);
        digits[count++] = (char)('0' + remainder);
    } while (value != 0U && count < sizeof(digits));
    while (count < 2U) digits[count++] = '0';
    while (count != 0U) {
        char digit[2] = {digits[--count], '\0'};
        open_cfw_pt_path_append(path, capacity, &length, digit);
    }
    open_cfw_pt_path_append(path, capacity, &length, ".pcm");
    path[length < capacity ? length : capacity - 1U] = '\0';
}


void open_cfw_pt_audio_register(uint32_t listener, uint32_t mode,
                                const void *callback)
{
    volatile struct open_cfw_pt_audio_registration *entry;
    if (mode >= 2U || callback == NULL) return;
    entry = &OPEN_CFW_PT_AUDIO_REGISTRATION_TABLE[mode];
    if (entry->callback != NULL)
        open_cfw_pt_zero_bytes(entry, sizeof(*entry));
    entry->listener = listener;
    entry->mode = (uint8_t)mode;
    entry->callback = callback;
}


int open_cfw_pt_audio_remove(uint32_t listener, uint32_t mode)
{
    volatile struct open_cfw_pt_audio_registration *entry;
    if (mode >= 2U) return -1;
    entry = &OPEN_CFW_PT_AUDIO_REGISTRATION_TABLE[mode];
    if (entry->callback == NULL) return 0;
    if (entry->listener != listener) return -1;
    open_cfw_pt_zero_bytes(entry, sizeof(*entry));
    return 0;
}


void open_cfw_pt_audio_unregister(uint32_t mode)
{
    volatile struct open_cfw_pt_audio_recorder *entry;
    if (mode >= 2U) return;
    entry = &OPEN_CFW_PT_AUDIO_RECORDER_TABLE[mode];
    if (entry->file != NULL) {
        (void)OPEN_CFW_PT_FILE_CLOSE(entry->file);
        entry->file = NULL;
    }
    entry->active = 0U;
}


struct open_cfw_pt_ambient_field {
    uint8_t most_significant_bit;
    uint8_t least_significant_bit;
    uint8_t register_address;
};


uint32_t open_cfw_pt_ambient_raw_read(uint32_t register_address)
{
    uint8_t address = (uint8_t)register_address;
    uint8_t bytes[2] = {0U, 0U};
    (void)OPEN_CFW_PT_AMBIENT_BUS_READ(
        2U, UINT32_C(0x45), &address, 1U, bytes, sizeof(bytes));
    return ((uint32_t)bytes[0] << 8U) | bytes[1];
}


static void open_cfw_pt_ambient_raw_write(uint32_t register_address,
                                          uint16_t value)
{
    uint8_t address = (uint8_t)register_address;
    uint8_t bytes[2] = {(uint8_t)(value >> 8U), (uint8_t)value};
    (void)OPEN_CFW_PT_AMBIENT_BUS_WRITE(
        2U, UINT32_C(0x45), &address, 1U, bytes, sizeof(bytes));
}


void open_cfw_pt_ambient_assign(void *field_pointer, uint32_t value)
{
    const struct open_cfw_pt_ambient_field *field = field_pointer;
    uint32_t width;
    uint32_t mask;
    uint16_t current;
    uint16_t updated;
    if (field == NULL || field->most_significant_bit > 15U ||
            field->least_significant_bit > field->most_significant_bit)
        return;
    width = (uint32_t)field->most_significant_bit -
        field->least_significant_bit + 1U;
    mask = (width == 16U ? UINT32_C(0xFFFF) :
            (UINT32_C(1) << width) - 1U) << field->least_significant_bit;
    current = (uint16_t)open_cfw_pt_ambient_raw_read(
        field->register_address);
    updated = (uint16_t)(((uint32_t)current & ~mask) |
        ((value << field->least_significant_bit) & mask));
    if (updated != current)
        open_cfw_pt_ambient_raw_write(field->register_address, updated);
}


uint16_t open_cfw_pt_ambient_sample(void *field_pointer)
{
    const struct open_cfw_pt_ambient_field *field = field_pointer;
    if (field == NULL) return 0U;
    return (uint16_t)open_cfw_pt_ambient_raw_read(field->register_address);
}


void open_cfw_pt_font_xip_acquire(void)
{
    void *mutex = *OPEN_CFW_PT_FONT_XIP_MUTEX_LINK;
    void *device = *OPEN_CFW_PT_FONT_XIP_DEVICE_LINK;
    if (mutex != NULL)
        (void)OPEN_CFW_PT_MUTEX_ACQUIRE(mutex, UINT32_MAX);
    if (*OPEN_CFW_PT_FONT_XIP_CONFIGURATION_FLAG != 1U && device != NULL) {
        (void)OPEN_CFW_PT_MSPI_CONTROL(device, 0U, 1U);
        *OPEN_CFW_PT_FONT_XIP_ACTIVE = 0U;
    }
}


void open_cfw_pt_font_xip_release(void)
{
    void *mutex = *OPEN_CFW_PT_FONT_XIP_MUTEX_LINK;
    void *device = *OPEN_CFW_PT_FONT_XIP_DEVICE_LINK;
    if (*OPEN_CFW_PT_FONT_XIP_CONFIGURATION_FLAG != 1U && device != NULL &&
            *OPEN_CFW_PT_FONT_XIP_ACTIVE != 1U) {
        (void)OPEN_CFW_PT_MSPI_CONTROL(device, 2U, 1U);
        *OPEN_CFW_PT_FONT_XIP_ACTIVE = 1U;
    }
    if (mutex != NULL) (void)OPEN_CFW_PT_MUTEX_RELEASE(mutex);
}


void open_cfw_pt_display_postprocess_commit(void)
{
    OPEN_CFW_PT_MRAM_DELETE_ALL_RECORDS();
    OPEN_CFW_PT_PRIVACY_CLEAR();
    *OPEN_CFW_PT_PAIRING_FLAG_0 = 0U;
    *OPEN_CFW_PT_PAIRING_WORD = 0U;
    *OPEN_CFW_PT_PAIRING_FLAG_1 = 0U;
}


const uint8_t *open_cfw_pt_board_display_state(void)
{
    return OPEN_CFW_PT_DISPLAY_STATE;
}


uint32_t open_cfw_pt_board_codec_platform_identifier(void)
{
    return *OPEN_CFW_PT_CODEC_IDENTIFIER_WORD;
}


void open_cfw_pt_board_buzzer_start(uint32_t frequency_hz,
                                    uint8_t duty_percent)
{
    OPEN_CFW_PT_BUZZER_PREPARE();
    OPEN_CFW_PT_AUDIO_CODEC_ROUTE(0x91U, *OPEN_CFW_PT_BUZZER_ROUTE_WORD);
    OPEN_CFW_PT_BUZZER_APPLY(frequency_hz, duty_percent);
}


void open_cfw_pt_board_buzzer_stop(void)
{
    OPEN_CFW_PT_BUZZER_DISABLE(1U);
}


int open_cfw_pt_board_hardware_identifier_0(uint32_t *value)
{
    uint32_t record[16];
    if (value == NULL) return -1;
    OPEN_CFW_PT_HARDWARE_IDENTIFIER_READ(1U, record);
    *value = record[0];
    return 0;
}


int open_cfw_pt_board_hardware_identifier_1(uint32_t *value)
{
    uint32_t identifier = 0U;
    int result;
    if (value == NULL) return -1;
    if (*OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_STATE == 0U &&
        OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_INITIALIZE() != 0)
        return -3;
    OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_ACQUIRE();
    OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_PREPARE();
    result = OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_READ(&identifier);
    OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_FINISH();
    OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_RELEASE();
    if (result != 0) return -2;
    *value = identifier & 0x00FFFFFFU;
    return 0;
}


int open_cfw_pt_board_hardware_identifier_2(uint32_t *value)
{
    uint8_t identifier = 0U;
    int32_t result;
    if (value == NULL) return -1;
    result = OPEN_CFW_PT_HARDWARE_IDENTIFIER_2_READ(
        OPEN_CFW_PT_HARDWARE_IDENTIFIER_2_DEVICE, 0x101U, &identifier, 1U);
    if (result != OPEN_CFW_PT_PLATFORM_SUCCESS) return -2;
    if (identifier == 0U || identifier == 0xFFU) identifier = 0x13U;
    *value = identifier;
    return 0;
}


void open_cfw_pt_board_charger_test_disable(void)
{
    void *device = OPEN_CFW_PT_CHARGER_OPEN(OPEN_CFW_PT_CHARGER_DEVICE, 0U);
    if (device != NULL)
        (void)OPEN_CFW_PT_CHARGER_DISABLE(device, 0x0FU);
}


void open_cfw_pt_board_charger_test_enable(void)
{
    void *device = OPEN_CFW_PT_CHARGER_OPEN(OPEN_CFW_PT_CHARGER_DEVICE, 0U);
    if (device != NULL)
        (void)OPEN_CFW_PT_CHARGER_ENABLE(device, 0x0FU);
}


int open_cfw_pt_board_uart_sync_write(const uint8_t *data, uint32_t length,
                                      uint32_t timeout)
{
    return OPEN_CFW_PT_UART_WRITE(data, length, timeout) == 0 ? 0 : -1;
}


const uint8_t *open_cfw_pt_board_audio_status_get(uint32_t index)
{
    if (index > 2U) index = 0U;
    return OPEN_CFW_PT_AUDIO_STATUS_BASE + index;
}


void open_cfw_pt_board_audio_codec_route(uint32_t code, uint32_t enabled)
{
    (void)OPEN_CFW_PT_CODEC_ROUTE_SET(code, enabled == 1U ? 1U : 0U);
}


void open_cfw_pt_board_audio_channel_0_start(uint8_t selector)
{
    *OPEN_CFW_PT_AUDIO_CAPTURE_ACTIVE = 0U;
    if (selector == 0U) {
        OPEN_CFW_PT_AUDIO_REGISTER(
            0x10BU, 0U, OPEN_CFW_PT_AUDIO_SINGLE_CALLBACK);
    } else if (selector == 1U) {
        OPEN_CFW_PT_AUDIO_REGISTER(
            0x10BU, 0U, OPEN_CFW_PT_AUDIO_STEREO_CALLBACK);
    }
    OPEN_CFW_PT_CODEC_MIC_ENABLE(1U);
    OPEN_CFW_PT_PCM_ROUTE(0U);
}


void open_cfw_pt_board_audio_channel_1_start(void)
{
    int result;
    OPEN_CFW_PT_CODEC_MIC_ENABLE(0U);
    result = OPEN_CFW_PT_AUDIO_REMOVE(0x10BU, 0U);
    if (result == 0) {
        OPEN_CFW_PT_AUDIO_UNREGISTER(0U);
        OPEN_CFW_PT_AUDIO_RELEASE(OPEN_CFW_PT_AUDIO_CODEC_BUFFER_0);
        OPEN_CFW_PT_AUDIO_RELEASE(OPEN_CFW_PT_AUDIO_CODEC_BUFFER_1);
    }
}


void open_cfw_pt_board_audio_channel_0_stop(void)
{
    OPEN_CFW_PT_AUDIO_REGISTER(
        0x10BU, 1U, OPEN_CFW_PT_AUDIO_SINGLE_CALLBACK);
    OPEN_CFW_PT_PDM_MIC_ENABLE(1U);
    OPEN_CFW_PT_PCM_ROUTE(1U);
}


void open_cfw_pt_board_audio_channel_1_stop(void)
{
    int result;
    OPEN_CFW_PT_PDM_MIC_ENABLE(0U);
    result = OPEN_CFW_PT_AUDIO_REMOVE(0x10BU, 1U);
    if (result == 0) {
        OPEN_CFW_PT_AUDIO_UNREGISTER(1U);
        OPEN_CFW_PT_AUDIO_RELEASE(OPEN_CFW_PT_AUDIO_PDM_BUFFER);
    }
}


static void apply_display_state(void)
{
    OPEN_CFW_PT_DISPLAY_REINITIALIZE();
    OPEN_CFW_PT_DISPLAY_APPLY(0U, 0U, 0U, 0U, 0x240U, 0x120U);
}


void open_cfw_pt_board_display_stage_1(uint32_t value)
{
    *OPEN_CFW_PT_DISPLAY_STAGE_1_WORD = value;
    apply_display_state();
}


void open_cfw_pt_board_display_stage_2(uint32_t first, uint32_t second)
{
    if (first >= 0x31U || second >= 0x41U) return;
    *OPEN_CFW_PT_DISPLAY_STAGE_2_FIRST_WORD = first;
    *OPEN_CFW_PT_DISPLAY_STAGE_2_SECOND_WORD = second;
    apply_display_state();
}


void open_cfw_pt_board_display_stage_3(uint32_t value)
{
    *OPEN_CFW_PT_DISPLAY_STAGE_3_WORD = value;
    apply_display_state();
}


uint32_t open_cfw_pt_board_display_hardware_identifier(void)
{
    const struct open_cfw_pt_uled_operations *operations =
        *OPEN_CFW_PT_ULED_OPERATIONS_LINK;
    uint16_t identifier = 0U;
    if (operations == NULL) return 0xFFFFU;
    (void)operations->read_chip_id(&identifier);
    return identifier;
}


void open_cfw_pt_board_display_brightness(uint32_t delay, uint32_t period,
                                          uint32_t brightness)
{
    const struct open_cfw_pt_uled_operations *operations =
        *OPEN_CFW_PT_ULED_OPERATIONS_LINK;
    if (operations != NULL)
        (void)operations->set_brightness(delay, period, brightness);
}


void open_cfw_pt_board_display_offset(uint8_t first, uint8_t second)
{
    const struct open_cfw_pt_uled_operations *operations =
        *OPEN_CFW_PT_ULED_OPERATIONS_LINK;
    if (operations != NULL)
        (void)operations->set_display_offset(first, second);
}


struct open_cfw_pt_display_message {
    uint8_t operation;
    uint8_t reserved[3];
    uint32_t screen_id;
    uint32_t length;
};


static int submit_screen_message(uint8_t operation, uint16_t screen_id,
                                 uint32_t source, uint32_t length)
{
    struct open_cfw_pt_display_message message = {0U, {0U, 0U, 0U}, 0U, 0U};
    void *mutex;
    void *queue;
    if (length > 0x2800U) return -1;
    mutex = *OPEN_CFW_PT_DISPLAY_MUTEX_LINK;
    queue = *OPEN_CFW_PT_DISPLAY_QUEUE_LINK;
    if (mutex == NULL || queue == NULL) return -1;
    message.operation = operation;
    message.screen_id = screen_id;
    message.length = length;
    if (OPEN_CFW_PT_MUTEX_ACQUIRE(mutex, 0xFFFFFFFFU) != 0) return -1;
    OPEN_CFW_PT_DISPLAY_BUFFER_WRITE(
        OPEN_CFW_PT_DISPLAY_BUFFER, (uintptr_t)source, length);
    (void)OPEN_CFW_PT_MUTEX_RELEASE(mutex);
    if (OPEN_CFW_PT_QUEUE_SEND(queue, &message, 0U, 1000U) != 0) {
        OPEN_CFW_PT_FAIL_STOP();
        return -1;
    }
    return 0;
}


void open_cfw_pt_board_screen_show(uint16_t screen_id, uint32_t argument1,
                                   uint32_t argument2)
{
    (void)submit_screen_message(2U, screen_id, argument1, argument2);
}


void open_cfw_pt_board_screen_hide(uint16_t screen_id, uint32_t argument1,
                                   uint32_t argument2)
{
    (void)submit_screen_message(5U, screen_id, argument1, argument2);
}


struct open_cfw_pt_lens_sync_message {
    uint32_t user_data;
    uint16_t type;
    uint16_t payload_length;
    uint8_t *payload;
};


int open_cfw_pt_board_lens_sync_send(uint32_t service, const void *payload,
                                     uint32_t length, uint32_t user_data)
{
    struct open_cfw_pt_lens_sync_message *message;
    uint8_t *wire;
    uint32_t index;
    uint16_t bounded_length;
    void *queue;
    if (service > UINT16_MAX || length > 0xFFF7U ||
        (payload == NULL && length != 0U))
        return -1;
    bounded_length = (uint16_t)length;
    queue = *OPEN_CFW_PT_LENS_SYNC_QUEUE_LINK;
    if (queue == NULL) return -1;
    message = OPEN_CFW_PT_LENS_SYNC_ALLOCATE(sizeof(*message));
    if (message == NULL) return -1;
    message->user_data = user_data;
    message->type = 4U;
    message->payload_length = (uint16_t)(bounded_length + 8U);
    message->payload = OPEN_CFW_PT_LENS_SYNC_ALLOCATE(
        (uint32_t)bounded_length + 8U);
    if (message->payload == NULL) {
        OPEN_CFW_PT_LENS_SYNC_RELEASE(message);
        return -1;
    }
    wire = message->payload;
    wire[0] = 4U;
    wire[1] = 0x0CU;
    wire[2] = (uint8_t)service;
    wire[3] = (uint8_t)(service >> 8U);
    wire[4] = 0U;
    wire[5] = 0U;
    wire[6] = (uint8_t)bounded_length;
    wire[7] = (uint8_t)(bounded_length >> 8U);
    for (index = 0U; index < bounded_length; ++index)
        wire[index + 8U] = ((const uint8_t *)payload)[index];
    if (OPEN_CFW_PT_QUEUE_SEND(queue, &message, 0U, 2000U) != 0) {
        OPEN_CFW_PT_LENS_SYNC_RELEASE(message->payload);
        OPEN_CFW_PT_LENS_SYNC_RELEASE(message);
        return -1;
    }
    (void)OPEN_CFW_PT_EVENT_FLAGS_SET(
        *OPEN_CFW_PT_LENS_SYNC_EVENT_LINK, 2U);
    return 0;
}


void open_cfw_pt_board_audio_path_format(uint8_t selector, char *path,
                                         uint32_t capacity)
{
    const uint8_t *entry;
    uint16_t identifier;
    if (selector >= 2U) return;
    entry = OPEN_CFW_PT_AUDIO_PATH_TABLE + (uint32_t)selector * 12U;
    identifier = (uint16_t)entry[8] | ((uint16_t)entry[9] << 8U);
    OPEN_CFW_PT_AUDIO_PATH_FORMAT_PROVIDER(
        selector, identifier, path, capacity);
}


void open_cfw_pt_board_time_capture(void *time_record_40)
{
    uint8_t current[40];
    const uint8_t *configuration;
    int32_t seconds;
    int32_t timezone_seconds;
    OPEN_CFW_PT_TIME_READ(current);
    seconds = OPEN_CFW_PT_TIME_TO_SECONDS(current);
    configuration = *OPEN_CFW_PT_TIME_CONFIGURATION_LINK;
    timezone_seconds = (int32_t)(int8_t)configuration[8] * 900;
    OPEN_CFW_PT_TIME_OUTPUT(seconds + timezone_seconds, time_record_40);
}


void open_cfw_pt_board_time_configure(uint32_t seconds, int timezone)
{
    uint8_t record[40];
    unsigned int index;
    (void)timezone;
    OPEN_CFW_PT_SECONDS_TO_TIME(seconds, record);
    OPEN_CFW_PT_RTC_SET_TIME(record);
    for (index = 0U; index < sizeof(record); ++index) record[index] = 0U;
    open_cfw_pt_board_time_capture(record);
}


void open_cfw_pt_board_post_input_message_id3(void)
{
    uint32_t message[3] = {3U, 0U, 0U};
    OPEN_CFW_PT_INPUT_MESSAGE_SEND(message);
}


void open_cfw_pt_board_ambient_identifier_initialize(void)
{
    OPEN_CFW_PT_AUDIO_CODEC_ROUTE(0x86U, *OPEN_CFW_PT_AMBIENT_ROUTE_WORD);
    *OPEN_CFW_PT_AMBIENT_INIT_REGISTER = 0x40U;
    (void)OPEN_CFW_PT_DELAY_TICKS(10U);
}


void open_cfw_pt_board_ambient_identifier_step_1(void *device)
{
    OPEN_CFW_PT_AMBIENT_ASSIGN((uint8_t *)device + 12U, 3U);
}


void open_cfw_pt_board_ambient_identifier_step_2(void *device)
{
    OPEN_CFW_PT_AMBIENT_ASSIGN((uint8_t *)device + 9U, 0U);
}


static double positive_u32_to_double(uint32_t value)
{
    union {
        uint32_t words[2];
        double value;
    } result;
    uint32_t normalized;
    uint32_t exponent = 0U;
    uint32_t remainder;
    uint32_t shift;
    if (value == 0U) return 0.0;
    normalized = value;
    while (normalized > 1U) {
        normalized >>= 1U;
        ++exponent;
    }
    remainder = value - (1U << exponent);
    shift = 52U - exponent;
    result.words[0] = 0U;
    result.words[1] = (exponent + 1023U) << 20U;
    if (shift >= 32U) {
        result.words[1] |= remainder << (shift - 32U);
    } else {
        result.words[0] = remainder << shift;
        result.words[1] |= remainder >> (32U - shift);
    }
    return result.value;
}


uint16_t open_cfw_pt_board_ambient_identifier_low(void *device)
{
    return OPEN_CFW_PT_AMBIENT_SAMPLE((uint8_t *)device + 0x33U);
}


uint16_t open_cfw_pt_board_ambient_identifier_high(void *device)
{
    return OPEN_CFW_PT_AMBIENT_SAMPLE((uint8_t *)device + 0x36U);
}


double open_cfw_pt_board_ambient_read(void)
{
    uint32_t encoded;
    uint32_t mantissa;
    uint32_t exponent;
    if (OPEN_CFW_PT_LENS_SIDE() != 1U) return -1.0;
    encoded = OPEN_CFW_PT_AMBIENT_RAW_READ(0U);
    mantissa = encoded & 0x0FFFU;
    exponent = (encoded >> 12U) & 0x0FU;
    return positive_u32_to_double(mantissa * (1U << exponent));
}


void open_cfw_pt_board_production_reset(void)
{
    OPEN_CFW_PT_AUDIO_CODEC_ROUTE(0x86U, *OPEN_CFW_PT_AMBIENT_ROUTE_WORD);
    *OPEN_CFW_PT_AMBIENT_RESET_REGISTER = 0x40U;
}


void open_cfw_pt_board_system_reset(void)
{
    OPEN_CFW_PT_SYSTEM_RESET_INNER();
}


void open_cfw_pt_board_display_postprocess(void)
{
    uint8_t side = OPEN_CFW_PT_LENS_SIDE();
    uint8_t enabled = 1U;
    if (OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_0() == 1U) {
        if (OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_1() == 1U) {
            if (side == 1U)
                OPEN_CFW_PT_DISPLAY_POSTPROCESS_SEND(0U, 0U, 0U, 0U);
            (void)OPEN_CFW_PT_DELAY_TICKS(500U);
        }
        if (OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_2() == 1U) {
            if (side == 1U)
                OPEN_CFW_PT_DISPLAY_POSTPROCESS_SEND(0U, 0U, 0U, 0U);
            (void)OPEN_CFW_PT_DELAY_TICKS(500U);
        }
    }
    OPEN_CFW_PT_DISPLAY_POSTPROCESS_REFRESH();
    (void)OPEN_CFW_PT_DISPLAY_POSTPROCESS_ONBOARDING(0U, &enabled);
    (void)OPEN_CFW_PT_DISPLAY_POSTPROCESS_REMOVE(
        OPEN_CFW_PT_DISPLAY_POSTPROCESS_PATH);
    OPEN_CFW_PT_DISPLAY_POSTPROCESS_COMMIT();
}


static uint16_t open_cfw_pt_font_crc16_update(const uint8_t *data,
                                               uint32_t length,
                                               uint16_t crc)
{
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        uint32_t bit;
        crc ^= (uint16_t)((uint16_t)data[index] << 8U);
        for (bit = 0U; bit < 8U; ++bit)
            crc = (uint16_t)((crc & UINT16_C(0x8000)) != 0U
                ? (uint16_t)((uint16_t)(crc << 1U) ^ UINT16_C(0x1021))
                : (uint16_t)(crc << 1U));
    }
    return crc;
}


uint8_t open_cfw_pt_font_crc_validate(uint32_t base)
{
    enum {
        OPEN_CFW_PT_FONT_HEADER_BYTES = 0x46,
        OPEN_CFW_PT_FONT_LENGTH_OFFSET = 0x40,
        OPEN_CFW_PT_FONT_CRC_OFFSET = 0x44,
        OPEN_CFW_PT_FONT_PAYLOAD_OFFSET = 0x45,
        OPEN_CFW_PT_FONT_CHUNK_BYTES = 0x400
    };
    uint8_t header[OPEN_CFW_PT_FONT_HEADER_BYTES];
    uint8_t chunk[OPEN_CFW_PT_FONT_CHUNK_BYTES];
    uint32_t length;
    uint32_t address;
    uint16_t expected;
    uint16_t crc = UINT16_C(0xFFFF);

    if (base < OPEN_CFW_PT_FONT_XIP_START ||
            base > OPEN_CFW_PT_FONT_XIP_END - OPEN_CFW_PT_FONT_HEADER_BYTES)
        return 1U;

    OPEN_CFW_PT_FONT_XIP_READ(base, header, sizeof(header));
    length = (uint32_t)header[OPEN_CFW_PT_FONT_LENGTH_OFFSET] |
        ((uint32_t)header[OPEN_CFW_PT_FONT_LENGTH_OFFSET + 1U] << 8U) |
        ((uint32_t)header[OPEN_CFW_PT_FONT_LENGTH_OFFSET + 2U] << 16U) |
        ((uint32_t)header[OPEN_CFW_PT_FONT_LENGTH_OFFSET + 3U] << 24U);
    expected = (uint16_t)((uint16_t)header[OPEN_CFW_PT_FONT_CRC_OFFSET] |
        ((uint16_t)header[OPEN_CFW_PT_FONT_CRC_OFFSET + 1U] << 8U));

    if (length == 0U ||
            length > OPEN_CFW_PT_FONT_XIP_END - base -
                OPEN_CFW_PT_FONT_PAYLOAD_OFFSET)
        return 1U;

    address = base + OPEN_CFW_PT_FONT_PAYLOAD_OFFSET;
    while (length != 0U) {
        uint32_t count = length;
        if (count > OPEN_CFW_PT_FONT_CHUNK_BYTES)
            count = OPEN_CFW_PT_FONT_CHUNK_BYTES;
        OPEN_CFW_PT_FONT_XIP_READ(address, chunk, count);
        crc = open_cfw_pt_font_crc16_update(chunk, count, crc);
        address += count;
        length -= count;
    }
    return crc == expected ? 0U : 1U;
}


uint8_t open_cfw_pt_board_font_crc_check_0(void)
{
    return open_cfw_pt_font_crc_validate(OPEN_CFW_PT_FONT_0_BASE);
}


uint8_t open_cfw_pt_board_font_crc_check_1(void)
{
    return open_cfw_pt_font_crc_validate(OPEN_CFW_PT_FONT_1_BASE);
}
