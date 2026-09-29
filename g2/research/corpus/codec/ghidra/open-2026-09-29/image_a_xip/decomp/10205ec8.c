
undefined4 gx_analog_set_adc_rstn(uint param_1)

{
  *(uint *)(DAT_10205edc + 0x14) = *(uint *)(DAT_10205edc + 0x14) & 0xf7 | (param_1 & 0x1f) << 3;
  return 0;
}

