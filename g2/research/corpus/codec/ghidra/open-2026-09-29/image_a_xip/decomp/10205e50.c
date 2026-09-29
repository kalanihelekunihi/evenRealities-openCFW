
undefined4 gx_analog_set_pga_bypass(uint param_1)

{
  *(uint *)(DAT_10205e64 + 8) = *(uint *)(DAT_10205e64 + 8) & 0xbf | (param_1 & 3) << 6;
  return 0;
}

