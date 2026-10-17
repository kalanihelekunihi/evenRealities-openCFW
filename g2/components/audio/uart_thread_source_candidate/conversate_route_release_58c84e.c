/* Native Conversate release route at 0x58c84e. */
#include <stdint.h>

extern void audio_conversate_route_before_release_58c836(uint32_t handle);
extern void audio_conversate_route_set_property_597f52(uint32_t handle, uint32_t value);
extern void audio_conversate_route_cleanup_597ee0(uint32_t handle);

uint32_t audio_conversate_route_release_58c84e(uint32_t handle) {
    if (handle == 0u)
        return 0u;
    audio_conversate_route_before_release_58c836(handle);
    audio_conversate_route_set_property_597f52(handle, 100u);
    audio_conversate_route_cleanup_597ee0(handle);
    return 1u;
}
