
undefined4 gx_analog_set_pga_enable(uint param_1)

{
  *(uint *)(DAT_10008090 + 0x10) = *(uint *)(DAT_10008090 + 0x10) & 0xbf | (param_1 & 3) << 6;
  return 0;
}

