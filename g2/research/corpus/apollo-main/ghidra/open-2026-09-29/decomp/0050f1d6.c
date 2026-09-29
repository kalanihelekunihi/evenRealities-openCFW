
void FUN_0050f1d6(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 local_c8;
  undefined4 local_c4;
  undefined4 local_c0;
  undefined4 local_bc;
  undefined1 auStack_b8 [4];
  undefined4 local_b4;
  undefined4 local_ac;
  undefined1 auStack_a8 [16];
  undefined1 auStack_98 [16];
  undefined1 auStack_88 [16];
  undefined1 auStack_78 [16];
  int local_68;
  undefined4 local_5c;
  byte local_25;
  undefined4 uStack_14;
  
  iVar1 = *param_1;
  uStack_14 = param_4;
  iVar2 = FUN_0044dca2(iVar1);
  iVar3 = FUN_00451960(param_1);
  FUN_00489f5e(auStack_78);
  local_68 = iVar3;
  FUN_00452988(iVar2,0,auStack_78);
  iVar4 = FUN_00499f64(iVar1);
  if (iVar4 != 0) {
    local_25 = local_25 | 0x40;
  }
  FUN_00439c04(auStack_88,iVar3 + 0x18,0x10);
  iVar4 = FUN_00450bcc(auStack_98,iVar3 + 0x18,iVar2 + 0x14);
  if (iVar4 != 0) {
    FUN_00439c04(iVar3 + 0x18,auStack_98,0x10);
    FUN_0050f30e(iVar2,auStack_b8);
    local_c8 = *(undefined4 *)(iVar1 + 0x14);
    local_c4 = *(undefined4 *)(iVar1 + 0x18);
    local_c0 = *(undefined4 *)(iVar1 + 0x1c);
    local_bc = local_b4;
    iVar2 = FUN_00450bcc(&local_c8,iVar3 + 0x18,&local_c8);
    if (iVar2 != 0) {
      FUN_00439c04(auStack_a8,iVar3 + 0x18,0x10);
      FUN_00439c04(iVar3 + 0x18,&local_c8,0x10);
      local_5c = FUN_004997f8(iVar1);
      FUN_00489fe0(iVar3,auStack_78,iVar1 + 0x14);
      FUN_00439c04(iVar3 + 0x18,auStack_a8,0x10);
    }
    local_c8 = *(undefined4 *)(iVar1 + 0x14);
    local_c4 = local_ac;
    local_c0 = *(undefined4 *)(iVar1 + 0x1c);
    local_bc = *(undefined4 *)(iVar1 + 0x20);
    iVar2 = FUN_00450bcc(&local_c8,iVar3 + 0x18,&local_c8);
    if (iVar2 != 0) {
      FUN_00439c04(auStack_a8,iVar3 + 0x18,0x10);
      FUN_00439c04(iVar3 + 0x18,&local_c8,0x10);
      local_5c = FUN_004997f8(iVar1);
      FUN_00489fe0(iVar3,auStack_78,iVar1 + 0x14);
      FUN_00439c04(iVar3 + 0x18,auStack_a8,0x10);
    }
    FUN_00439c04(iVar3 + 0x18,auStack_88,0x10);
  }
  return;
}

