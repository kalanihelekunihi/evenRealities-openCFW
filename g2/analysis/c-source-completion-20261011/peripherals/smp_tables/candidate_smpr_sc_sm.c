/* Authenticated native Cordio transition/action table: smpr_sc_sm.c.
 * All indexed state rows and action names match stock interface pointers.
 * Pinned AmbiqSuite source is included verbatim below; only public names
 * are scoped to this experimental table candidate. */
#define SmprScInit audio_ble_pinned_smprscinit_unused
#define smprScSmIf audio_ble_smpr_sc_table
#define smprStateStr audio_ble_pinned_smpr_statestr_unused
#define smpCb audio_ble_smp_handler_state
#include "../../../../../third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio/ble-host/sources/stack/smp/smpr_sc_sm.c"
