
longlong af_dummy_hints_init(int param_1,int param_2,undefined4 param_3,uint param_4)

{
  af_glyph_hints_rescale(param_1,param_2);
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)(param_2 + 8);
  *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(param_2 + 0xc);
  *(undefined4 *)(param_1 + 8) = *(undefined4 *)(param_2 + 0x10);
  *(undefined4 *)(param_1 + 0x10) = *(undefined4 *)(param_2 + 0x14);
  return (ulonglong)param_4 << 0x20;
}

