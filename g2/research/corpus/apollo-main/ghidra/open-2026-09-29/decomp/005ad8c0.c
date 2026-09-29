
undefined4 cff_index_done(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (*param_1 != 0) {
    uVar1 = *(undefined4 *)(*param_1 + 0x1c);
    if (param_1[8] != 0) {
      FT_Stream_ReleaseFrame(*param_1,param_1 + 8);
    }
    ft_mem_free(uVar1,param_1[7]);
    param_1[7] = 0;
    FUN_0043c0e4(param_1,0x24,0);
  }
  return param_4;
}

