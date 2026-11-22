/* Reconstructed nrf_fuel_gauge API (init, ext-state, process, TTE, TTF)
 * plus relocated typographic translations of stock 0x43A1B0, 0x43A698 and
 * callees (fg_cores.S). The public wrappers follow the stock Thumb at
 * 0x43C150, 0x55F74C, 0x55F848, 0x55F994 and 0x55F9A0. */
#include "../../../../../../../third-party/upstream/nrf-fuel-gauge-1.0.1/include/nrf_fuel_gauge.h"
#include "g2c_fuel_gauge_model_tte.h"
#include <stddef.h>

const char *nrf_fuel_gauge_version = "c205a2";
const char *nrf_fuel_gauge_build_date = "Apr 28 2025";
const enum nrf_fuel_gauge_variant_type nrf_fuel_gauge_variant =
    NRF_FUEL_GAUGE_VARIANT_SECONDARY;

/* Scratch the stock cores originally addressed at 0x20004510. */
uint32_t fg_aux[16];
uint32_t fg_iar_err[8];

/* Model state: 0xE8 bytes, TTE at +0x84, model pointer at +0xE0, magic at +0xE4. */
static uint8_t model_state[0xE8];
static uint8_t ext_block[0x14]; /* charge_state, vbus, factors, limits */

#define EXT_CHARGE_STATE  ((uint8_t *)ext_block)[0]
#define EXT_VBUS          ((uint8_t *)ext_block)[1]

/* Stock default opt_params at 0x006D8248, 0x6C bytes. */
static const uint32_t fg_default_opt[0x6C / 4] = {
    0x358637BD, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x358637BD, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x322BCC77, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
    0x3951B717, 0x3B449BA6, 0x3A83126F, 0x42480000, 0x41F00000,
    0x3F733333, 0x3FA66666, 0x3F800000, 0x42700000, 0x3FC00000,
    0x3F666666, 0x3F733333,
};

#define MAGIC 0xABCD1234u

/* Hard-float AAPCS: v,i,T[,dt] in s0-s3, pointers in r0-r3, extra on the stack. */
void nrf_model_init_43a1b0(float v, float i, float T, const void *opt,
                           const void *model, void *state, float *adjusted_v);
void nrf_model_process_43a698(float v, float i, float T, float dt, void *state,
                              const void *model, float *soc, void *scratch, void *opt);
void nrf_model_tte_params_58eab0(void *state, const float pair[2]);
float nrf_model_ttf_58eac4(void *state, int mode, const void *model);

static uint32_t float_bits(float value)
{
    uint32_t bits;
    __builtin_memcpy(&bits, &value, sizeof(bits));
    return bits;
}

static float bits_float(uint32_t bits)
{
    float value;
    __builtin_memcpy(&value, &bits, sizeof(value));
    return value;
}

static int valid_saved_state(const void *state)
{
    if (state == 0) return 0;
    uint32_t magic;
    __builtin_memcpy(&magic, (const uint8_t *)state + 0xE4, 4);
    return magic == MAGIC;
}

static void set_saved_magic(void *state)
{
    uint32_t magic = MAGIC;
    if (state) __builtin_memcpy((uint8_t *)state + 0xE4, &magic, 4);
}

int nrf_fuel_gauge_init(const struct nrf_fuel_gauge_init_parameters *parameters,
                        float *adjusted_voltage)
{
    if (parameters == 0) return -22;
    if (parameters->model == 0 && parameters->state == 0) return -22;

    __builtin_memset(ext_block, 0, sizeof ext_block);
    /* charge_factor, discharge_factor, charge_limit, term_current */
    float ones_nans[4] = {1.0f, 1.0f, __builtin_nanf(""), __builtin_nanf("")};
    __builtin_memcpy(ext_block + 4, ones_nans, sizeof ones_nans);
    EXT_CHARGE_STATE = 0;
    /* vbus already 0 */

    if (parameters->state != 0) {
        if (!valid_saved_state(parameters->state)) return -22;
        __builtin_memcpy(model_state, parameters->state, 0xE8);
        return 0;
    }

    __builtin_memset(model_state, 0, sizeof model_state);
    uint8_t opt[0x70];
    __builtin_memcpy(opt, fg_default_opt, 0x6C);
    __builtin_memcpy(model_state + 0xE0, &parameters->model, 4);
    if (parameters->opt_params != 0) {
        const struct nrf_fuel_gauge_config_parameters *o = parameters->opt_params;
        /* Stock copies a subset of fields onto the default opt image. */
        __builtin_memcpy(opt + 0x4C, &o->tau1, 4);
        __builtin_memcpy(opt + 0x50, &o->tau2, 4);
        __builtin_memcpy(opt + 0x54, &o->neta1, 4);
        __builtin_memcpy(opt + 0x58, &o->neta2, 4);
        __builtin_memcpy(opt + 0x5C, &o->neta3, 4);
        __builtin_memcpy(opt + 0x68, &o->beta1, 4);
        __builtin_memcpy(opt + 0x6C - 4, &o->beta2, 4); /* +0x68 is beta1; beta2 at +0x6C? */
        /* From init disasm (offsets into the 0x6C copy, which starts at sp+4):
         * +0 (sp+4+0x48=sp+76=+0x4C): first 5 words tau1..
         * +0x40 of opt_params -> sp+96, +0x2c -> sp+100
         * Mapped in 43c1c6-43c1e8:
         *  opt[0]  -> sp+76  (opt_copy+0x48)
         *  opt[1]  -> sp+80
         *  opt[2]  -> sp+84
         *  opt[3]  -> sp+88
         *  opt[4]  -> sp+92
         *  opt[5]  -> sp+104  (+0x68)
         *  opt[6]  -> sp+108  (+0x6C)  -- 0x6C is the end, this is last word
         *  opt[0x28] -> sp+96 (+0x60)
         *  opt[0x2c] -> sp+100 (+0x64)
         */
        __builtin_memcpy(opt + 0x48, o, 20);          /* tau1..neta? first 5 floats */
        __builtin_memcpy(opt + 0x68, ((const uint8_t *)o) + 20, 8); /* next 2 floats at +0x14,+0x18 */
        __builtin_memcpy(opt + 0x60, ((const uint8_t *)o) + 0x28, 8);
    }

    float adj = 0.0f;
    nrf_model_init_43a1b0(parameters->v0, parameters->i0, parameters->t0,
                          opt, parameters->model, model_state, &adj);
    if (adjusted_voltage) *adjusted_voltage = adj;
    set_saved_magic(model_state);
    return 0;
}

int nrf_fuel_gauge_ext_state_update(enum nrf_fuel_gauge_ext_state_info_type type,
                                     union nrf_fuel_gauge_ext_state_info_data *data)
{
    switch (type) {
    case NRF_FUEL_GAUGE_EXT_STATE_INFO_VBUS_CONNECTED:
        EXT_VBUS = 1;
        return 0;
    case NRF_FUEL_GAUGE_EXT_STATE_INFO_VBUS_DISCONNECTED:
        EXT_VBUS = 0;
        return 0;
    case NRF_FUEL_GAUGE_EXT_STATE_INFO_CHARGE_STATE_CHANGE:
        if (data == 0) return -22;
        if (((const uint8_t *)data)[0] > 5u) return -22;
        EXT_CHARGE_STATE = ((const uint8_t *)data)[0];
        return 0;
    case NRF_FUEL_GAUGE_EXT_STATE_INFO_CHARGE_CURRENT_CORRECTION:
    case NRF_FUEL_GAUGE_EXT_STATE_INFO_DISCHARGE_CURRENT_CORRECTION: {
        if (data == 0) return -22;
        float f = data->current_correction_factor;
        uint32_t b = float_bits(f);
        /* Stock rejects NaN, negative (sign bit), and zero. */
        if ((b & 0x7fffffffu) == 0u) return -22;
        if ((b & 0x80000000u) != 0u) return -22;
        if ((b & 0x7f800000u) == 0x7f800000u && (b & 0x007fffffu) != 0u)
            return -22;
        if (type == NRF_FUEL_GAUGE_EXT_STATE_INFO_CHARGE_CURRENT_CORRECTION)
            __builtin_memcpy(ext_block + 4, &f, 4);
        else
            __builtin_memcpy(ext_block + 8, &f, 4);
        return 0;
    }
    case NRF_FUEL_GAUGE_EXT_STATE_INFO_CHARGE_CURRENT_LIMIT:
    case NRF_FUEL_GAUGE_EXT_STATE_INFO_TERM_CURRENT: {
        if (data == 0) return -22;
        float f = (type == NRF_FUEL_GAUGE_EXT_STATE_INFO_CHARGE_CURRENT_LIMIT)
                      ? data->charge_current_limit
                      : data->charge_term_current;
        if (f == 0.0f) return -22;
        if (float_bits(f) & 0x80000000u) {
            /* already negative: keep for term; for limit also keep if already neg */
        } else {
            f = -f;
        }
        if (type == NRF_FUEL_GAUGE_EXT_STATE_INFO_CHARGE_CURRENT_LIMIT)
            __builtin_memcpy(ext_block + 0x0C, &f, 4);
        else
            __builtin_memcpy(ext_block + 0x10, &f, 4);
        return 0;
    }
    default:
        return -22;
    }
}

float nrf_fuel_gauge_process(float voltage, float current, float temperature,
                             float seconds, struct nrf_fuel_gauge_state_info *state)
{
    float i_corr;
    float pair[2];
    uint32_t ibits = float_bits(current);
    int charging = ((ibits & 0x80000000u) != 0u) || (EXT_VBUS != 0);
    if (charging) {
        float limit;
        __builtin_memcpy(&limit, ext_block + 0x0C, 4);
        pair[0] = bits_float(fg_aux[1]); /* 0x20004514 */
        pair[1] = bits_float(fg_aux[3]); /* 0x2000451c */
        uint32_t lb = float_bits(limit);
        int limit_nan = ((lb & 0x7f800000u) == 0x7f800000u && (lb & 0x007fffffu) != 0u);
        if (limit_nan || EXT_CHARGE_STATE != NRF_FUEL_GAUGE_CHARGE_STATE_CC) {
            float factor;
            __builtin_memcpy(&factor, ext_block + 4, 4);
            i_corr = current * factor;
        } else {
            i_corr = limit;
        }
    } else {
        float factor;
        __builtin_memcpy(&factor, ext_block + 8, 4);
        i_corr = current * factor;
        pair[0] = bits_float(fg_aux[2]); /* 0x20004518 */
        pair[1] = bits_float(fg_aux[4]); /* 0x20004520 */
    }
    nrf_model_tte_params_58eab0(model_state, pair);

    uint8_t opt[0x70];
    if (EXT_CHARGE_STATE == NRF_FUEL_GAUGE_CHARGE_STATE_COMPLETE) {
        __builtin_memcpy(opt, fg_default_opt, 0x6C);
        /* Preserve a window of model state, memset 0xE0, re-init. */
        uint8_t saved[0x28];
        __builtin_memcpy(saved, model_state + 0x54, 0x20);
        __builtin_memcpy(saved + 0x20, model_state + 0x74, 4);
        void *modelptr;
        __builtin_memcpy(&modelptr, model_state + 0xE0, 4);
        __builtin_memset(model_state, 0, 0xE0);
        /* The stock path kept 0x54..0x74 on its stack and then called init;
         * it did not write those bytes back first. The init function
         * rebuilds the state. */
        float adj = 0.0f;
        nrf_model_init_43a1b0(voltage, i_corr, temperature, opt, modelptr, model_state, &adj);
        (void)saved;
        EXT_CHARGE_STATE = 0;
        __builtin_memcpy(model_state + 0xE0, &modelptr, 4);
    }

    float soc_frac = 0.0f;
    uint8_t scratch[8];
    /* 5th argument is also the first core-output window (yhat, r0, ?, T). */
    __builtin_memset(opt, 0, sizeof opt);
    void *modelptr;
    __builtin_memcpy(&modelptr, model_state + 0xE0, 4);
    nrf_model_process_43a698(voltage, i_corr, temperature, seconds,
                               model_state, modelptr, &soc_frac, scratch, opt);
    float soc = soc_frac * 100.0f;
    if (state != 0) {
        /* Stock copies four floats from the process scratch window and soc_raw. */
        /* After the call, the wrapper loaded sp+48,52,60 and i_corr into a
         * vector stored at state+0, and soc at +0x10. We fill from the
         * documented state_info fields as the wrapper did: first four
         * floats yhat, r0, T_truncated, i_corrected come from the core
         * outputs placed at the opt/scratch area. The stock window was:
         *   [sp+48]=yhat? actually from local_98 start after process...
         * Safer: read the same layout the core writes through r3/opt if
         * we can. The golden compared yhat/r0/T/i_corr from STATE_INFO
         * after process; those were written by the stock wrapper. */
        /* Re-run the documented store: yhat, r0, T, i at the start of the
         * 16-byte vector the wrapper built from [sp+48], [sp+52], [sp+60]
         * and s16 (i_corr). Without the exact stack map from the core we
         * copy i_corrected surely, and leave a best-effort for the rest
         * after inspecting core outputs below. */
        /* Stock process wrapper: state[0:16] = (buf[0], buf[1], buf[3], i_corr). */
        __builtin_memcpy(&state->yhat, opt + 0, 4);
        __builtin_memcpy(&state->r0, opt + 4, 4);
        __builtin_memcpy(&state->T_truncated, opt + 12, 4);
        state->i_corrected = i_corr;
        state->soc_raw = soc;
    }
    return soc;
}

float nrf_fuel_gauge_tte_get(void)
{
    return nrf_model_tte_cached_58eabc((const struct nrf_model_state_tte_view *)model_state);
}

float nrf_fuel_gauge_ttf_get(void)
{
    float term;
    __builtin_memcpy(&term, ext_block + 0x10, 4);
    uint32_t b = float_bits(term);
    if ((b & 0x7f800000u) == 0x7f800000u && (b & 0x007fffffu) != 0u)
        return __builtin_nanf("");
    uint8_t cs = EXT_CHARGE_STATE;
    if (cs <= 1u) return __builtin_nanf("");
    if (cs == 4u) {
        void *modelptr;
        __builtin_memcpy(&modelptr, model_state + 0xE0, 4);
        return nrf_model_ttf_58eac4(model_state, 0, modelptr);
    }
    if (cs == 2u || cs == 3u) {
        void *modelptr;
        __builtin_memcpy(&modelptr, model_state + 0xE0, 4);
        return nrf_model_ttf_58eac4(model_state, 1, modelptr);
    }
    return __builtin_nanf("");
}
