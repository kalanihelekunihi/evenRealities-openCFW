
undefined4 gx_analog_set_pga_itrim(uint param_1)

{
  *(uint *)(DAT_10205e4c + 8) =
       *(uint *)(DAT_10205e4c + 8) & 0xc0 |
       (param_1 < 0x3f) * param_1 + (uint)(param_1 >= 0x3f) * 0x3f & 0xff;
  return 0;
}

