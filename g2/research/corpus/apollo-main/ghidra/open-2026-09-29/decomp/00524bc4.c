
undefined4
FT_GlyphLoader_Reset(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  uVar1 = *param_1;
  ft_mem_free(uVar1,param_1[6]);
  param_1[6] = 0;
  ft_mem_free(uVar1,param_1[7]);
  param_1[7] = 0;
  ft_mem_free(uVar1,param_1[8]);
  param_1[8] = 0;
  ft_mem_free(uVar1,param_1[10]);
  param_1[10] = 0;
  ft_mem_free(uVar1,param_1[0xd]);
  param_1[0xd] = 0;
  param_1[0xb] = 0;
  param_1[1] = 0;
  param_1[2] = 0;
  param_1[3] = 0;
  FT_GlyphLoader_Rewind(param_1);
  return param_4;
}

