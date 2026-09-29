
void FT_Select_Metrics(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  short *psVar3;
  
  iVar1 = *(int *)(param_1 + 0x58);
  psVar3 = (short *)(*(int *)(param_1 + 0x20) + param_2 * 0x10);
  *(undefined2 *)(iVar1 + 0xc) = (short)(*(int *)(psVar3 + 4) + 0x20 >> 6);
  *(short *)(iVar1 + 0xe) = (short)(*(int *)(psVar3 + 6) + 0x20 >> 6);
  if ((int)((uint)*(byte *)(param_1 + 8) << 0x1f) < 0) {
    uVar2 = FT_DivFix(*(undefined4 *)(psVar3 + 4),*(undefined2 *)(param_1 + 0x44));
    *(undefined4 *)(iVar1 + 0x10) = uVar2;
    uVar2 = FT_DivFix(*(undefined4 *)(psVar3 + 6),*(undefined2 *)(param_1 + 0x44));
    *(undefined4 *)(iVar1 + 0x14) = uVar2;
    ft_recompute_scaled_metrics(param_1,(undefined2 *)(iVar1 + 0xc));
  }
  else {
    *(undefined4 *)(iVar1 + 0x10) = 0x10000;
    *(undefined4 *)(iVar1 + 0x14) = 0x10000;
    *(undefined4 *)(iVar1 + 0x18) = *(undefined4 *)(psVar3 + 6);
    *(undefined4 *)(iVar1 + 0x1c) = 0;
    *(int *)(iVar1 + 0x20) = (int)*psVar3 << 6;
    *(undefined4 *)(iVar1 + 0x24) = *(undefined4 *)(psVar3 + 4);
  }
  return;
}

