/* Apollo Main compressed SRAM record 0x75d3f4 initializes this observed
 * BLE MsgRx manager at 0x20003ffc. Selected paths use thread/queue cells
 * at +8/+12. Final absolute placement and wider native allocation remain
 * separate gates. */
#include <stdint.h>

/* Sim-test fix (2026-10-26): the stock RAM-init words 0x0048ee69/0x0048ee95 are
 * stock-flash Thumb pointers; copying them as bytes made our image jump
 * into unrelated code (Renode boot hang in main_5ce01e). Evidence: apollo_main.tsv 0x0048EE68 threadBleMsgRxInit / 0x0048EE94 threadBleMsgRxDeinit; thread_ble_msgrx.c:9-10; called via thread_manager.c:216.
 * Now relocated to our own symbols threadBleMsgRxInit/threadBleMsgRxDeinit. Layout and size unchanged. */
void threadBleMsgRxInit(void);
void threadBleMsgRxDeinit(void);
_Alignas(4) struct { void (*init)(void); void (*deinit)(void); uint8_t rest[8u]; } audio_ble_rx_thread_state = {
    threadBleMsgRxInit, threadBleMsgRxDeinit, {0}
};
