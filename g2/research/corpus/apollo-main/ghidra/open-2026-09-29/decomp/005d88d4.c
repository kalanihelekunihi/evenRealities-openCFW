
undefined4 FUN_005d88d4(undefined4 *param_1)

{
  undefined4 unaff_r7;
  
  if (param_1 != (undefined4 *)0x0) {
    param_1[1] = 0;
    param_1[0x34] = 0;
    param_1[0x67] = 0;
    param_1[0xe8] = 0;
    param_1[0x169] = 0;
    param_1[0x1ea] = 0;
    ft_mem_free(*param_1);
  }
  return unaff_r7;
}

