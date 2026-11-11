/* Apollo Main compressed SRAM record 0x75d3f4 initializes this observed
 * 16-byte device-manager prefix at 0x2000060c. Both C consumer names refer
 * to the same native state. The complete native allocation extent and
 * absolute pointer/code placement remain separate gates. */
#include <stdint.h>

/* Sim-test fix (2026-10-26): the stock RAM-init words 0x004c6241/0x004c64a5 are
 * stock-flash Thumb pointers; copying them as bytes made our image jump
 * into unrelated code (Renode boot hang in main_5ce01e). Evidence: stock words are Thumb addresses of device_mgr_fn_004c6240/_004c64a4; called via thread_manager.c:213.
 * Now relocated to our own symbols device_mgr_fn_004c6240/device_mgr_fn_004c64a4. Layout and size unchanged. */
void device_mgr_fn_004c6240(void);
void device_mgr_fn_004c64a4(void);
_Alignas(4) struct { void (*init)(void); void (*deinit)(void); uint8_t rest[8u]; } audio_device_manager_state = {
    device_mgr_fn_004c6240, device_mgr_fn_004c64a4, {0}
};
__asm__(".global audio_ble_device_manager_state\n"
        ".set audio_ble_device_manager_state,audio_device_manager_state");
