/* Authenticated native Cordio transition/action table: smpr_sm.c.
 * All indexed state rows and action names match stock interface pointers.
 * Pinned AmbiqSuite source is included verbatim below; only public names
 * are scoped to this experimental table candidate. */
#define SmprInit audio_ble_pinned_smprinit_unused
#define smprSmIf audio_ble_smpr_legacy_table
#define smpCb audio_ble_smp_handler_state
#include "../../../../../third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio/ble-host/sources/stack/smp/smpr_sm.c"
