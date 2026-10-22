/* Front-microphone audio analysis, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\audio\service_algo.c (module tag
 * "svc.audio.algo"). Native 0x5915dc..0x591c8b; literal pool 0x591c90..0x591d13.
 *
 * One 3200-byte block of interleaved 16-bit stereo (800 L/R pairs) produces two
 * stream metadata values:
 *   - SVC_SSRProcess: energy ratio low16((cur + 1) / (base + 1)), where cur is
 *     the mean of the left/right mean squares of this block and base the mean of
 *     a 10-entry ring of per-ISR mean squares (service_algo_energy_window_update,
 *     fed from the PDM DMA ISR).
 *   - service_algo_source_angle: direction of arrival in degrees from the
 *     integer cross-correlation lag (|lag| <= 10 at fs = 16000, mic spacing
 *     0.14 m, c = 343 m/s): asin(clamp(lag / fs * c / d, -1, 1)) * 180 / pi.
 *
 * All doubles use the VFP calling convention (D0..D4), like the IAR build;
 * compile with a double-precision FPU (profile g2-apollo-main-20). */
#include <stdint.h>
#include <stddef.h>

#pragma STDC FP_CONTRACT OFF

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))

#define ALGO_PAIRS 800u
#define ALGO_BLOCK_BYTES 0xc80u /* 800 stereo pairs */
#define ALGO_CHANNEL_BYTES 0x640u
#define ALGO_WINDOW 10u
#define ALGO_MAX_LAG 10
#define ALGO_DEFAULT_LAG 8

#define ALGO_FS 16000.0          /* ROM 0x591ce8 */
#define ALGO_MIC_SPACING 0.14    /* ROM 0x591ce0, metres */
#define ALGO_SOUND_SPEED 343.0   /* ROM 0x591cd8, m/s */
#define ALGO_CORR_EPSILON 1e-12  /* ROM 0x591cc8 */
#define ALGO_DEG_PER_HALF_TURN 180.0          /* ROM 0x591cf8 */
#define ALGO_PI 3.141592653589793             /* ROM 0x591d0c */
#define ALGO_QNAN_HIGH 0x7ff80000u            /* ROM 0x591d08 */

extern int16_t g2_algo_left_pcm[ALGO_PAIRS];   /* RAM 0x20375400 */
extern int16_t g2_algo_right_pcm[ALGO_PAIRS];  /* RAM 0x20375a40 */
extern int16_t g2_algo_front_pcm[ALGO_PAIRS];  /* RAM 0x20376080, L/2 + R/2 */
extern uint64_t g2_algo_left_energy;           /* RAM 0x20074168, mean square */
extern uint64_t g2_algo_right_energy;          /* RAM 0x20074170, mean square */
extern uint64_t g2_algo_window_index;          /* RAM 0x20074178 */
extern uint64_t g2_algo_energy_window[ALGO_WINDOW]; /* RAM 0x20072d08 */

extern void audio_uart_buffer_zero(void *dst, uint32_t size, uint32_t value); /* 0x43c0e4 memset */
extern IAR_VFP double iar_asin_43c260(double x);
extern IAR_VFP double iar_sqrt_59c800(double x); /* VSQRT, EDOM for x < 0 */
extern __attribute__((pcs("aapcs"))) double __aeabi_l2d(int64_t value);         /* RTABI, soft-float r1:r0 -> r1:r0; 0x59c7ac */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "svc.audio.algo"; /* ROM 0x788670 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_algo.c"; /* ROM 0x7052b4 */
static const char preprocess_fn[] = "algo_front_data_preprocess"; /* ROM 0x770b14 */
static const char bad_size[] = "Invalid front pcm data size: %d"; /* ROM 0x764850 */
static const char bad_size_short[] = "[svc.audio.algo]Invalid front pcm data size: %d"; /* ROM 0x737b74 */
static const char ssr_fn[] = "SVC_SSRProcess"; /* ROM 0x788680 */
static const char bad_params[] = "invalid params, front_pcm_data=%p data_size=%u"; /* ROM 0x737ba4 */
static const char bad_params_short[] =
    "[svc.audio.algo]invalid params, front_pcm_data=%p data_size=%u"; /* ROM 0x70e7a4 */
static const char wait_window[] = "wait window: left_mean_abs=%llu right_mean_abs=%llu"; /* ROM 0x72cd9c */
static const char wait_window_short[] =
    "[svc.audio.algo]wait window: left_mean_abs=%llu right_mean_abs=%llu"; /* ROM 0x7052f8 */

void service_algo_front_buffer_get(int16_t **buffer, uint32_t *bytes)
{
    *buffer = g2_algo_front_pcm;
    *bytes = ALGO_CHANNEL_BYTES;
}

/* Split one interleaved block into left/right/mono and compute the per-channel
 * mean squares. The loop always covers 800 pairs; size is only validated. */
int32_t algo_front_data_preprocess(const int16_t *pcm, uint32_t bytes)
{
    if (pcm == NULL || (bytes & 3u) != 0u || bytes > ALGO_BLOCK_BYTES) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, preprocess_fn, 43u, bad_size, bytes);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04400000u, bad_size_short, bad_size_short, bytes);
        return -1;
    }
    int16_t *left = g2_algo_left_pcm;
    int16_t *right = g2_algo_right_pcm;
    int16_t *front = g2_algo_front_pcm;
    audio_uart_buffer_zero(left, ALGO_CHANNEL_BYTES, 0u);
    audio_uart_buffer_zero(right, ALGO_CHANNEL_BYTES, 0u);
    audio_uart_buffer_zero(front, ALGO_CHANNEL_BYTES, 0u);
    g2_algo_left_energy = 0u;
    g2_algo_right_energy = 0u;
    for (uint32_t i = 0u; i < ALGO_PAIRS; i++) {
        left[i] = pcm[2u * i];
        right[i] = pcm[2u * i + 1u];
        front[i] = (int16_t)(left[i] / 2 + right[i] / 2);
        g2_algo_left_energy += (uint64_t)(int64_t)((int32_t)left[i] * left[i]);
        g2_algo_right_energy += (uint64_t)(int64_t)((int32_t)right[i] * right[i]);
    }
    g2_algo_left_energy /= ALGO_PAIRS;
    g2_algo_right_energy /= ALGO_PAIRS;
    return 0;
}

/* Sound-strength ratio of this block against the ISR energy window. */
uint16_t SVC_SSRProcess(const int16_t *pcm, uint32_t bytes)
{
    if (pcm == NULL || bytes == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, ssr_fn, 99u, bad_params, pcm, bytes);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04800000u, bad_params_short, bad_params_short, pcm, bytes);
        return 0u;
    }
    if (g2_algo_left_energy == 0u || g2_algo_right_energy == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, ssr_fn, 105u, wait_window,
                               g2_algo_left_energy, g2_algo_right_energy);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x10800000u, wait_window_short, wait_window_short,
                                      g2_algo_left_energy, g2_algo_right_energy);
        return 0u;
    }
    uint64_t current = (g2_algo_left_energy + g2_algo_right_energy) >> 1;
    uint64_t sum = 0u;
    for (int32_t i = 0; i < (int32_t)ALGO_WINDOW; i++)
        sum += g2_algo_energy_window[i];
    uint64_t baseline = sum / ALGO_WINDOW;
    return (uint16_t)((current + 1u) / (baseline + 1u));
}

IAR_VFP double service_algo_quiet_nan(void)
{
    union {
        uint32_t word[2];
        double value;
    } nan = {{0u, ALGO_QNAN_HIGH}};
    return nan.value;
}

/* Clamp to [low, high]; NaN passes through. */
IAR_VFP double service_algo_float_hook(double x, double low, double high)
{
    if (x < low)
        return low;
    if (high < x)
        return high;
    return x;
}

/* Arrival angle in radians for a time difference tau (seconds). */
IAR_VFP double service_algo_delay_to_angle(double tau, double spacing, double speed)
{
    return iar_asin_43c260(service_algo_float_hook(tau * speed / spacing, -1.0, 1.0));
}

/* Integer cross-correlation of a against b over lags -max_lag..max_lag (8 when
 * max_lag < 1). Outputs: angle (radians) and tau (seconds) of the best lag, the
 * normalised peak (best / (mean |corr| + 1e-12)) and the larger channel RMS.
 * Below either threshold angle and tau are quiet NaNs. Ties keep the earliest
 * (most negative) lag. */
IAR_VFP void service_algo_cross_correlation(double fs, double spacing, double speed,
                                            double min_rms, double min_corr,
                                            const int16_t *a, const int16_t *b,
                                            int32_t n, int32_t max_lag,
                                            double *angle, double *tau,
                                            double *corr, double *rms)
{
    if (n < 1) {
        if (angle != NULL)
            *angle = service_algo_quiet_nan();
        if (tau != NULL)
            *tau = service_algo_quiet_nan();
        if (corr != NULL)
            *corr = 0.0;
        if (rms != NULL)
            *rms = 0.0;
        return;
    }
    int64_t sum_a = 0;
    int64_t sum_b = 0;
    for (int32_t i = 0; i < n; i++) {
        sum_a += (int64_t)a[i] * (int64_t)a[i];
        sum_b += (int64_t)b[i] * (int64_t)b[i];
    }
    /* Stock converts the int64 energy sums with __aeabi_l2d (0x59c7ac). Call it
     * explicitly: clang proves the sums non-negative and would otherwise emit
     * __aeabi_ul2d, which the stock runtime does not contain. */
    double rms_a = n >= 1 ? iar_sqrt_59c800(__aeabi_l2d(sum_a) / (double)n) : 0.0;
    double rms_b = n >= 1 ? iar_sqrt_59c800(__aeabi_l2d(sum_b) / (double)n) : 0.0;
    double level = rms_a;
    if (!(rms_b < rms_a))
        level = rms_b;
    if (rms != NULL)
        *rms = level;
    if (level < min_rms) {
        if (angle != NULL)
            *angle = service_algo_quiet_nan();
        if (tau != NULL)
            *tau = service_algo_quiet_nan();
        if (corr != NULL)
            *corr = 0.0;
        return;
    }

    if (max_lag < 1)
        max_lag = ALGO_DEFAULT_LAG;
    int32_t count = 2 * max_lag + 1;
    int64_t best = INT64_MIN;
    int32_t best_lag = 0; /* ROM 0x591cc4 */
    double sum_abs = 0.0;
    for (int32_t lag = -max_lag; lag <= max_lag; lag++) {
        int64_t acc = 0;
        if (lag < 0) {
            int32_t shift = -lag;
            for (int32_t i = 0; i < n - shift; i++)
                acc += (int64_t)b[i] * a[i + shift];
        } else {
            for (int32_t i = 0; i < n - lag; i++)
                acc += (int64_t)b[lag + i] * a[i];
        }
        if (acc > best) {
            best = acc;
            best_lag = lag;
        }
        sum_abs += __builtin_fabs((double)acc);
    }
    double peak = (double)best;
    double mean_abs = count >= 1 ? sum_abs / (double)count : 0.0;
    double normalised = mean_abs > 0.0 ? peak / (mean_abs + ALGO_CORR_EPSILON) : 0.0;
    if (corr != NULL)
        *corr = normalised;
    if (normalised < min_corr) {
        if (angle != NULL)
            *angle = service_algo_quiet_nan();
        if (tau != NULL)
            *tau = service_algo_quiet_nan();
        return;
    }
    double delay = (double)best_lag / fs;
    double result = service_algo_delay_to_angle(delay, spacing, speed);
    if (angle != NULL)
        *angle = result;
    if (tau != NULL)
        *tau = delay;
}

/* Direction of arrival of the last preprocessed block, whole degrees
 * (truncated). The pcm arguments are unused; the split buffers are read. */
int16_t service_algo_source_angle(const int16_t *pcm, uint32_t bytes)
{
    double angle, energy, corr, tau;
    (void)pcm;
    (void)bytes;
    service_algo_cross_correlation(ALGO_FS, ALGO_MIC_SPACING, ALGO_SOUND_SPEED, 0.0, 0.0,
                                   g2_algo_left_pcm, g2_algo_right_pcm, (int32_t)ALGO_PAIRS,
                                   ALGO_MAX_LAG, &angle, &tau, &corr, &energy);
    return (int16_t)(int32_t)(angle * ALGO_DEG_PER_HALF_TURN / ALGO_PI);
}

/* Metadata pair for one front block: [0] energy ratio, [1] angle in degrees. */
int32_t service_algo_process(const int16_t *pcm, uint32_t bytes, uint16_t *ratio, int16_t *angle)
{
    (void)algo_front_data_preprocess(pcm, bytes);
    *ratio = SVC_SSRProcess(pcm, bytes);
    *angle = service_algo_source_angle(pcm, bytes);
    return 0;
}

/* Push the mean square of one mono PCM chunk into the 10-entry window. */
int32_t service_algo_energy_window_update(const int16_t *pcm, uint32_t bytes)
{
    if (pcm == NULL || bytes == 0u)
        return -1;
    uint32_t samples = bytes >> 1;
    uint64_t sum = 0u;
    for (uint32_t i = 0u; i < samples; i++)
        sum += (uint64_t)(int64_t)((int32_t)pcm[i] * pcm[i]);
    g2_algo_energy_window[g2_algo_window_index] = sum / samples;
    g2_algo_window_index = (g2_algo_window_index + 1u) % ALGO_WINDOW;
    return 0;
}
