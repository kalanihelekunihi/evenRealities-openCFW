
undefined4
af_glyph_hints_done(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if ((param_1 != (int *)0x0) && (*param_1 != 0)) {
    iVar1 = *param_1;
    for (iVar2 = 0; iVar2 < 2; iVar2 = iVar2 + 1) {
      param_1[iVar2 * 0x151 + 0xb] = 0;
      param_1[iVar2 * 0x151 + 0xc] = 0;
      if ((int *)param_1[iVar2 * 0x151 + 0xd] != param_1 + iVar2 * 0x151 + 0x12) {
        ft_mem_free(iVar1,param_1[iVar2 * 0x151 + 0xd]);
        param_1[iVar2 * 0x151 + 0xd] = 0;
      }
      param_1[iVar2 * 0x151 + 0xe] = 0;
      param_1[iVar2 * 0x151 + 0xf] = 0;
      if ((int *)param_1[iVar2 * 0x151 + 0x10] != param_1 + iVar2 * 0x151 + 0xd8) {
        ft_mem_free(iVar1,param_1[iVar2 * 0x151 + 0x10]);
        param_1[iVar2 * 0x151 + 0x10] = 0;
      }
    }
    if ((int *)param_1[10] != param_1 + 0x2b2) {
      ft_mem_free(iVar1,param_1[10]);
      param_1[10] = 0;
    }
    param_1[8] = 0;
    param_1[9] = 0;
    if ((int *)param_1[7] != param_1 + 0x2ba) {
      ft_mem_free(iVar1,param_1[7]);
      param_1[7] = 0;
    }
    param_1[5] = 0;
    param_1[6] = 0;
    *param_1 = 0;
  }
  return param_4;
}

