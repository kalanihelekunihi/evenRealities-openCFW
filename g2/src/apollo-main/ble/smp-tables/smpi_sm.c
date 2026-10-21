/* Authenticated native Cordio transition/action table: smpi_sm.c.
 * All indexed state rows and action names match stock interface pointers.
 * Pinned AmbiqSuite source is included verbatim below; only public names
 * are scoped to this experimental table candidate. */
#define SmpiInit audio_ble_pinned_smpiinit_unused
#define smpiSmIf audio_ble_smpi_legacy_table
#define smpCb audio_ble_smp_handler_state
#include "../../../../../third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio/ble-host/sources/stack/smp/smpi_sm.c"
