
void af_latin_hints_compute_blue_edges(int param_1,int param_2)

{
  short *psVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  short *psVar7;
  uint uVar8;
  uint uVar9;
  int *piVar10;
  uint uVar11;
  bool bVar12;
  
  psVar7 = *(short **)(param_1 + 0x584);
  psVar1 = psVar7 + *(int *)(param_1 + 0x57c) * 0x16;
  puVar2 = (undefined4 *)(param_2 + 0x245c);
  uVar3 = *puVar2;
  for (; psVar7 < psVar1; psVar7 = psVar7 + 0x16) {
    piVar6 = (int *)0x0;
    uVar8 = 0;
    iVar4 = FT_MulFix(*(uint *)(param_2 + 0x28) / 0x28,uVar3);
    if (0x20 < iVar4) {
      iVar4 = 0x20;
    }
    for (uVar9 = 0; uVar9 < *(uint *)(param_2 + 0x2534); uVar9 = uVar9 + 1) {
      piVar10 = puVar2 + uVar9 * 9 + 0x37;
      if ((int)((uint)*(byte *)(puVar2 + uVar9 * 9 + 0x3f) << 0x1f) < 0) {
        bVar12 = (*(byte *)(puVar2 + uVar9 * 9 + 0x3f) & 6) != 0;
        uVar11 = (puVar2[uVar9 * 9 + 0x3f] & 0xf) >> 3;
        if (((*(char *)((int)psVar7 + 0xd) == *(char *)(param_1 + 0x588)) != bVar12) ||
           (uVar11 != 0)) {
          iVar5 = (int)*psVar7 - *piVar10;
          if (iVar5 < 0) {
            iVar5 = -iVar5;
          }
          iVar5 = FT_MulFix(iVar5,uVar3);
          if (iVar5 < iVar4) {
            piVar6 = piVar10;
            uVar8 = uVar11;
            iVar4 = iVar5;
          }
          if (((((int)((uint)*(byte *)(psVar7 + 6) << 0x1f) < 0) && (iVar5 != 0)) && (uVar11 == 0))
             && ((int)*psVar7 < *piVar10 != bVar12)) {
            iVar5 = (int)*psVar7 - puVar2[uVar9 * 9 + 0x3a];
            if (iVar5 < 0) {
              iVar5 = -iVar5;
            }
            iVar5 = FT_MulFix(iVar5,uVar3);
            if (iVar5 < iVar4) {
              piVar6 = puVar2 + uVar9 * 9 + 0x3a;
              uVar8 = uVar11;
              iVar4 = iVar5;
            }
          }
        }
      }
    }
    if ((piVar6 != (int *)0x0) && (*(int **)(psVar7 + 10) = piVar6, uVar8 != 0)) {
      *(byte *)(psVar7 + 6) = *(byte *)(psVar7 + 6) | 8;
    }
  }
  return;
}

