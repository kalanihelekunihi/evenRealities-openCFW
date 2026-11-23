/* Native Cordio/profile handler initialization 0x535488. */
#include <stdint.h>
extern uint8_t audio_ble_profile_handler_id; /* RAM 0x20074f8a */
extern const uint16_t audio_ble_profile_table_78f530[20]; /* ROM 0x78f530 */
extern const void *audio_ble_profile_dispatch_slot; /* RAM 0x20074360 */
extern const void *audio_ble_profile_table_slot; /* RAM 0x20074364 */
extern uint32_t audio_ble_profile_runtime_rows[6]; /* RAM 0x20074310..0x20074327 */
/* Stock 0x5fa056 is the two-byte alignment pad immediately before
 * vRestoreContextOfFirstTask at 0x5fa058. Discovery reads these bytes as
 * mode flags: [0]!=0 starts appDiscStart on encrypt/pair-complete;
 * [1]!=0 runs AppDiscReadDatabaseHash. They are not the RTOS function
 * (sources.json currently aliases audio_ble_profile_handler_entry_5fa056
 * to vRestoreContextOfFirstTask, whose OpenCFW first bytes are 0x0b,0x4a). */
static const uint8_t audio_ble_discovery_mode_bytes_5fa056[2] = { 0x01u, 0x00u };
void audio_ble_profile_handler_init(uint8_t handler,uint8_t *state,uint8_t *mode) {
    audio_ble_profile_handler_id=handler;
    audio_ble_profile_dispatch_slot=audio_ble_discovery_mode_bytes_5fa056;
    audio_ble_profile_table_slot=audio_ble_profile_table_78f530;
    audio_ble_profile_runtime_rows[0]=(uintptr_t)state;
    audio_ble_profile_runtime_rows[1]=(uintptr_t)mode;
    audio_ble_profile_runtime_rows[2]=(uintptr_t)(state+0x2au);
    audio_ble_profile_runtime_rows[3]=(uintptr_t)(state+0x30u);
    audio_ble_profile_runtime_rows[4]=(uintptr_t)state;
    audio_ble_profile_runtime_rows[5]=(uintptr_t)(state+4u);
}
