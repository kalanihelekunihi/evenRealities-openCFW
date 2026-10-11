/* Stock 0x5918b0: D0=delay, D1=spacing, D2=speed; D0=result.
 * The stock asin body remains an external authenticated provider.
 */
extern double stock_asin(double);
extern double g2_audio_dsp_clamp(double, double, double);

double g2_audio_dsp_delay_to_angle(double delay, double spacing, double speed) {
    double x = (delay * speed) / spacing;
    x = g2_audio_dsp_clamp(x, -1.0, 1.0);
    return stock_asin(x);
}
