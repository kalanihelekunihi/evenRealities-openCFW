
undefined8 FUN_00440c2e(int param_1)

{
  int iVar1;
  byte bVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  
  iVar3 = FUN_0044e498(param_1);
  if (*(int *)(param_1 + 8) != 0) {
    *(undefined4 *)(*(int *)(param_1 + 8) + 0x24) = 0;
  }
  iVar4 = FUN_0043f022(param_1,0);
  iVar5 = FUN_0043f050(param_1,0);
  iVar6 = FUN_0043ff5e(param_1);
  iVar1 = DAT_00440d68;
  iVar12 = iVar5 + iVar4 + iVar6;
  uVar7 = FUN_0044ddea(param_1);
  iVar6 = iVar1;
  for (uVar10 = 0; uVar10 < uVar7; uVar10 = uVar10 + 1) {
    iVar11 = *(int *)(**(int **)(param_1 + 8) + uVar10 * 4);
    iVar9 = FUN_0043e11c(iVar11,DAT_00440d6c);
    if (iVar9 == 0) {
      iVar9 = FUN_0043f612(iVar11);
      if (iVar9 == 0) {
        bVar2 = FUN_0043eef6(iVar11,0);
        if (bVar2 < 4) {
          iVar9 = (*(int *)(iVar11 + 0x20) - *(int *)(param_1 + 0x18)) + 1;
        }
        else {
          iVar8 = FUN_0043eeec(iVar11,0);
          iVar9 = iVar1;
          if (iVar8 == 0) {
            iVar8 = FUN_004515a4(iVar11 + 0x14);
            iVar9 = FUN_0043ef70(iVar11,0);
            iVar9 = iVar9 + iVar4 + iVar8;
          }
        }
      }
      else {
        iVar9 = (*(int *)(iVar11 + 0x20) - *(int *)(param_1 + 0x18)) + 1;
      }
      iVar8 = FUN_0043ef7a(iVar11,0);
      if (iVar6 <= iVar8 + iVar9) {
        iVar6 = FUN_0043ef7a(iVar11,0);
        iVar6 = iVar6 + iVar9;
      }
    }
  }
  if (*(int *)(param_1 + 8) != 0) {
    *(int *)(*(int *)(param_1 + 8) + 0x24) = -iVar3;
  }
  if ((iVar6 != iVar1) && (iVar12 <= iVar5 + iVar6)) {
    iVar12 = iVar5 + iVar6;
  }
  return CONCAT44(iVar5,iVar12);
}

