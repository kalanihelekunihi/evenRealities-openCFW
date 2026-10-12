/* Pinned Cordio common SMP action bodies. The native state-table action
 * slots have been matched by name; the existing native smpSmExecute body
 * remains the selected provider. */
#define smpCb audio_ble_smp_handler_state
#define smpSmExecute audio_ble_pinned_smp_sm_execute_unused
#include "../../../../../third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio/ble-host/sources/stack/smp/smp_act.c"
