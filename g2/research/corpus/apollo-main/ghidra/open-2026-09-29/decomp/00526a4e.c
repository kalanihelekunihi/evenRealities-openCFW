
undefined4
ft_recompute_scaled_metrics(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = FT_MulFix((int)*(short *)(param_1 + 0x46),*(undefined4 *)(param_2 + 8));
  *(uint *)(param_2 + 0xc) = iVar1 + 0x3fU & 0xffffffc0;
  uVar2 = FT_MulFix((int)*(short *)(param_1 + 0x48),*(undefined4 *)(param_2 + 8));
  *(uint *)(param_2 + 0x10) = uVar2 & 0xffffffc0;
  iVar1 = FT_MulFix((int)*(short *)(param_1 + 0x4a),*(undefined4 *)(param_2 + 8));
  *(uint *)(param_2 + 0x14) = iVar1 + 0x20U & 0xffffffc0;
  iVar1 = FT_MulFix((int)*(short *)(param_1 + 0x4c),*(undefined4 *)(param_2 + 4));
  *(uint *)(param_2 + 0x18) = iVar1 + 0x20U & 0xffffffc0;
  return param_4;
}

