
int FT_GlyphLoader_CheckSubGlyphs
              (undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  uint uVar2;
  int local_18;
  undefined4 uStack_14;
  
  local_18 = 0;
  uVar2 = param_2 + param_1[0x15] + param_1[0xc];
  if ((uint)param_1[3] < uVar2) {
    uVar2 = uVar2 + 1 & 0xfffffffe;
    uStack_14 = param_4;
    uVar1 = ft_mem_realloc(*param_1,0x20,param_1[3],uVar2,param_1[0xd],&local_18);
    param_1[0xd] = uVar1;
    if (local_18 == 0) {
      param_1[3] = uVar2;
      FT_GlyphLoader_Adjust_Subglyphs(param_1);
    }
  }
  return local_18;
}

