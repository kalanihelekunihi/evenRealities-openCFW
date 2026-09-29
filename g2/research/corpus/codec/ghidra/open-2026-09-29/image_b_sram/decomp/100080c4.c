
undefined4 gx_analog_set_adc_in_sel(uint param_1)

{
  *(uint *)(DAT_100080d8 + 0x14) = *(uint *)(DAT_100080d8 + 0x14) & 0xfb | (param_1 & 0x3f) << 2;
  return 0;
}

