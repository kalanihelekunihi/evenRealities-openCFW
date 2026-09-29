
void FUN_005cc85e(int *param_1)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  byte bVar8;
  int iVar9;
  int local_118;
  int local_114;
  int local_110;
  int local_10c;
  undefined1 auStack_108 [16];
  undefined1 auStack_f8 [16];
  undefined4 local_e8;
  undefined1 auStack_88 [16];
  undefined4 local_78;
  
  iVar2 = *param_1;
  uVar3 = FUN_00451960(param_1);
  FUN_0043feca(iVar2,auStack_108);
  FUN_00451b9c(auStack_88);
  local_78 = uVar3;
  FUN_00452616(iVar2,0x20000,auStack_88);
  FUN_00451c6e(uVar3,auStack_88,auStack_108);
  FUN_005cc6e8(&local_118,iVar2 + 0x14);
  iVar4 = FUN_00451598(iVar2 + 0x14);
  iVar5 = FUN_004515a4(iVar2 + 0x14);
  bVar8 = *(byte *)(iVar2 + 0x30) & 7;
  if (bVar8 == 1) {
    bVar1 = true;
  }
  else if (bVar8 == 2) {
    bVar1 = false;
  }
  else if (iVar4 < iVar5) {
    bVar1 = false;
  }
  else {
    bVar1 = true;
  }
  if (bVar1) {
    iVar4 = FUN_0043fdda(iVar2);
    iVar5 = FUN_00451598(iVar2 + 0x14);
    iVar5 = iVar5 - iVar4;
    if (*(int *)(iVar2 + 0x2c) == -1) {
      uVar6 = FUN_0043e156(iVar2);
      iVar9 = iVar5;
      if ((uVar6 & 1) == 0) {
        iVar9 = 0;
      }
    }
    else {
      iVar9 = (*(int *)(iVar2 + 0x2c) * iVar5) / 0x100;
    }
    iVar7 = FUN_005cc72c(iVar2,0);
    if (iVar7 == 1) {
      iVar9 = iVar5 - iVar9;
    }
    local_118 = iVar9 + local_118;
    if (iVar4 < 1) {
      iVar4 = 0;
    }
    else {
      iVar4 = iVar4 + -1;
    }
    local_110 = iVar4 + local_118;
  }
  else {
    iVar4 = FUN_0043fd9e(iVar2);
    iVar5 = FUN_004515a4(iVar2 + 0x14);
    iVar5 = iVar5 - iVar4;
    if (*(int *)(iVar2 + 0x2c) == -1) {
      uVar6 = FUN_0043e156(iVar2);
      iVar9 = iVar5;
      if ((uVar6 & 1) == 0) {
        iVar9 = 0;
      }
    }
    else {
      iVar9 = (*(int *)(iVar2 + 0x2c) * iVar5) / 0x100;
    }
    iVar7 = FUN_005cc72c(iVar2,0);
    if (iVar7 == 1) {
      iVar9 = iVar5 - iVar9;
    }
    local_10c = local_10c - iVar9;
    if (iVar4 < 1) {
      iVar4 = 0;
    }
    else {
      iVar4 = iVar4 + -1;
    }
    local_114 = local_10c - iVar4;
  }
  iVar4 = FUN_005cc70e(iVar2,0x30000);
  iVar5 = FUN_005cc718(iVar2,0x30000);
  iVar9 = FUN_005cc6fa(iVar2,0x30000);
  iVar7 = FUN_005cc704(iVar2,0x30000);
  local_118 = local_118 - iVar4;
  local_110 = iVar5 + local_110;
  local_114 = local_114 - iVar9;
  local_10c = iVar7 + local_10c;
  FUN_00451b9c(auStack_f8);
  local_e8 = uVar3;
  FUN_00452616(iVar2,0x30000,auStack_f8);
  FUN_00451c6e(uVar3,auStack_f8,&local_118);
  return;
}

