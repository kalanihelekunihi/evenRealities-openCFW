/* Apollo main storage product state: NVDB default-record table and its
 * RAM records (storage/nvdb), FlashDB database objects (kvdb), littlefs
 * port boot-count file, menu configuration cells set by the KVDB module
 * configure path, and the CRC-32C MRAM table. FlashDB and littlefs library
 * internals belong to the upstream units.
 *
 * .data values are from the decoded startup init image (RAM
 * 0x20000000..0x20004557); ROM bytes are from the stock image (VA = file
 * offset + 0x437fe0). Sizes are the sizeof of the referencing declarations,
 * the FlashDB default-node lengths and the gap to the next stock object. */
#include <stdint.h>

/* ROM 0x6983a8: MSB-first CRC-32C table, polynomial 0x1edc6f41 (entry[1]),
 * checked against the generator for all 256 entries. */
const uint32_t g2_crc32c_msb_table[256] = {
    0x00000000u, 0x1edc6f41u, 0x3db8de82u, 0x2364b1c3u,
    0x7b71bd04u, 0x65add245u, 0x46c96386u, 0x58150cc7u,
    0xf6e37a08u, 0xe83f1549u, 0xcb5ba48au, 0xd587cbcbu,
    0x8d92c70cu, 0x934ea84du, 0xb02a198eu, 0xaef676cfu,
    0xf31a9b51u, 0xedc6f410u, 0xcea245d3u, 0xd07e2a92u,
    0x886b2655u, 0x96b74914u, 0xb5d3f8d7u, 0xab0f9796u,
    0x05f9e159u, 0x1b258e18u, 0x38413fdbu, 0x269d509au,
    0x7e885c5du, 0x6054331cu, 0x433082dfu, 0x5deced9eu,
    0xf8e959e3u, 0xe63536a2u, 0xc5518761u, 0xdb8de820u,
    0x8398e4e7u, 0x9d448ba6u, 0xbe203a65u, 0xa0fc5524u,
    0x0e0a23ebu, 0x10d64caau, 0x33b2fd69u, 0x2d6e9228u,
    0x757b9eefu, 0x6ba7f1aeu, 0x48c3406du, 0x561f2f2cu,
    0x0bf3c2b2u, 0x152fadf3u, 0x364b1c30u, 0x28977371u,
    0x70827fb6u, 0x6e5e10f7u, 0x4d3aa134u, 0x53e6ce75u,
    0xfd10b8bau, 0xe3ccd7fbu, 0xc0a86638u, 0xde740979u,
    0x866105beu, 0x98bd6affu, 0xbbd9db3cu, 0xa505b47du,
    0xef0edc87u, 0xf1d2b3c6u, 0xd2b60205u, 0xcc6a6d44u,
    0x947f6183u, 0x8aa30ec2u, 0xa9c7bf01u, 0xb71bd040u,
    0x19eda68fu, 0x0731c9ceu, 0x2455780du, 0x3a89174cu,
    0x629c1b8bu, 0x7c4074cau, 0x5f24c509u, 0x41f8aa48u,
    0x1c1447d6u, 0x02c82897u, 0x21ac9954u, 0x3f70f615u,
    0x6765fad2u, 0x79b99593u, 0x5add2450u, 0x44014b11u,
    0xeaf73ddeu, 0xf42b529fu, 0xd74fe35cu, 0xc9938c1du,
    0x918680dau, 0x8f5aef9bu, 0xac3e5e58u, 0xb2e23119u,
    0x17e78564u, 0x093bea25u, 0x2a5f5be6u, 0x348334a7u,
    0x6c963860u, 0x724a5721u, 0x512ee6e2u, 0x4ff289a3u,
    0xe104ff6cu, 0xffd8902du, 0xdcbc21eeu, 0xc2604eafu,
    0x9a754268u, 0x84a92d29u, 0xa7cd9ceau, 0xb911f3abu,
    0xe4fd1e35u, 0xfa217174u, 0xd945c0b7u, 0xc799aff6u,
    0x9f8ca331u, 0x8150cc70u, 0xa2347db3u, 0xbce812f2u,
    0x121e643du, 0x0cc20b7cu, 0x2fa6babfu, 0x317ad5feu,
    0x696fd939u, 0x77b3b678u, 0x54d707bbu, 0x4a0b68fau,
    0xc0c1d64fu, 0xde1db90eu, 0xfd7908cdu, 0xe3a5678cu,
    0xbbb06b4bu, 0xa56c040au, 0x8608b5c9u, 0x98d4da88u,
    0x3622ac47u, 0x28fec306u, 0x0b9a72c5u, 0x15461d84u,
    0x4d531143u, 0x538f7e02u, 0x70ebcfc1u, 0x6e37a080u,
    0x33db4d1eu, 0x2d07225fu, 0x0e63939cu, 0x10bffcddu,
    0x48aaf01au, 0x56769f5bu, 0x75122e98u, 0x6bce41d9u,
    0xc5383716u, 0xdbe45857u, 0xf880e994u, 0xe65c86d5u,
    0xbe498a12u, 0xa095e553u, 0x83f15490u, 0x9d2d3bd1u,
    0x38288facu, 0x26f4e0edu, 0x0590512eu, 0x1b4c3e6fu,
    0x435932a8u, 0x5d855de9u, 0x7ee1ec2au, 0x603d836bu,
    0xcecbf5a4u, 0xd0179ae5u, 0xf3732b26u, 0xedaf4467u,
    0xb5ba48a0u, 0xab6627e1u, 0x88029622u, 0x96def963u,
    0xcb3214fdu, 0xd5ee7bbcu, 0xf68aca7fu, 0xe856a53eu,
    0xb043a9f9u, 0xae9fc6b8u, 0x8dfb777bu, 0x9327183au,
    0x3dd16ef5u, 0x230d01b4u, 0x0069b077u, 0x1eb5df36u,
    0x46a0d3f1u, 0x587cbcb0u, 0x7b180d73u, 0x65c46232u,
    0x2fcf0ac8u, 0x31136589u, 0x1277d44au, 0x0cabbb0bu,
    0x54beb7ccu, 0x4a62d88du, 0x6906694eu, 0x77da060fu,
    0xd92c70c0u, 0xc7f01f81u, 0xe494ae42u, 0xfa48c103u,
    0xa25dcdc4u, 0xbc81a285u, 0x9fe51346u, 0x81397c07u,
    0xdcd59199u, 0xc209fed8u, 0xe16d4f1bu, 0xffb1205au,
    0xa7a42c9du, 0xb97843dcu, 0x9a1cf21fu, 0x84c09d5eu,
    0x2a36eb91u, 0x34ea84d0u, 0x178e3513u, 0x09525a52u,
    0x51475695u, 0x4f9b39d4u, 0x6cff8817u, 0x7223e756u,
    0xd726532bu, 0xc9fa3c6au, 0xea9e8da9u, 0xf442e2e8u,
    0xac57ee2fu, 0xb28b816eu, 0x91ef30adu, 0x8f335fecu,
    0x21c52923u, 0x3f194662u, 0x1c7df7a1u, 0x02a198e0u,
    0x5ab49427u, 0x4468fb66u, 0x670c4aa5u, 0x79d025e4u,
    0x243cc87au, 0x3ae0a73bu, 0x198416f8u, 0x075879b9u,
    0x5f4d757eu, 0x41911a3fu, 0x62f5abfcu, 0x7c29c4bdu,
    0xd2dfb272u, 0xcc03dd33u, 0xef676cf0u, 0xf1bb03b1u,
    0xa9ae0f76u, 0xb7726037u, 0x9416d1f4u, 0x8acabeb5u,
};

/* RAM 0x2005dffc: two FlashDB KVDB objects of 0x8ac bytes (0x1158 B). */
uint8_t g2_flashdb_db_rows[2u * 0x8acu] __attribute__((aligned(4)));

/* RAM 0x2006b930: AmbiqSuite am_util_stdio print scratch (g_prfbuf,
 * AM_PRINTF_BUFSIZE 1024; literal 0x473470 of am_util_stdio_printf 0x4733ee).
 * Its print hook g_pfnCharPrint 0x200742f0 is
 * audio_uart_stdio_print_char_cell_200742f0 (app/board-callback);
 * g2_flashdb_print_sink is a defsym alias of it. Replaces the unlinked
 * flashdb-print-wrapper/print_buffer_2006b930.c. */
uint8_t g2_flashdb_print_buffer[1024] __attribute__((aligned(4)));

/* RAM 0x200728a0: lfs_file_t (0x54 B with the U7 littlefs configuration). */
uint8_t g2_littlefs_boot_count_file[0x54] __attribute__((aligned(4)));

/* Menu configuration (menu_page.c / service_kvdb_module_configure.c). */
uint8_t g2_menu_page_items[0x410] __attribute__((aligned(4))); /* RAM 0x2006ad0c, 20 rows */
int32_t g2_menu_use_ext_items;                                 /* RAM 0x200746fc */
int32_t g2_menu_ext_item_count;                                /* RAM 0x20074700 */

/* NVDB RAM records (.data). */
/* RAM 0x20003858 "nvString" record, 9 bytes. */
char g2_nvdb_string_record_20003858[9] __attribute__((aligned(4))) = "nvString";
/* RAM 0x20003864 "nvMagic" record. */
uint32_t g2_nvdb_magic_record_20003864 = 0x55550022u;
/* RAM 0x200038d4 "nvAdvMagic", 4 bytes: 01 20 00 00. */
uint16_t g2_nvdb_adv_magic_record[2] __attribute__((aligned(4))) = {0x2001u, 0x0000u};
/* RAM 0x200038d8 "nvBuzzer", 12 bytes. */
uint32_t g2_nvdb_buzzer_record[3] = {0x2u, 0xfa0u, 0x1eu};
/* RAM 0x200038e4 "nvMAC", 10 bytes: 01 then nine zero bytes. */
uint8_t g2_nvdb_mac_record[10] __attribute__((aligned(4))) = {0x01u};
/* RAM 0x200038f4 "nvSCald", 0x5c bytes. */
uint32_t g2_nvdb_sensor_caldata[23] = {
    0x00000001u, /* +0x00 1 */
    0x3fa00000u, /* +0x04 1.25 */
    0x3fa00000u, /* +0x08 1.25 */
    0x3fa00000u, /* +0x0c 1.25 */
    0x3fa00000u, /* +0x10 1.25 */
    0x3fa00000u, /* +0x14 1.25 */
    0x3fa00000u, /* +0x18 1.25 */
    0x3fa00000u, /* +0x1c 1.25 */
    0x3fa00000u, /* +0x20 1.25 */
    0x3fa00000u, /* +0x24 1.25 */
    0x3fa00000u, /* +0x28 1.25 */
    0xffed2979u, /* +0x2c 4293732729 */
    0x0012d687u, /* +0x30 1234567 */
    0x0012d687u, /* +0x34 1234567 */
    0xffed2979u, /* +0x38 4293732729 */
    0x3fa00000u, /* +0x3c 1.25 */
    0xffffffffu, /* +0x40 4294967295 */
    0xffffffffu, /* +0x44 4294967295 */
    0xffffffffu, /* +0x48 4294967295 */
    0xffffffffu, /* +0x4c 4294967295 */
    0xffffffffu, /* +0x50 4294967295 */
    0xffffffffu, /* +0x54 4294967295 */
    0x00000000u, /* +0x58 0 */
};
/* RAM 0x20003950 "nvSCaldAG", 0x44 bytes. Its +0x1c..+0x3f words (the
 * 3x3 IMU calibration matrix) are read by app/a-58-pt-protocol as
 * g2_imu_calibration_matrix_2000396c, an assembler alias below. */
uint32_t g2_nvdb_sensor_caldata_ag[17] = {
    0x00000001u, /* +0x00 1 */
    0x00000000u, /* +0x04 0 */
    0x00000000u, /* +0x08 0 */
    0x00000000u, /* +0x0c 0 */
    0x00000000u, /* +0x10 0 */
    0x00000000u, /* +0x14 0 */
    0x00000000u, /* +0x18 0 */
    0xbf51ab4bu, /* +0x1c -0.819019973 */
    0xbebbd599u, /* +0x20 -0.366863996 */
    0x3ed912fdu, /* +0x24 0.423972994 */
    0x3ee548cbu, /* +0x28 0.447820991 */
    0x3d8a0cffu, /* +0x2c 0.0674076006 */
    0x3f5f8002u, /* +0x30 0.873046994 */
    0xbeb2d14au, /* +0x34 -0.349252999 */
    0x3f6ed688u, /* +0x38 0.932960987 */
    0x3ded9e84u, /* +0x3c 0.116025001 */
    0x00000000u, /* +0x40 0 */
};
__asm__(".globl g2_imu_calibration_matrix_2000396c\n"
        ".set g2_imu_calibration_matrix_2000396c, g2_nvdb_sensor_caldata_ag + 0x1c\n"
        ".type g2_imu_calibration_matrix_2000396c, %object\n"
        ".size g2_imu_calibration_matrix_2000396c, 0x24\n");

/* Records owned elsewhere: nvProdMode 0x200038f0 (hal/uart/uart-product)
 * and nvSysDt 0x20003994 (drivers/display/display-driver). */
extern volatile uint8_t g2_uart_product_mode_state[];
extern uint8_t display_driver_ratio_cells_20003994[];

typedef struct {
    const char *key;
    void *value;
    uint32_t value_len;
} g2_fdb_default_kv_node_t;
_Static_assert(sizeof(g2_fdb_default_kv_node_t) == 12u, "struct fdb_default_kv_node");

/* RAM 0x20003868 (.data): FlashDB default KV nodes of the "factory" NVDB.
 * Keys are ROM strings 0x78bfa8, 0x78e5e4, 0x78bfb4, 0x78e5ec, 0x78bfc0,
 * 0x78e5f4, 0x78e5fc, 0x78bfcc, 0x78bfd8. */
g2_fdb_default_kv_node_t g2_nvdb_default_kv_nodes[9] = {
    {"nvString", g2_nvdb_string_record_20003858, 9u},
    {"nvMagic", &g2_nvdb_magic_record_20003864, 4u},
    {"nvProdMode", (void *)g2_uart_product_mode_state, 4u},
    {"nvSysDt", display_driver_ratio_cells_20003994, 0xacu},
    {"nvAdvMagic", g2_nvdb_adv_magic_record, 4u},
    {"nvMAC", g2_nvdb_mac_record, 10u},
    {"nvSCald", g2_nvdb_sensor_caldata, 0x5cu},
    {"nvSCaldAG", g2_nvdb_sensor_caldata_ag, 0x44u},
    {"nvBuzzer", g2_nvdb_buzzer_record, 12u},
};

/* Zero-initialised NVDB state. */
g2_fdb_default_kv_node_t *g2_nvdb_default_kvs; /* RAM 0x20074990 */
volatile uint8_t g2_nvdb_legacy_psn_flag;      /* RAM 0x2007501a */
char g2_nvdb_month_text[12];                   /* RAM 0x200740b0 */
char g2_otp_psn[15];                           /* RAM 0x20073ee4 g_OTP_PSN */
