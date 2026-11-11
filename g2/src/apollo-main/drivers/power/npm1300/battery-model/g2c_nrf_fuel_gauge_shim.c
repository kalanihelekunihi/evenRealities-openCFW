/* Address-named entry points used by npmx_main_driver.c. The public Nordic API
 * symbols are supplied by g2c_fuel_gauge_source.c for the source-only build.
 * Stock addresses identify the original IAR link, not byte-identical bodies. */
#include "../../../../../../../third-party/upstream/nrf-fuel-gauge-1.0.1/include/nrf_fuel_gauge.h"

int nrf_fuel_gauge_init_43c150(const struct nrf_fuel_gauge_init_parameters *p, float *v0) {
    return nrf_fuel_gauge_init(p, v0);
}
int nrf_fuel_gauge_ext_state_update_55f74c(enum nrf_fuel_gauge_ext_state_info_type type,
                                           union nrf_fuel_gauge_ext_state_info_data *data) {
    return nrf_fuel_gauge_ext_state_update(type, data);
}
float nrf_fuel_gauge_process_55f848(float v, float i, float t, float dt,
                                    struct nrf_fuel_gauge_state_info *state) {
    return nrf_fuel_gauge_process(v, i, t, dt, state);
}
float nrf_fuel_gauge_tte_get_55f994(void) { return nrf_fuel_gauge_tte_get(); }
float nrf_fuel_gauge_ttf_get_55f9a0(void) { return nrf_fuel_gauge_ttf_get(); }

/* Retain the IAR math bridges used elsewhere in the composed image. */
extern float iar_expf_43ba98(float);
extern float iar_logf_598074(float);
float expf(float x) { return iar_expf_43ba98(x); }
float logf(float x) { return iar_logf_598074(x); }
float fabsf(float x) { return __builtin_fabsf(x); }
