
undefined8 FUN_00440a3c(int param_1)

{
  int iVar1;
  char cVar2;
  byte bVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  int iVar13;
  
  iVar4 = FUN_0044e486(param_1);
  if (*(int *)(param_1 + 8) != 0) {
    *(undefined4 *)(*(int *)(param_1 + 8) + 0x20) = 0;
  }
  iVar5 = FUN_0043eff4(param_1,0);
  iVar6 = FUN_0043efc6(param_1,0);
  iVar7 = FUN_0043ff44(param_1);
  iVar1 = DAT_00440d68;
  iVar7 = iVar5 + iVar6 + iVar7;
  uVar8 = FUN_0044ddea(param_1);
  iVar9 = FUN_0043efba(param_1,0);
  iVar10 = iVar1;
  if (iVar9 == 1) {
    for (uVar12 = 0; uVar12 < uVar8; uVar12 = uVar12 + 1) {
      iVar13 = *(int *)(**(int **)(param_1 + 8) + uVar12 * 4);
      iVar9 = FUN_0043e11c(iVar13,DAT_00440d6c);
      if (iVar9 == 0) {
        iVar9 = FUN_0043f612(iVar13);
        if (iVar9 == 0) {
          cVar2 = FUN_0043eef6(iVar13,0);
          if (((cVar2 == '\0') || (cVar2 == '\x03')) || ((cVar2 == '\x06' || (cVar2 == '\b')))) {
            iVar9 = (*(int *)(param_1 + 0x1c) - *(int *)(iVar13 + 0x14)) + 1;
          }
          else {
            iVar11 = FUN_0043eee2(iVar13,0);
            iVar9 = iVar1;
            if (iVar11 == 0) {
              iVar11 = FUN_00451598(iVar13 + 0x14);
              iVar9 = FUN_0043ef84(iVar13,0);
              iVar9 = iVar9 + iVar5 + iVar11;
            }
          }
        }
        else {
          iVar9 = (*(int *)(param_1 + 0x1c) - *(int *)(iVar13 + 0x14)) + 1;
        }
        iVar11 = FUN_0043ef84(iVar13,0);
        if (iVar10 <= iVar11 + iVar9) {
          iVar10 = FUN_0043ef84(iVar13,0);
          iVar10 = iVar10 + iVar9;
        }
      }
    }
    if (iVar10 != iVar1) {
      iVar10 = iVar6 + iVar10;
    }
  }
  else {
    for (uVar12 = 0; uVar12 < uVar8; uVar12 = uVar12 + 1) {
      iVar13 = *(int *)(**(int **)(param_1 + 8) + uVar12 * 4);
      iVar9 = FUN_0043e11c(iVar13,DAT_00440d6c);
      if (iVar9 == 0) {
        iVar9 = FUN_0043f612(iVar13);
        if (iVar9 == 0) {
          bVar3 = FUN_0043eef6(iVar13,0);
          if (((bVar3 < 2) || (bVar3 == 4)) || (bVar3 == 7)) {
            iVar9 = (*(int *)(iVar13 + 0x1c) - *(int *)(param_1 + 0x14)) + 1;
          }
          else {
            iVar11 = FUN_0043eee2(iVar13,0);
            iVar9 = iVar1;
            if (iVar11 == 0) {
              iVar11 = FUN_00451598(iVar13 + 0x14);
              iVar9 = FUN_0043ef8e(iVar13,0);
              iVar9 = iVar9 + iVar6 + iVar11;
            }
          }
        }
        else {
          iVar9 = (*(int *)(iVar13 + 0x1c) - *(int *)(param_1 + 0x14)) + 1;
        }
        iVar11 = FUN_0043ef8e(iVar13,0);
        if (iVar10 <= iVar11 + iVar9) {
          iVar10 = FUN_0043ef8e(iVar13,0);
          iVar10 = iVar10 + iVar9;
        }
      }
    }
    if (iVar10 != iVar1) {
      iVar10 = iVar5 + iVar10;
    }
  }
  if (*(int *)(param_1 + 8) != 0) {
    *(int *)(*(int *)(param_1 + 8) + 0x20) = -iVar4;
  }
  if ((iVar10 != iVar1) && (iVar7 < iVar10)) {
    iVar7 = iVar10;
  }
  return CONCAT44(iVar6,iVar7);
}

