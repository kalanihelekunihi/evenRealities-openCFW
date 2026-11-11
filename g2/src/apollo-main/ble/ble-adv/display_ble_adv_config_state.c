/* Apollo Main compressed SRAM record 0x75d3f4 initializes this pointer
 * table at native RAM 0x20003838 with the stock image words
 *   200038f0 20003994 200038d4 200038e4 200038f4 20003950 200038d8 00000000
 * (.waves/init_20000000.bin +0x3838). Each word is the address of one live
 * NVDB record; the record identities come from include/g2_nvdb.h:
 *   0x200038f0 nvProdMode, 0x20003994 nvSysDt, 0x200038d4 nvAdvMagic,
 *   0x200038e4 nvMAC, 0x200038f4 nvSCald, 0x20003950 nvSCaldAG,
 *   0x200038d8 nvBuzzer.
 * Evidence (sim stkbd3/stkbd4): stock _bleAdvNameSet 0x46dd44 reads word +12
 * (0x200038e4) and copies +1..+6 = 69 df 22 65 31 fc, the MAC written by
 * nvdbMacDefaultInitialize 0x5d9f48, into the BD address sent with 0xFC43.
 * The raw stock words pointed into unrelated objects in our layout, which
 * gave a zero BD address, so the table now holds relocations to our
 * definitions of the same records. */
#include <stdint.h>

extern uint8_t g2_uart_product_mode_state[];          /* nvProdMode */
extern uint8_t display_driver_ratio_cells_20003994[]; /* nvSysDt */
extern uint8_t g2_nvdb_adv_magic_record[];            /* nvAdvMagic */
extern uint8_t g2_nvdb_mac_record[];                  /* nvMAC */
extern uint8_t g2_nvdb_sensor_caldata[];              /* nvSCald */
extern uint8_t g2_nvdb_sensor_caldata_ag[];           /* nvSCaldAG */
extern uint8_t g2_nvdb_buzzer_record[];               /* nvBuzzer */

/* Same symbol and 32-byte size as before; other units declare it as
 * uint8_t audio_ble_adv_config_state[]. */
_Alignas(4) void *g2_adv_config_state_ptrs[8] __asm__("audio_ble_adv_config_state") = {
    g2_uart_product_mode_state,
    display_driver_ratio_cells_20003994,
    g2_nvdb_adv_magic_record,
    g2_nvdb_mac_record,
    g2_nvdb_sensor_caldata,
    g2_nvdb_sensor_caldata_ag,
    g2_nvdb_buzzer_record,
    0,
};
