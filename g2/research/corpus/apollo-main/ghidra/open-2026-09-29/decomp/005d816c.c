
void FUN_005d816c(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  uint *puVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  undefined4 uVar12;
  uint uVar13;
  int local_30;
  int local_28;
  
  iVar2 = param_2 * 0xcc + *(int *)(param_1 + 0x18);
  uVar4 = *(undefined4 *)(iVar2 + 200);
  local_28 = *(int *)(iVar2 + 0xcc);
  puVar5 = *(uint **)(param_1 + 0xc);
  local_30 = *(int *)(param_1 + 4);
  do {
    if (local_30 == 0) {
      return;
    }
    uVar6 = *puVar5;
    uVar8 = uVar6 + puVar5[1] * 0x28;
    uVar3 = 0;
    uVar13 = 0;
    for (uVar7 = uVar6; uVar7 < uVar8; uVar7 = uVar7 + 0x28) {
      if ((int)((uint)*(byte *)(uVar7 + 0x10) << 0x1a) < 0) {
        if (uVar13 == 0) {
          uVar13 = uVar7;
        }
        uVar3 = uVar3 + 1;
      }
    }
    uVar7 = uVar13;
    if (uVar3 < 2) {
      if (uVar3 == 1) {
        local_28 = FT_MulFix(*(undefined4 *)(uVar13 + 0x1c),uVar4);
        local_28 = *(int *)(uVar13 + 0x24) - local_28;
      }
      for (; uVar6 < uVar8; uVar6 = uVar6 + 0x28) {
        if (uVar6 != uVar13) {
          iVar2 = FT_MulFix(*(undefined4 *)(uVar6 + 0x1c),uVar4);
          *(int *)(uVar6 + 0x24) = local_28 + iVar2;
        }
      }
    }
    else {
      do {
        do {
          uVar3 = uVar7;
          uVar7 = *(uint *)(uVar3 + 4);
          if (uVar7 == uVar13) goto LAB_005d81a2;
        } while ((int)((uint)*(byte *)(uVar7 + 0x10) << 0x1a) < 0);
        do {
          uVar7 = *(uint *)(uVar7 + 4);
        } while (-1 < (int)((uint)*(byte *)(uVar7 + 0x10) << 0x1a));
        if (*(int *)(uVar7 + 0x1c) < *(int *)(uVar3 + 0x1c)) {
          iVar2 = *(int *)(uVar7 + 0x1c);
          iVar9 = *(int *)(uVar7 + 0x24);
          iVar10 = *(int *)(uVar3 + 0x1c) - iVar2;
          iVar11 = *(int *)(uVar3 + 0x24) - iVar9;
        }
        else {
          iVar2 = *(int *)(uVar3 + 0x1c);
          iVar9 = *(int *)(uVar3 + 0x24);
          iVar10 = *(int *)(uVar7 + 0x1c) - iVar2;
          iVar11 = *(int *)(uVar7 + 0x24) - iVar9;
        }
        uVar12 = 0x10000;
        if (0 < iVar10) {
          uVar12 = FT_DivFix(iVar11,iVar10);
        }
        uVar3 = *(uint *)(uVar3 + 4);
        do {
          iVar1 = *(int *)(uVar3 + 0x1c) - iVar2;
          if (iVar1 < 1) {
            iVar1 = FT_MulFix(iVar1,uVar4);
            iVar1 = iVar1 + iVar9;
          }
          else if (iVar1 < iVar10) {
            iVar1 = FT_MulFix(iVar1,uVar12);
            iVar1 = iVar1 + iVar9;
          }
          else {
            iVar1 = FT_MulFix(iVar1 - iVar10,uVar4);
            iVar1 = iVar1 + iVar11 + iVar9;
          }
          *(int *)(uVar3 + 0x24) = iVar1;
          uVar3 = *(uint *)(uVar3 + 4);
        } while (uVar3 != uVar7);
      } while (uVar7 != uVar13);
    }
LAB_005d81a2:
    local_30 = local_30 + -1;
    puVar5 = puVar5 + 2;
  } while( true );
}

