/* Image-B native 0x1000c0bc..0x1000c1a7, I2S output sample-app init.
 * The two called sample-app descendants remain separate real contracts. */
#include <stdint.h>

extern uint32_t gx8002_image_b_audio_out_init_10006c08(uint32_t);
extern uint32_t gx8002_image_b_audio_out_alloc_10006a88(uint32_t);
extern uint32_t gx8002_image_b_audio_out_config_cb_10006b28(
    uint32_t,uint32_t);
extern uint32_t gx8002_image_b_audio_out_set_db_10006b98(
    uint32_t,int32_t);
extern uint32_t gx8002_image_b_audio_out_set_channel_10006bd0(
    uint32_t,uint32_t);
extern uint32_t gx8002_image_b_audio_out_config_buffer_10006abc(
    uint32_t,uint32_t);
extern uint32_t gx8002_image_b_audio_out_config_pcm_10006af0(
    uint32_t,uint32_t);
extern uint32_t gx8002_image_b_audio_state_word_54_10009e24(void);
extern uint32_t gx8002_image_b_audio_state_word_50_10009e18(void);
extern uint32_t gx8002_image_b_clock_frequency_10003cf0(uint32_t);
extern uint32_t gx8002_image_b_spi_pin_mode_10008154(uint32_t,uint32_t);
extern int gx8002_image_b_heap_log_10009934(const char *,...);
extern void gx8002_image_b_sample_app_audio_callback_1000bef4(void);
extern void gx8002_image_b_sample_app_begin_1000c404(void);

int gx8002_image_b_sample_app_init_1000c0bc(void)
{
    volatile uint32_t *const handle_slot =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002d798);
    volatile uint32_t *const sample_state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002d360);
    (void)gx8002_image_b_audio_out_init_10006c08(0u);
    (void)gx8002_image_b_clock_frequency_10003cf0(11u);
    uint32_t handle = gx8002_image_b_audio_out_alloc_10006a88(0u);
    *handle_slot = handle;
    uint32_t callbacks[2] = {
        (uint32_t)(uintptr_t)gx8002_image_b_sample_app_audio_callback_1000bef4,
        0u,
    };
    (void)gx8002_image_b_audio_out_config_cb_10006b28(
        handle,(uint32_t)(uintptr_t)callbacks);
    (void)gx8002_image_b_audio_out_set_db_10006b98(handle,0);

    uint32_t first = gx8002_image_b_audio_state_word_54_10009e24();
    uint32_t rounded = first + (first >> 31);
    int32_t half = (int32_t)rounded >> 1;
    sample_state[0x28u / 4u] = (uint32_t)half;
    (void)gx8002_image_b_audio_out_set_channel_10006bd0(handle,0u);
    uint32_t second = gx8002_image_b_audio_state_word_50_10009e18();
    sample_state[0x2cu / 4u] = second;
    uint32_t combined = second + (uint32_t)half;
    sample_state[0x30u / 4u] = combined;
    uint32_t buffer[3] = {second,combined,(uint32_t)half};
    (void)gx8002_image_b_audio_out_config_buffer_10006abc(
        handle,(uint32_t)(uintptr_t)buffer);

    struct {
        uint32_t rate;
        uint8_t channels,bits,reserved0,reserved1;
    } pcm = {16000u,2u,16u,0u,0u};
    (void)gx8002_image_b_audio_out_config_pcm_10006af0(
        handle,(uint32_t)(uintptr_t)&pcm);
    (void)gx8002_image_b_heap_log_10009934(
        "\tMCLK:%dHz\n",gx8002_image_b_clock_frequency_10003cf0(11u));
    (void)gx8002_image_b_heap_log_10009934("\tLRCLK:%dHz\n",pcm.rate);
    (void)gx8002_image_b_heap_log_10009934("\tbits:%d\n",pcm.bits);
    (void)gx8002_image_b_heap_log_10009934(
        "\t%s Init OK\n","I2S out Master");
    const uint32_t pins[] = {8u,9u,10u,11u,0u,1u};
    for (uint32_t i=0;i<6u;++i)
        (void)gx8002_image_b_spi_pin_mode_10008154(pins[i],0u);
    gx8002_image_b_sample_app_begin_1000c404();
    return 0;
}
