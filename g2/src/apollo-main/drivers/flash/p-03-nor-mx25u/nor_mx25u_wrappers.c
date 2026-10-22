/* MX25U25643G NOR wrappers, stock D:\01_workspace\s200_ap510b_iar_git\driver\flash\drv_mx25u25643g.c.
 * Native 0x4709c0..0x4709c7 and 0x471020..0x4710a1 (pool 0x4710a4..0x4710af, 0x471160).
 *
 * 0x4709c0 is the public program entry (used by the OTA raw-data parser at 0x446d40)
 * that forwards to the page-program loop at 0x4708a8. 0x471020 issues a single MSPI
 * read with instruction 0x6C (4-byte-address quad-output fast read, 4QOR) for the
 * resource region read at 0x4763b8 (flash offset 0x1400000 + page * 0x1000). */
#include <stdint.h>
#include <stddef.h>

#define NOR_SIZE_BYTES 0x02000000u     /* 32 MiB device */
#define NOR_CMD_4QOR 0x6cu
#define NOR_MSPI_TIMEOUT 1000000u      /* ROM 0x471160 */

enum { NOR_STATUS_OUT_OF_RANGE = 5u, NOR_STATUS_INVALID_ARG = 6u };

/* MSPI PIO transaction as laid out by the stock driver (24 bytes). */
typedef struct {
    uint32_t num_bytes;    /* +0x00 */
    uint8_t reserved4;     /* +0x04 */
    uint8_t reserved5;     /* +0x05 */
    uint8_t reserved6;     /* +0x06 */
    uint8_t send_address;  /* +0x07 */
    uint32_t address;      /* +0x08 */
    uint8_t send_instr;    /* +0x0c */
    uint8_t reserved13;    /* +0x0d */
    uint16_t instr;        /* +0x0e */
    uint8_t direction_rx;  /* +0x10 */
    uint8_t reserved17;    /* +0x11 */
    uint8_t reserved18;    /* +0x12 */
    uint8_t reserved19;    /* +0x13 */
    uint8_t *buffer;       /* +0x14 */
} nor_mspi_pio_t;
_Static_assert(sizeof(nor_mspi_pio_t) == 24u, "stock MSPI PIO request is 24 bytes");

extern volatile uint32_t g2_norflash_controller_handle_20074544; /* RAM 0x20074544 MSPI handle */
extern int32_t g2_norflash_write_lower_4708a8(int32_t address, const uint8_t *buffer, uint32_t size);
extern void g2_norflash_lock_46f65e(void);
extern void g2_norflash_unlock_46f674(void);
extern void g2_norflash_exit_470e90(void);
extern uint32_t g2_norflash_wait_idle_4703ba(void);
extern void audio_uart_lv_memzero_48949c(void *destination, uint32_t size);
extern uint32_t g2_norflash_transfer_4c2098(uint32_t controller, const void *request, uint32_t timeout);

int32_t norflash_write_4709c0(int32_t address, const uint8_t *buffer, uint32_t size)
{
    return g2_norflash_write_lower_4708a8(address, buffer, size);
}

/* Returns the MSPI HAL status; the idle wait result is not checked by stock. */
uint32_t norflash_quad_read_471020(uint32_t address, uint8_t *buffer, uint32_t size)
{
    nor_mspi_pio_t request;

    if (g2_norflash_controller_handle_20074544 == 0u || buffer == NULL || size == 0u)
        return NOR_STATUS_INVALID_ARG;
    if (address >= NOR_SIZE_BYTES)
        return NOR_STATUS_OUT_OF_RANGE;

    g2_norflash_lock_46f65e();
    g2_norflash_exit_470e90();
    (void)g2_norflash_wait_idle_4703ba();
    audio_uart_lv_memzero_48949c(&request, sizeof(request));
    request.reserved6 = 0u;
    request.send_address = 1u;
    request.address = address;
    request.send_instr = 1u;
    request.instr = NOR_CMD_4QOR;
    request.direction_rx = 1u;
    request.num_bytes = size;
    request.buffer = buffer;
    request.reserved5 = 0u;
    request.reserved17 = 0u;
    uint32_t status = g2_norflash_transfer_4c2098(g2_norflash_controller_handle_20074544, &request,
                                                  NOR_MSPI_TIMEOUT);
    g2_norflash_unlock_46f674();
    return status;
}
