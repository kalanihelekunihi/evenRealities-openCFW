
void FUN_005c8e1e(int *param_1)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  int local_108;
  int local_104;
  int local_100;
  int local_fc;
  undefined1 auStack_f8 [8];
  undefined1 auStack_f0 [16];
  undefined4 local_e0;
  undefined1 *local_d4;
  undefined4 local_cc;
  byte local_9c;
  undefined1 auStack_8c [16];
  undefined4 local_7c;
  byte local_6c;
  
  iVar2 = *param_1;
  uVar3 = FUN_00451960(param_1);
  iVar4 = FUN_004997f8(*(undefined4 *)(iVar2 + 0x2c));
  if ((int)((uint)*(byte *)(iVar2 + 100) << 0x1f) < 0) {
    FUN_00451b9c(auStack_8c);
    local_7c = uVar3;
    FUN_00452616(iVar2,0x60000,auStack_8c);
    FUN_005c78a4(&local_108,iVar2 + 0x50);
    local_108 = *(int *)(*(int *)(iVar2 + 0x2c) + 0x14) + local_108;
    local_104 = *(int *)(*(int *)(iVar2 + 0x2c) + 0x18) + local_104;
    local_100 = *(int *)(*(int *)(iVar2 + 0x2c) + 0x14) + local_100;
    local_fc = *(int *)(*(int *)(iVar2 + 0x2c) + 0x18) + local_fc;
    FUN_00451c6e(uVar3,auStack_8c,&local_108);
    iVar5 = FUN_005c78de(iVar2,0x60000);
    iVar6 = FUN_005c78ca(iVar2,0x60000);
    iVar7 = FUN_005c78b6(iVar2,0x60000);
    FUN_0043bb00(auStack_f8,0,8);
    uVar1 = (*(code *)*DAT_005c8fd8)(*(int *)(iVar2 + 0x60) + iVar4);
    FUN_00454738(auStack_f8,iVar4 + *(int *)(iVar2 + 0x60),uVar1);
    local_108 = iVar5 + iVar6 + local_108;
    local_104 = iVar5 + iVar7 + local_104;
    uVar8 = FUN_005c78e8(*(undefined4 *)(iVar2 + 0x2c),0);
    FUN_00489f5e(auStack_f0);
    local_e0 = uVar3;
    FUN_00452988(iVar2,0x60000,auStack_f0);
    if ((2 < local_6c) || (iVar2 = FUN_0044102e(local_cc,uVar8), iVar2 == 0)) {
      local_d4 = auStack_f8;
      local_9c = local_9c | 1;
      FUN_00489fe0(uVar3,auStack_f0,&local_108);
    }
  }
  return;
}

