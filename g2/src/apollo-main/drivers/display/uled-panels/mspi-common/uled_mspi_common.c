/* uLED MSPI common layer, stock
 * D:\01_workspace\s200_ap510b_iar_git\driver\uled\drv_mspi_uled_common.c.
 * Native 0x59c820..0x59c875 (NVIC helpers, transfer callback) and
 * 0x59cd86..0x59ce1d (blocking QSPI write); literal pool 0x59d158..0x59d1f4.
 *
 * am_devices_mspi_init (0x59cf1a) opens MSPI instance 0, sets the MSPI0 IRQ
 * (20) priority to 4 and enables it with the two helpers below. The serial and
 * quad device configurations it publishes at RAM 0x20074538 / 0x2007453c are
 * swapped in around every QSPI data phase. */
#include <stdint.h>
#include <stddef.h>
#include "../uled_mspi_request.h"

extern void *g2_uled_mspi_semaphore;               /* RAM 0x20074534, binary semaphore */
extern const void *g2_uled_mspi_serial_config;     /* RAM 0x20074538 */
extern const void *g2_uled_mspi_quad_config;       /* RAM 0x2007453c */

extern int32_t osSemaphoreRelease(void *semaphore);
extern void audio_uart_lv_memzero_48949c(void *dst, uint32_t len);
extern uint32_t display_driver_uled_packet_validate_59cb42(const void *request, const char *caller); /* uled_rw_param_validate */
extern void display_driver_uled_quad_mode_59ca2c(const void *config, uint32_t handle);   /* am_devices_mspi_set_quad_mode */
extern void display_driver_uled_serial_mode_59c980(const void *config, uint32_t handle); /* am_devices_mspi_set_serail_mode */
extern void display_driver_uled_packet_encode_59cafc(const void *request, void *pio, uint32_t direction); /* mspi_transfer_build */
extern uint32_t g2_norflash_transfer_4c2098(uint32_t handle, const uint8_t *pio, uint32_t timeout); /* am_hal_mspi_blocking_transfer */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

#define NVIC_ISER ((volatile uint32_t *)0xe000e100u)
#define NVIC_IPR  ((volatile uint8_t *)0xe000e400u)
#define SCB_SHPR  ((volatile uint8_t *)0xe000ed18u)
#define MSPI_DIR_TX 1u
#define MSPI_BLOCKING_TIMEOUT 1000000u

static const char module_tag[] = "driver.uled_common"; /* ROM 0x77f0a4 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\drv_mspi_uled_common.c"; /* ROM 0x6f9fd4 */
static const char qspi_write_fn[] = "am_devices_mspi_qspi_write"; /* ROM 0x76b308 */
static const char blocking_failed[] = "blocking transfer failed.\n"; /* ROM 0x76b324 */
static const char blocking_failed_short[] = "[driver.uled_common]blocking transfer failed.\n"; /* ROM 0x733824 */

void NVIC_EnableIRQ(int16_t irq)
{
    if (irq >= 0)
        NVIC_ISER[(uint32_t)irq >> 5] = 1u << ((uint32_t)irq & 31u);
}

/* Four implemented priority bits (priority << 4). Negative numbers address
 * the SCB system-handler priority bytes. */
__attribute__((used)) static void NVIC_SetPriority(int16_t irq, uint32_t priority)
{
    if (irq >= 0)
        NVIC_IPR[irq] = (uint8_t)(priority << 4);
    else
        SCB_SHPR[((uint32_t)irq & 15u) - 4u] = (uint8_t)(priority << 4);
}

/* am_hal_mspi non-blocking completion: store the HAL status for the waiter and
 * wake it. */
void mspi_transfer_callback(void *context, uint32_t status)
{
    *(uint32_t *)context = status;
    (void)osSemaphoreRelease(g2_uled_mspi_semaphore);
}

/* Blocking write in quad mode: reconfigure the device to QSPI, run one PIO
 * transfer, then drop back to serial mode whatever the result. */
uint32_t am_devices_mspi_qspi_write(g2_uled_mspi_request_t *request)
{
    uint8_t pio[24];
    uint32_t status;

    audio_uart_lv_memzero_48949c(pio, sizeof pio);
    status = display_driver_uled_packet_validate_59cb42(request, qspi_write_fn);
    if (status != 0u)
        return status;
    display_driver_uled_quad_mode_59ca2c(g2_uled_mspi_quad_config, (uint32_t)(uintptr_t)request->handle);
    display_driver_uled_packet_encode_59cafc(request, pio, MSPI_DIR_TX);
    status = g2_norflash_transfer_4c2098((uint32_t)(uintptr_t)request->handle, pio, MSPI_BLOCKING_TIMEOUT);
    if (status != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, qspi_write_fn, 0xfdu, blocking_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, blocking_failed_short, blocking_failed_short);
    }
    display_driver_uled_serial_mode_59c980(g2_uled_mspi_serial_config, (uint32_t)(uintptr_t)request->handle);
    return status;
}
