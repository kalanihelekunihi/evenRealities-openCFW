#include <stdint.h>

/* Candidate for stock 0x5918cc. Lower numerical providers remain explicit. */
extern uint64_t g2_audio_dsp_i64_to_double_bits(int64_t value);
extern double g2_audio_dsp_sqrt(double value);
extern double g2_audio_dsp_delay_to_angle(double delay, double spacing, double speed);

static double from_bits(uint64_t bits) {
    union { uint64_t bits; double value; } u;
    u.bits = bits;
    return u.value;
}
static uint64_t to_bits(double value) {
    union { uint64_t bits; double value; } u;
    u.value = value;
    return u.bits;
}
static double i64_to_double(int64_t value) {
    return from_bits(g2_audio_dsp_i64_to_double_bits(value));
}
static double absolute(double value) {
    return from_bits(to_bits(value) & UINT64_C(0x7fffffffffffffff));
}
static inline int stock_less(double a, double b) {
    int less;
    __asm__ volatile (
        "vcmp.f64 %P1, %P2\n\t"
        "vmrs APSR_nzcv, FPSCR\n\t"
        "ite mi\n\t"
        "movmi %0, #1\n\t"
        "movpl %0, #0"
        : "=r"(less) : "w"(a), "w"(b) : "cc"
    );
    return less;
}
static inline int stock_positive(double a) {
    int positive;
    __asm__ volatile (
        "vcmp.f64 %P1, #0\n\t"
        "vmrs APSR_nzcv, FPSCR\n\t"
        "ite gt\n\t"
        "movgt %0, #1\n\t"
        "movle %0, #0"
        : "=r"(positive) : "w"(a) : "cc"
    );
    return positive;
}

void g2_audio_dsp_correlate(const int16_t *left, const int16_t *right,
                            int32_t count, int32_t limit, double sample_rate,
                            double spacing, double speed, double rms_floor,
                            double quality_floor, double *angle, double *delay,
                            double *quality, double *max_rms) {
    const double nan = from_bits(UINT64_C(0x7ff8000000000000));
    if (count < 1) {
        if (angle) *angle = nan;
        if (delay) *delay = nan;
        if (quality) *quality = 0.0;
        if (max_rms) *max_rms = 0.0;
        return;
    }
    int64_t left_energy = 0, right_energy = 0;
    for (int32_t i = 0; i < count; ++i) {
        int32_t l = left[i], r = right[i];
        left_energy += (int64_t)l * l;
        right_energy += (int64_t)r * r;
    }
    double left_rms = g2_audio_dsp_sqrt(i64_to_double(left_energy) / (double)count);
    double right_rms = g2_audio_dsp_sqrt(i64_to_double(right_energy) / (double)count);
    double maximum = stock_less(right_rms, left_rms) ? left_rms : right_rms;
    if (max_rms) *max_rms = maximum;
    if (stock_less(maximum, rms_floor)) {
        if (angle) *angle = nan;
        if (delay) *delay = nan;
        if (quality) *quality = 0.0;
        return;
    }
    if (limit < 1) limit = 8;
    int64_t best = INT64_MIN;
    int32_t best_lag = 0;
    double sum_abs = 0.0;
    for (int32_t lag = -limit; lag <= limit; ++lag) {
        int64_t corr = 0;
        if (lag < 0) {
            for (int32_t i = 0; i < count + lag; ++i)
                corr += (int64_t)right[i] * left[i-lag];
        } else {
            for (int32_t i = 0; i < count - lag; ++i)
                corr += (int64_t)left[i] * right[i+lag];
        }
        if (corr > best) { best = corr; best_lag = lag; }
        sum_abs += absolute(i64_to_double(corr));
    }
    double mean_abs = sum_abs / (double)(2 * limit + 1);
    double score = stock_positive(mean_abs)
        ? i64_to_double(best) / (mean_abs + 1e-12) : 0.0;
    if (quality) *quality = score;
    if (stock_less(score, quality_floor)) {
        if (angle) *angle = nan;
        if (delay) *delay = nan;
        return;
    }
    double lag_seconds = (double)best_lag / sample_rate;
    double radians = g2_audio_dsp_delay_to_angle(lag_seconds, spacing, speed);
    if (angle) *angle = radians;
    if (delay) *delay = lag_seconds;
}
