
void FUN_005c2904(int param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  int iVar14;
  uint uVar15;
  int iVar16;
  int iVar17;
  uint uVar18;
  uint uVar19;
  uint local_58;
  int local_50;
  
  cVar1 = FUN_005c1658(param_1,0);
  iVar2 = FUN_005c1664(param_1,0);
  iVar3 = FUN_005c1692(param_1,0);
  iVar4 = FUN_005c162e(param_1,0);
  iVar5 = FUN_005c1638(param_1,0);
  iVar6 = FUN_0043fe16(param_1);
  iVar7 = FUN_0043fe70(param_1);
  iVar7 = iVar7 - (*(int *)(param_1 + 0x3c) + -1) * iVar4;
  iVar16 = 0;
  iVar17 = *(int *)(param_1 + 0x2c);
  for (local_58 = 0; local_58 < *(uint *)(param_1 + 0x3c); local_58 = local_58 + 1) {
    uVar18 = 0;
    uVar15 = 0;
    while (((*(int *)(iVar17 + uVar15 * 4) != 0 &&
            (iVar9 = FUN_004547be(*(undefined4 *)(iVar17 + uVar15 * 4),&LAB_005c2ab0), iVar9 != 0))
           && (**(char **)(iVar17 + uVar15 * 4) != '\0'))) {
      iVar9 = FUN_005c25c8(*(undefined2 *)(*(int *)(param_1 + 0x34) + (uVar15 + iVar16) * 2));
      uVar18 = iVar9 + uVar18;
      uVar15 = uVar15 + 1;
    }
    if (uVar15 != 0) {
      uVar10 = *(uint *)(param_1 + 0x3c);
      uVar13 = *(uint *)(param_1 + 0x3c);
      local_50 = iVar6 - (uVar15 - 1) * iVar5;
      if (local_50 < 0) {
        local_50 = 0;
      }
      iVar9 = 0;
      for (uVar19 = 0; uVar19 < uVar15; uVar19 = uVar19 + 1) {
        iVar8 = FUN_005c25c8(*(undefined2 *)(*(int *)(param_1 + 0x34) + iVar16 * 2));
        iVar11 = iVar5 * uVar19 + (uint)(iVar9 * local_50) / uVar18;
        iVar14 = iVar5 * uVar19 + (uint)((iVar8 + iVar9) * local_50) / uVar18 + -1;
        iVar12 = iVar11;
        if (cVar1 == '\x01') {
          iVar12 = iVar6 - iVar14;
          iVar14 = iVar6 - iVar11;
        }
        FUN_00450b5c(*(int *)(param_1 + 0x30) + iVar16 * 0x10,iVar2 + iVar12,
                     iVar4 * local_58 + (local_58 * iVar7) / uVar10 + iVar3,iVar2 + iVar14,
                     iVar4 * local_58 + ((local_58 + 1) * iVar7) / uVar13 + iVar3 + -1);
        iVar9 = iVar8 + iVar9;
        iVar16 = iVar16 + 1;
      }
    }
    iVar17 = iVar17 + uVar15 * 4 + 4;
  }
  FUN_00452d42(param_1);
  FUN_00440656(param_1);
  return;
}

