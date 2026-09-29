
undefined8 FUN_0043ffd0(undefined4 param_1)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int local_30;
  undefined4 uStack_2c;
  
  iVar2 = FUN_0043f612(param_1);
  if (iVar2 == 0) {
    local_30 = FUN_0044dca2(param_1);
    uVar3 = FUN_0043eee2(param_1,0);
    uVar4 = FUN_0043eeec(param_1,0);
    if (local_30 == 0) {
      FUN_00440246(param_1,uVar3,uVar4);
    }
    else {
      iVar2 = FUN_0043fe16(local_30);
      iVar5 = FUN_0043fe70(local_30);
      if (((uVar3 & 0x60000000) == 0x20000000) && ((int)(uVar3 & 0x9fffffff) < 0x1fffffff)) {
        iVar6 = FUN_0043eea6(local_30,0);
        if (iVar6 == 0x3fffffff) {
          uVar3 = 0;
        }
        else {
          if ((int)(uVar3 & 0x9fffffff) < 0x10000000) {
            uVar3 = uVar3 & 0x9fffffff;
          }
          else {
            uVar3 = 0xfffffff - (uVar3 & 0x9fffffff);
          }
          uVar3 = (int)(uVar3 * iVar2) / 100;
        }
      }
      if (((uVar4 & 0x60000000) == 0x20000000) && ((int)(uVar4 & 0x9fffffff) < 0x1fffffff)) {
        iVar6 = FUN_0043eec4(local_30,0);
        if (iVar6 == 0x3fffffff) {
          uVar4 = 0;
        }
        if ((int)(uVar4 & 0x9fffffff) < 0x10000000) {
          uVar4 = uVar4 & 0x9fffffff;
        }
        else {
          uVar4 = 0xfffffff - (uVar4 & 0x9fffffff);
        }
        uVar4 = (int)(uVar4 * iVar5) / 100;
      }
      uVar7 = FUN_0043ef02(param_1,0);
      uVar8 = FUN_0043ef0c(param_1,0);
      iVar6 = FUN_0043fd9e(param_1);
      iVar9 = FUN_0043fdda(param_1);
      if (((uVar7 & 0x60000000) == 0x20000000) && ((int)(uVar7 & 0x9fffffff) < 0x1fffffff)) {
        if ((int)(uVar7 & 0x9fffffff) < 0x10000000) {
          uVar7 = uVar7 & 0x9fffffff;
        }
        else {
          uVar7 = 0xfffffff - (uVar7 & 0x9fffffff);
        }
        uVar7 = (int)(uVar7 * iVar6) / 100;
      }
      if (((uVar8 & 0x60000000) == 0x20000000) && ((int)(uVar8 & 0x9fffffff) < 0x1fffffff)) {
        if ((int)(uVar8 & 0x9fffffff) < 0x10000000) {
          uVar8 = uVar8 & 0x9fffffff;
        }
        else {
          uVar8 = 0xfffffff - (uVar8 & 0x9fffffff);
        }
        uVar8 = (int)(uVar8 * iVar9) / 100;
      }
      iVar11 = uVar7 + uVar3;
      iVar12 = uVar8 + uVar4;
      bVar1 = FUN_0043eef6(param_1,0);
      if (bVar1 == 0) {
        iVar10 = FUN_0043efba(local_30,0);
        if (iVar10 == 1) {
          bVar1 = 3;
        }
        else {
          bVar1 = 1;
        }
      }
      if ((bVar1 != 1) && (bVar1 != 0)) {
        if (bVar1 == 3) {
          iVar11 = (iVar2 + iVar11) - iVar6;
        }
        else if (bVar1 < 3) {
          iVar11 = (iVar2 / 2 + iVar11) - iVar6 / 2;
        }
        else if (bVar1 == 5) {
          iVar11 = (iVar2 / 2 + iVar11) - iVar6 / 2;
          iVar12 = (iVar5 + iVar12) - iVar9;
        }
        else if (bVar1 < 5) {
          iVar12 = (iVar5 + iVar12) - iVar9;
        }
        else if (bVar1 == 7) {
          iVar12 = (iVar5 / 2 + iVar12) - iVar9 / 2;
        }
        else if (bVar1 < 7) {
          iVar11 = (iVar2 + iVar11) - iVar6;
          iVar12 = (iVar5 + iVar12) - iVar9;
        }
        else if (bVar1 == 9) {
          iVar11 = (iVar2 / 2 + iVar11) - iVar6 / 2;
          iVar12 = (iVar5 / 2 + iVar12) - iVar9 / 2;
        }
        else if (bVar1 < 9) {
          iVar11 = (iVar2 + iVar11) - iVar6;
          iVar12 = (iVar5 / 2 + iVar12) - iVar9 / 2;
        }
      }
      FUN_00440246(param_1,iVar11,iVar12);
    }
  }
  return CONCAT44(uStack_2c,local_30);
}

