
int FT_GlyphLoader_CheckPoints(undefined4 *param_1,int param_2,int param_3,undefined4 param_4)

{
  bool bVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  int local_28;
  undefined4 uStack_24;
  
  uVar4 = *param_1;
  local_28 = 0;
  bVar1 = false;
  uVar3 = param_2 + (int)*(short *)((int)param_1 + 0x3a) + (int)*(short *)((int)param_1 + 0x16);
  uVar5 = param_1[1];
  uStack_24 = param_4;
  if (uVar5 < uVar3) {
    uVar3 = uVar3 + 7 & 0xfffffff8;
    if (0x7fff < uVar3) {
      return 10;
    }
    uVar2 = ft_mem_realloc(uVar4,8,uVar5,uVar3,param_1[6],&local_28);
    param_1[6] = uVar2;
    if (local_28 == 0) {
      uVar2 = ft_mem_realloc(uVar4,1,uVar5,uVar3,param_1[7],&local_28);
      param_1[7] = uVar2;
      if (local_28 != 0) goto LAB_00524d4c;
      bVar1 = false;
    }
    else {
LAB_00524d4c:
      bVar1 = true;
    }
    if (bVar1) goto LAB_00524df2;
    if (*(char *)(param_1 + 4) != '\0') {
      uVar2 = ft_mem_realloc(uVar4,8,uVar5 << 1,uVar3 << 1,param_1[10],&local_28);
      param_1[10] = uVar2;
      if (local_28 != 0) goto LAB_00524df2;
      FUN_00439710(param_1[10] + uVar3 * 8,param_1[10] + uVar5 * 8,uVar5 << 3);
      param_1[0xb] = param_1[10] + uVar3 * 8;
    }
    bVar1 = true;
    param_1[1] = uVar3;
  }
  uVar3 = param_3 + (int)*(short *)(param_1 + 5) + (int)*(short *)(param_1 + 0xe);
  if ((uint)param_1[2] < uVar3) {
    uVar3 = uVar3 + 3 & 0xfffffffc;
    if (0x7fff < uVar3) {
      return 10;
    }
    uVar4 = ft_mem_realloc(uVar4,2,param_1[2],uVar3,param_1[8],&local_28);
    param_1[8] = uVar4;
    if (local_28 != 0) goto LAB_00524df2;
    bVar1 = true;
    param_1[2] = uVar3;
  }
  if (bVar1) {
    FT_GlyphLoader_Adjust_Points(param_1);
  }
LAB_00524df2:
  if (local_28 != 0) {
    FT_GlyphLoader_Reset(param_1);
  }
  return local_28;
}

