
undefined4 gx8002_audio_input_sadc(int param_1)

{
  func_0x10025080(7,1);
  gx_analog_set_adc_rstn(0);
  gx_analog_set_pga_bypass(~(param_1 != 0));
  gx_analog_set_pga_enable(param_1);
  gx_analog_set_adc_sample_clk_sel(1);
  gx_analog_set_adc_out_at_clk(0);
  gx_analog_set_adc_in_sel(param_1 == 0);
  gx_analog_set_pga_itrim(0);
  gx_analog_set_adc_rstn(1);
  uRam00000000 = uRam00000000 & 0xffffffbf | 0x40;
  *DAT_10203e78 = *DAT_10203e78 | 1;
  return 0;
}

