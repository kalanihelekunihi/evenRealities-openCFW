/* Native als_function_37 0x4ae8e8: clamp and propagate ALS scale. */
#include <stdint.h>
extern uint32_t audio_als_active_previous; /* RAM 0x200741e0 */
extern uint32_t audio_als_default_previous; /* RAM 0x200741dc */
extern uint32_t audio_als_scale_clamped; /* RAM 0x20000060 */
extern uint32_t audio_als_scale_active; /* RAM 0x20000064 */
extern uint32_t audio_als_scale_shadow; /* RAM 0x20000068 */
extern uint32_t audio_als_recompute_pending; /* RAM 0x20074200 */
extern void audio_als_apply_previous(uint32_t); /* native 0x4add8c */
void audio_settings_apply_als(uint32_t requested) {
    uint32_t previous=audio_als_active_previous;
    if(previous==0u) previous=audio_als_default_previous;
    uint32_t clamped=requested;
    if(clamped<614u) clamped=614u;
    if(clamped>1434u) clamped=1434u;
    audio_als_scale_clamped=clamped;
    audio_als_scale_active=clamped;
    audio_als_scale_shadow=audio_als_scale_active;
    audio_als_recompute_pending=0u;
    audio_als_apply_previous(previous);
}
