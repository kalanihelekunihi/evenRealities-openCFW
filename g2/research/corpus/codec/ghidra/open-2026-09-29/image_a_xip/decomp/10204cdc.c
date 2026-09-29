
undefined4 aout_set_fixed_src(undefined4 param_1,uint param_2)

{
  uRam00000010 = (param_2 & 0x7fff) << 8 | uRam00000010 & 0xff000000 | 0x80000000;
  return 0;
}

