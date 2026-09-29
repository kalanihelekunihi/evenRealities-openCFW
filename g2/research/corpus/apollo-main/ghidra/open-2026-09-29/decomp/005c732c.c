
void FUN_005c732c(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  bool bVar13;
  int local_134;
  int local_130;
  int local_12c;
  int local_128;
  int local_124;
  int local_120;
  int local_11c;
  int local_118;
  int local_114;
  int local_110;
  undefined1 auStack_10c [16];
  undefined1 auStack_fc [16];
  undefined4 local_ec;
  undefined4 local_e0;
  undefined1 auStack_98 [16];
  undefined4 local_88;
  undefined4 uStack_28;
  
  iVar1 = *param_1;
  local_120 = iVar1;
  uStack_28 = param_4;
  uVar2 = FUN_00451960(param_1);
  local_124 = FUN_005c719a(iVar1,0);
  iVar3 = *(int *)(local_124 + 0xc);
  iVar4 = FUN_005c71b8(iVar1,0);
  bVar13 = iVar4 != 1;
  iVar4 = FUN_005c7190(iVar1,0);
  iVar5 = FUN_005c715e(iVar1,0);
  if (bVar13) {
    iVar6 = FUN_005c7172(iVar1,0);
    iVar6 = iVar4 + iVar6;
  }
  else {
    iVar6 = FUN_005c717c(iVar1,0);
  }
  iVar7 = FUN_005c7186(iVar1,0);
  iVar8 = FUN_005c7172(iVar1,0x20000);
  iVar9 = FUN_005c717c(iVar1,0x20000);
  iVar10 = FUN_005c715e(iVar1,0x20000);
  local_118 = FUN_005c7168(iVar1,0x20000);
  local_11c = FUN_005c714a(iVar1,0x20000);
  uVar11 = FUN_005c7154(iVar1,0x20000);
  FUN_00451b9c(auStack_98);
  local_88 = uVar2;
  FUN_00452616(iVar1,0x20000,auStack_98);
  if (bVar13) {
    local_134 = iVar6 + *(int *)(iVar1 + 0x14);
    local_12c = iVar9 + iVar8 + iVar3 + local_134 + -1;
  }
  else {
    local_12c = *(int *)(iVar1 + 0x1c) - iVar6;
    local_134 = (((local_12c - iVar3) - iVar8) - iVar9) + 1;
  }
  local_130 = iVar4 + iVar5 + *(int *)(iVar1 + 0x18);
  local_128 = local_118 + iVar10 + iVar3 + local_130 + -1;
  FUN_005c7138(auStack_10c,&local_134);
  FUN_00450b98(auStack_10c,local_11c,uVar11);
  FUN_00451c6e(uVar2,auStack_98,auStack_10c);
  uVar11 = FUN_005c71ae(iVar1,0);
  uVar12 = FUN_005c71a4(iVar1,0);
  FUN_00489546(&local_114,*(undefined4 *)(local_120 + 0x2c),local_124,uVar12,uVar11,0x1fffffff,0);
  FUN_00489f5e(auStack_fc);
  local_ec = uVar2;
  FUN_00452988(iVar1,0,auStack_fc);
  local_e0 = *(undefined4 *)(local_120 + 0x2c);
  iVar6 = FUN_004515a4(&local_134);
  if (bVar13) {
    local_124 = iVar7 + local_12c;
    local_11c = local_114 + local_124;
  }
  else {
    local_11c = local_134 - iVar7;
    local_124 = local_11c - local_114;
  }
  local_120 = (iVar6 - iVar3) / 2 + iVar4 + iVar5 + *(int *)(iVar1 + 0x18);
  local_118 = local_110 + local_120;
  FUN_00489fe0(uVar2,auStack_fc,&local_124);
  return;
}

