/* Authenticated native Cordio transition/action table: smpi_sc_sm.c.
 * All indexed state rows and action names match stock interface pointers.
 * Pinned AmbiqSuite source is included verbatim below; only public names
 * are scoped to this experimental table candidate. */
/* The vendored SmpiScInit body below is the single implementation of the stock
 * SMP state-machine init entry (formerly a hand copy in
 * ble/ble-smp/display_ble_smp_sm_init.c). */
#define smpiScSmIf audio_ble_smpi_sc_table
#define smpiStateStr audio_ble_pinned_smpi_statestr_unused
#define smpCb audio_ble_smp_handler_state
#include "../../../../../third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio/ble-host/sources/stack/smp/smpi_sc_sm.c"
