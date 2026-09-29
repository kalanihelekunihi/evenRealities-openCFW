
undefined8 FUN_00471cd6(uint param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  bool bVar1;
  int iVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  uint *puVar5;
  undefined4 local_10;
  
  iVar2 = DAT_00471ed0;
  if ((param_1 == 0xe) || (param_1 == 0xf)) {
    uVar4 = 3;
    local_10 = param_4;
  }
  else {
    if ((*(uint *)(DAT_00471ed0 + param_1 * 0x20 + 0x200) & 0x1ffff) >> 8 < 0x1c) {
      uVar3 = FUN_00471b9c();
      FUN_004c44bc(uVar3,param_1 + 0x22 & 0xff);
    }
    local_10 = FUN_00473940();
    *DAT_00471ed4 = *DAT_00471ed4 | 1 << (param_1 & 0xff);
    puVar5 = (uint *)(iVar2 + param_1 * 0x20 + 0x200);
    *puVar5 = *puVar5 | 2;
    puVar5 = (uint *)(iVar2 + param_1 * 0x20 + 0x200);
    *puVar5 = *puVar5 & 0xfffffffd;
    puVar5 = (uint *)(iVar2 + param_1 * 0x20 + 0x200);
    *puVar5 = *puVar5 | 1;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
    uVar4 = 0;
  }
  return CONCAT44(local_10,uVar4);
}

