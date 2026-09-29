
undefined4
tt_size_done_bytecode(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  uVar1 = *(undefined4 *)(*param_1 + 100);
  if (param_1[0x4b] != 0) {
    TT_Done_Context(param_1[0x4b]);
    param_1[0x4b] = 0;
  }
  ft_mem_free(uVar1,param_1[0x3f]);
  param_1[0x3f] = 0;
  param_1[0x3e] = 0;
  ft_mem_free(uVar1,param_1[0x41]);
  param_1[0x41] = 0;
  *(undefined2 *)(param_1 + 0x40) = 0;
  tt_glyphzone_done(param_1 + 0x42);
  ft_mem_free(uVar1,param_1[0x21]);
  param_1[0x21] = 0;
  ft_mem_free(uVar1,param_1[0x24]);
  param_1[0x24] = 0;
  param_1[0x1f] = 0;
  param_1[0x20] = 0;
  param_1[0x22] = 0;
  param_1[0x23] = 0;
  param_1[0x25] = 0;
  param_1[0x26] = 0;
  param_1[0x4c] = -1;
  param_1[0x4d] = -1;
  return param_4;
}

