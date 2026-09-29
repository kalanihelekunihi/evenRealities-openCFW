
undefined8 af_cjk_hints_compute_blue_edges(int param_1,int param_2,uint param_3)

{
  short *psVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  undefined4 *puVar7;
  undefined4 uVar8;
  short *psVar9;
  int iVar10;
  uint uVar11;
  int *piVar12;
  
  param_1 = param_1 + (param_3 & 0xff) * 0x544;
  psVar9 = *(short **)(param_1 + 0x40);
  psVar1 = psVar9 + *(int *)(param_1 + 0x38) * 0x16;
  iVar2 = param_2 + (param_3 & 0xff) * 0x1c58;
  puVar7 = (undefined4 *)(iVar2 + 0x2c);
  uVar8 = *puVar7;
  iVar3 = FT_MulFix(*(uint *)(param_2 + 0x28) / 0x28,uVar8);
  if (0x20 < iVar3) {
    iVar3 = 0x20;
  }
  for (; psVar9 < psVar1; psVar9 = psVar9 + 0x16) {
    piVar6 = (int *)0x0;
    iVar10 = iVar3;
    for (uVar11 = 0; uVar11 < *(uint *)(iVar2 + 0x104); uVar11 = uVar11 + 1) {
      piVar12 = puVar7 + uVar11 * 7 + 0x37;
      if (((int)((uint)*(byte *)(puVar7 + uVar11 * 7 + 0x3d) << 0x1f) < 0) &&
         ((uint)(*(char *)((int)psVar9 + 0xd) == *(char *)(param_1 + 0x44)) !=
          (puVar7[uVar11 * 7 + 0x3d] & 3) >> 1)) {
        if ((int)*psVar9 - puVar7[uVar11 * 7 + 0x3a] < 0) {
          iVar4 = puVar7[uVar11 * 7 + 0x3a] - (int)*psVar9;
        }
        else {
          iVar4 = (int)*psVar9 - puVar7[uVar11 * 7 + 0x3a];
        }
        if ((int)*psVar9 - *piVar12 < 0) {
          iVar5 = *piVar12 - (int)*psVar9;
        }
        else {
          iVar5 = (int)*psVar9 - *piVar12;
        }
        if (iVar4 < iVar5) {
          piVar12 = puVar7 + uVar11 * 7 + 0x3a;
        }
        iVar4 = (int)*psVar9 - *piVar12;
        if (iVar4 < 0) {
          iVar4 = -iVar4;
        }
        iVar4 = FT_MulFix(iVar4,uVar8);
        if (iVar4 < iVar10) {
          piVar6 = piVar12;
          iVar10 = iVar4;
        }
      }
    }
    if (piVar6 != (int *)0x0) {
      *(int **)(psVar9 + 10) = piVar6;
    }
  }
  return CONCAT44(psVar1,param_1 + 0x2c);
}

