/* OTA and EFS service/transport storage (S3 storage-definition pass,
 * 2.2.6.10).
 *
 * Stock owners: service\ota (ota_service_flash.c / ota_service_file_parse.c /
 * ota_service_export.c), the OTA BLE transport (a-12-ota-transport), the EVEN
 * file service (a-05-efs-service) and its transport (a-23-efs-transport).
 * .data values are from the decoded startup init image (scatter record
 * 0x75d3f4, RAM 0x20000000..0x20004557); everything else is zero-init
 * (0x20004558..0x20075048 or SSRAM). Sizes are the referencing C types,
 * cross-checked with the stride to the next stock object.
 *
 * Each transport owns one 0x2138-byte SSRAM block that its .data pointers
 * split into a 0x1020-byte RX reassembly buffer, a 0x1020-byte TX data copy
 * and a 0xf8-byte TX frame (stock pointers 0x20354c78/0x20355c98/0x20356cb8
 * for OTA, 0x20352b40/0x20353b60/0x20354b80 for EFS). The OTA block is also
 * handed out whole as the Android notification JSON buffer
 * (svc_android_notify_buffer_48e0a8, zeroed as 0x2137 bytes by the EFS
 * service), so it is one object here. */
#include <stdint.h>

#define TRANSPORT_BLOCK_SIZE 0x2138u
#define TRANSPORT_RX_OFFSET 0x0000u
#define TRANSPORT_TX_OFFSET 0x1020u
#define TRANSPORT_FRAME_OFFSET 0x2040u

typedef struct {
    void (*rx)(uint8_t command, const uint8_t *data, uint16_t length);
    uint8_t (*tx)(const uint8_t *frame, uint16_t length);
} g2_transport_cb_t;
_Static_assert(sizeof(g2_transport_cb_t) == 8u, "transport callbacks");

/* Flash backend vtable (ota_service_flash.c g2_ota_flash_ops_t). */
typedef struct {
    uint32_t write_size;
    uint32_t erase_size;
    int32_t (*init)(void);
    int32_t (*deinit)(void);
    int32_t (*lock)(void);
    int32_t (*unlock)(void);
    int32_t (*read)(void *dst, uint32_t address, uint32_t length);
    int32_t (*program)(uint32_t address, const void *src, uint32_t length);
    int32_t (*erase)(uint32_t address);
} g2_ota_flash_backend_t;
_Static_assert(sizeof(g2_ota_flash_backend_t) == 0x24u, "flash vtable");

typedef struct {
    uint8_t *buffer; /* +0 */
    uint16_t fill;   /* +4 */
} g2_ota_page_cache_t;
_Static_assert(sizeof(g2_ota_page_cache_t) == 8u, "write cache");

/* Callees, resolved by address, declared with their g2/src prototypes and
 * converted to the slot types through a generic function pointer. 0x48f12c is linked through the existing
 * Thread_MsgRxFromBle defsym; 0x5a4f30/0x5a4f58/0x5a4f80 are the MRAM
 * backend bodies (range check 0x5a4ef4, then memcpy / 0x47cbe8 MRAM program
 * / erase), not yet written in g2/src. */
extern int32_t Thread_MsgRxFromBle(uint32_t id, const void *bytes, uint32_t length);       /* 0x48f12c */
extern uint32_t APP_BleEfsSendDataMsg(const uint8_t *data, uint16_t length);              /* 0x4be580 */
extern uint32_t APP_EvenOtaSendDataMsg(const uint8_t *data, uint16_t length);             /* 0x4bdd7e */
extern int32_t g2_norflash_read_lower_4709c8(int32_t address, uint8_t *buffer, uint32_t size); /* 0x4709c8 */
extern int32_t norflash_write_4709c0(int32_t address, const uint8_t *buffer, uint32_t size); /* 0x4709c0 */
extern uint32_t g2_norflash_erase_lower_47075c(uint32_t address);                        /* 0x47075c */
extern int32_t ota_mram_read_5a4f30(void *dst, uint32_t address, uint32_t length);       /* 0x5a4f30 */
extern int32_t ota_mram_program_5a4f58(uint32_t address, const void *src, uint32_t length); /* 0x5a4f58 */
extern int32_t ota_mram_erase_5a4f80(uint32_t address);                                  /* 0x5a4f80 */

typedef int32_t (*g2_flash_read_fn)(void *, uint32_t, uint32_t);
typedef int32_t (*g2_flash_program_fn)(uint32_t, const void *, uint32_t);
typedef int32_t (*g2_flash_erase_fn)(uint32_t);
typedef void (*g2_transport_rx_fn)(uint8_t, const uint8_t *, uint16_t);
typedef uint8_t (*g2_transport_tx_fn)(const uint8_t *, uint16_t);

/* ---- OTA service ------------------------------------------------------- */

/* RAM 0x2000038c (.data): MRAM backend {0x1000, 0x1000, 0, 0, 0, 0,
 * 0x5a4f31, 0x5a4f59, 0x5a4f81}. */
g2_ota_flash_backend_t g2_ota_mram_flash_ops = {
    0x1000u, 0x1000u, 0, 0, 0, 0, ota_mram_read_5a4f30, ota_mram_program_5a4f58, ota_mram_erase_5a4f80};
/* RAM 0x20003028 (.data): external NOR backend {0x1000, 0x1000, 0, 0, 0, 0,
 * 0x4709c9, 0x4709c1, 0x47075d}. */
g2_ota_flash_backend_t g2_ota_xip_flash_ops = {
    0x1000u, 0x1000u, 0, 0, 0, 0, (g2_flash_read_fn)(void (*)(void))g2_norflash_read_lower_4709c8,
    (g2_flash_program_fn)(void (*)(void))norflash_write_4709c0, (g2_flash_erase_fn)(void (*)(void))g2_norflash_erase_lower_47075c};
/* RAM 0x2000301c (.data): active backend, initially 0x2000038c (MRAM). */
const g2_ota_flash_backend_t *g2_ota_flash_ops = &g2_ota_mram_flash_ops;

/* RAM 0x2034ac00 (SSRAM, stride 0x1010): page write-back buffer, one
 * write_size (0x1000) page. */
__attribute__((aligned(4))) static uint8_t g2_ota_page_buffer_2034ac00[0x1000];
/* RAM 0x20003020 (.data): {0x2034ac00, 0}. */
g2_ota_page_cache_t g2_ota_write_cache = {g2_ota_page_buffer_2034ac00, 0u};

__attribute__((aligned(4))) uint8_t g2_ota_cache_buffer[0x1000];  /* RAM 0x2034bc10, stride 0x1010 */
__attribute__((aligned(4))) uint8_t g2_ota_verify_buffer[0x1000]; /* RAM 0x2034cc20, stride 0x1010 */
__attribute__((aligned(4))) uint8_t g2_ota_transfer[0x70];        /* RAM 0x20071ff0 g2_ota_transfer_t */
uint32_t g2_ota_start_tick;      /* RAM 0x20074844 */
uint32_t g2_ota_data_start_tick; /* RAM 0x20074848 */
uint32_t g2_ota_last_tick;       /* RAM 0x2007484c */
uint8_t g2_ota_crc_failed;       /* RAM 0x20075007 */

/* ---- OTA transport ----------------------------------------------------- */

/* RAM 0x20354c78 (SSRAM): RX / TX / frame block, also the Android
 * notification JSON buffer. */
__attribute__((aligned(4))) uint8_t g2_ota_shared_buffer_20354c78[TRANSPORT_BLOCK_SIZE];
/* RAM 0x2000304c / 0x20003050 / 0x20003054 (.data). */
uint8_t *g2_ota_rx_static_buf_2000304c = g2_ota_shared_buffer_20354c78 + TRANSPORT_RX_OFFSET;
uint8_t *g2_ota_tx_data_buf_20003050 = g2_ota_shared_buffer_20354c78 + TRANSPORT_TX_OFFSET;
uint8_t *g2_ota_tx_frame_buf_20003054 = g2_ota_shared_buffer_20354c78 + TRANSPORT_FRAME_OFFSET;
/* RAM 0x20003058 (.data): {0x48f12d, 0x4bdd7f}. */
g2_transport_cb_t g2_ota_transport_callbacks_20003058 = {(g2_transport_rx_fn)(void (*)(void))Thread_MsgRxFromBle,
                                                       (g2_transport_tx_fn)(void (*)(void))APP_EvenOtaSendDataMsg};

uint32_t g2_ota_rx_total_len_20074850;  /* RAM 0x20074850 */
uint8_t *g2_ota_rx_data_buf_20074854;   /* RAM 0x20074854 */
uint8_t g2_ota_rx_active_20074ff4;      /* RAM 0x20074ff4 */
uint8_t g2_ota_rx_error_pending_20074ff5; /* RAM 0x20074ff5 */
uint8_t g2_ota_rx_error_sync_id_20074ff6; /* RAM 0x20074ff6 */
uint8_t g2_ota_sync_id_20074ff7;        /* RAM 0x20074ff7 */

/* ---- EFS transport ----------------------------------------------------- */

/* RAM 0x20352b40 (SSRAM): RX / TX / frame block (stride 0x2138 to the OTA
 * block). */
__attribute__((aligned(4))) static uint8_t g2_efs_transport_block_20352b40[TRANSPORT_BLOCK_SIZE];
/* RAM 0x20000960 / 0x20000964 / 0x20000968 (.data). */
uint8_t *g2_efs_rx_static_buf_20000960 = g2_efs_transport_block_20352b40 + TRANSPORT_RX_OFFSET;
uint8_t *g2_efs_tx_data_buf_20000964 = g2_efs_transport_block_20352b40 + TRANSPORT_TX_OFFSET;
uint8_t *g2_efs_tx_frame_buf_20000968 = g2_efs_transport_block_20352b40 + TRANSPORT_FRAME_OFFSET;
/* RAM 0x2000096c (.data): {0x48f12d, 0x4be581}. */
g2_transport_cb_t g2_efs_transport_callbacks_2000096c = {(g2_transport_rx_fn)(void (*)(void))Thread_MsgRxFromBle,
                                                       (g2_transport_tx_fn)(void (*)(void))APP_BleEfsSendDataMsg};

uint32_t g2_efs_rx_total_len_20074564;    /* RAM 0x20074564 */
uint8_t *g2_efs_rx_data_buf_20074568;     /* RAM 0x20074568 */
uint8_t g2_efs_rx_active_20074fbd;        /* RAM 0x20074fbd */
uint8_t g2_efs_rx_error_pending_20074fbe; /* RAM 0x20074fbe */
uint8_t g2_efs_rx_error_sync_id_20074fbf; /* RAM 0x20074fbf */

/* ---- EFS service ------------------------------------------------------- */

__attribute__((aligned(4))) uint8_t g2_efs_export_buffer[0x1000]; /* RAM 0x2035adf8, stride 0x1010 */
/* RAM 0x2035be08, stride 0x1010: verify chunk; efs_service_file.c names the
 * same cell g2_efs_crc_buffer (defsym alias). */
__attribute__((aligned(4))) uint8_t g2_efs_verify_buffer[0x1000];
uint8_t *g2_efs_android_msg_buffer; /* RAM 0x20074554 */
uint32_t g2_efs_start_tick;         /* RAM 0x20074558 */
uint32_t g2_efs_data_tick;          /* RAM 0x2007455c */
uint32_t g2_efs_last_tick;          /* RAM 0x20074560 */
volatile uint8_t g2_efs_export_active; /* RAM 0x20074fbc */
