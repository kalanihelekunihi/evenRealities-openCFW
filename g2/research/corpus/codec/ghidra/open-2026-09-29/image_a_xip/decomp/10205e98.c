
undefined4 gx_analog_set_adc_out_at_clk(uint param_1)

{
  *(uint *)(DAT_10205eac + 0x14) = *(uint *)(DAT_10205eac + 0x14) & 0xfd | (param_1 & 0x7f) << 1;
  return 0;
}

