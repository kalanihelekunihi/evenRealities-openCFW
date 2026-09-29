
int FT_GlyphLoader_CreateExtra
              (undefined4 *param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  uVar1 = ft_mem_realloc(*param_1,8,0,param_1[1] << 1,0,&local_10);
  param_1[10] = uVar1;
  if (local_10 == 0) {
    *(undefined1 *)(param_1 + 4) = 1;
    param_1[0xb] = param_1[10] + param_1[1] * 8;
    FT_GlyphLoader_Adjust_Points(param_1);
  }
  return local_10;
}

