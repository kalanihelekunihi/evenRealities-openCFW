/* Native 0x1000c404..0x1000c4df: message UART and five registrations.
 * The event callback at 0x1000c1f8 remains a separate source contract. */
#include <stdint.h>

extern int gx8002_image_b_heap_log_10009934(const char *,...);
extern uint32_t gx8002_image_b_spi_pin_output_100081b8(uint32_t,uint32_t);
extern uint32_t gx8002_image_b_spi_pin_mode_10008154(uint32_t,uint32_t);
extern int32_t gx8002_image_b_audio_uart_shutdown_1000b6f0(void);
extern int32_t gx8002_image_b_audio_uart_open_1000b5f8(const uint32_t *);
extern int32_t gx8002_image_b_audio_registration_table_1000b430(
    const uint8_t *);
extern int gx8002_image_b_sample_app_command_1000c1f8(void *);

static void register_command(uint32_t code,uint32_t destination,
                             uint32_t capacity,const char *name)
{
    uint32_t record[7] = {
        0u,code,destination,capacity,0u,
        (uint32_t)(uintptr_t)gx8002_image_b_sample_app_command_1000c1f8,
        (uint32_t)(uintptr_t)name,
    };
    (void)gx8002_image_b_audio_registration_table_1000b430(
        (const uint8_t *)record);
}

void gx8002_image_b_sample_app_begin_1000c404(void)
{
    (void)gx8002_image_b_heap_log_10009934(
        "[VC_MESSAGE]NOTIFY PIN %d\n",2);
    (void)gx8002_image_b_spi_pin_output_100081b8(2u,1u);
    (void)gx8002_image_b_spi_pin_mode_10008154(2u,1u);
    (void)gx8002_image_b_heap_log_10009934(
        "[VC_MESSAGE]MASSAGE UART %d\n",0);
    (void)gx8002_image_b_heap_log_10009934("[%s]%d\n","_uartMsgInit",316);
    (void)gx8002_image_b_audio_uart_shutdown_1000b6f0();
    uint32_t config[4] = {0u,UINT32_C(0x0001c200),
                          UINT32_C(0x58585542),1u};
    (void)gx8002_image_b_audio_uart_open_1000b5f8(config);
    register_command(368u,0u,0u,"mic status");
    register_command(369u,0u,0u,"gsensor status");
    register_command(258u,0u,0u,"version");
    register_command(264u,0u,0u,"switch wakeup cmd");
    register_command(267u,UINT32_C(0x2002d3c0),32u,"set pga gain");
}
