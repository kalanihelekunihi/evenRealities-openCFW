
void FUN_005c9fec(int param_1,undefined4 param_2)

{
  char cVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined8 uVar8;
  undefined1 auStack_160 [8];
  undefined1 auStack_158 [8];
  undefined1 auStack_150 [8];
  int local_148;
  int local_144;
  undefined4 local_140;
  undefined8 local_134;
  undefined8 local_12c;
  undefined1 auStack_110 [8];
  int local_108;
  int local_104;
  undefined4 local_100;
  undefined8 local_f4;
  undefined8 local_ec;
  byte local_d3;
  undefined1 auStack_d0 [16];
  undefined4 local_c0;
  undefined1 auStack_90 [8];
  int local_88;
  int local_84;
  undefined4 local_80;
  int iStack_2c;
  undefined4 local_28;
  
  iStack_2c = param_1;
  local_28 = param_2;
  uVar2 = FUN_00451960(param_2);
  if (1 < (*(uint *)(param_1 + 0x48) & 0x7fff)) {
    FUN_00489f5e(auStack_90);
    local_80 = uVar2;
    FUN_00452988(param_1,0x20000,auStack_90);
    FUN_005c6fbc(auStack_110);
    local_100 = uVar2;
    FUN_00452b0e(param_1,0x20000,auStack_110);
    if ((*(char *)(param_1 + 0x3c) == '\x10') || (*(char *)(param_1 + 0x3c) == '\b')) {
      local_d3 = local_d3 & 0xfb;
    }
    FUN_005c6fbc(auStack_150);
    local_140 = uVar2;
    FUN_00452b0e(param_1,0x50000,auStack_150);
    FUN_005c6fbc(auStack_d0);
    local_c0 = uVar2;
    FUN_00452b0e(param_1,0,auStack_d0);
    uVar3 = *(uint *)(param_1 + 0x48) & 0x7fff;
    iVar6 = 0;
    for (iVar7 = 0; iVar7 < (int)uVar3; iVar7 = iVar7 + 1) {
      cVar1 = FUN_005cb402(param_1,iVar7);
      if (cVar1 != '\0') {
        iVar6 = iVar6 + 1;
      }
      iVar4 = FUN_004888b4(iVar7,0,uVar3 - 1,*(undefined4 *)(param_1 + 0x40),
                           *(undefined4 *)(param_1 + 0x44));
      local_88 = iVar7;
      local_84 = iVar4;
      local_80 = uVar2;
      iVar5 = FUN_00482ce4(param_1 + 0x2c);
      while (iVar5 != 0) {
        if ((*(int *)(iVar5 + 0xc) <= iVar4) && (iVar4 <= *(int *)(iVar5 + 0x10))) {
          if (cVar1 == '\0') {
            FUN_005caede(param_1,auStack_150,*(undefined4 *)(iVar5 + 8),0x50000);
          }
          else {
            FUN_005cb0ba(param_1,auStack_90,*(undefined4 *)(iVar5 + 4));
            FUN_005caede(param_1,auStack_110,*(undefined4 *)(iVar5 + 4),0x20000);
          }
          break;
        }
        FUN_00452988(param_1,0x20000,auStack_90);
        FUN_00452b0e(param_1,0x20000,auStack_110);
        FUN_00452b0e(param_1,0x50000,auStack_150);
        iVar5 = FUN_00482cfa(param_1 + 0x2c,iVar5);
      }
      FUN_005ca9cc(param_1,iVar7,cVar1,auStack_158,auStack_160);
      if ((*(int *)(param_1 + 0x48) << 1 < 0) && (cVar1 != '\0')) {
        FUN_005ca1e2(param_1,local_28,auStack_90,iVar6,iVar4,auStack_160,iVar7);
      }
      if (cVar1 == '\0') {
        uVar8 = FUN_004515b0(auStack_158);
        local_134 = uVar8;
        uVar8 = FUN_004515b0(auStack_160);
        local_148 = iVar7;
        local_144 = iVar4;
        local_12c = uVar8;
        FUN_005c6fea(uVar2,auStack_150);
      }
      else {
        uVar8 = FUN_004515b0(auStack_158);
        local_f4 = uVar8;
        uVar8 = FUN_004515b0(auStack_160);
        local_108 = iVar7;
        local_104 = iVar4;
        local_ec = uVar8;
        FUN_005c6fea(uVar2,auStack_110);
      }
    }
  }
  return;
}

