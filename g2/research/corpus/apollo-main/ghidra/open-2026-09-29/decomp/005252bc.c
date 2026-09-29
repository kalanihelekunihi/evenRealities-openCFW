
undefined4 ft_glyphslot_clear(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  ft_glyphslot_free_bitmap(param_1);
  FUN_0043c0e4(param_1 + 0x18,0x20,0);
  FUN_0043c0e4(param_1 + 0x6c,0x14,0);
  *(undefined4 *)(param_1 + 0x50) = 0;
  *(undefined4 *)(param_1 + 0x4c) = 0;
  *(undefined4 *)(param_1 + 0x54) = 0;
  *(undefined1 *)(param_1 + 0x5e) = 0;
  *(undefined4 *)(param_1 + 100) = 0;
  *(undefined4 *)(param_1 + 0x68) = 0;
  *(undefined4 *)(param_1 + 0x80) = 0;
  *(undefined4 *)(param_1 + 0x84) = 0;
  *(undefined4 *)(param_1 + 0x88) = 0;
  *(undefined4 *)(param_1 + 0x8c) = 0;
  *(undefined4 *)(param_1 + 0x98) = 0;
  *(undefined4 *)(param_1 + 0x48) = 0;
  *(undefined4 *)(param_1 + 0x38) = 0;
  *(undefined4 *)(param_1 + 0x3c) = 0;
  *(undefined4 *)(param_1 + 0x90) = 0;
  *(undefined4 *)(param_1 + 0x94) = 0;
  return param_4;
}

