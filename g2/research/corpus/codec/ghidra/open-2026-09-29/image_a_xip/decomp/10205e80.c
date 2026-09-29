
undefined4 gx_analog_set_adc_sample_clk_sel(uint param_1)

{
  *(uint *)(DAT_10205e94 + 0x14) = param_1 & 0xff | *(uint *)(DAT_10205e94 + 0x14) & 0xfe;
  return 0;
}

