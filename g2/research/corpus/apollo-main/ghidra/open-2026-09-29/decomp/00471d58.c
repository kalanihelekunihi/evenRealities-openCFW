
undefined8 FUN_00471d58(int param_1,undefined4 param_2,uint param_3)

{
  bool bVar1;
  int iVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  uint *puVar5;
  uint uVar6;
  undefined4 local_18;
  
  iVar2 = DAT_00471ed0;
  if ((param_1 == 0xe) || (param_1 == 0xf)) {
    uVar4 = 3;
    local_18 = param_3;
  }
  else {
    uVar6 = (*(uint *)(DAT_00471ed0 + param_1 * 0x20 + 0x200) & 0x1ffff) >> 8;
    local_18 = FUN_00473940();
    puVar5 = (uint *)(iVar2 + param_1 * 0x20 + 0x200);
    *puVar5 = *puVar5 & 0xfffffffe;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_18 & 1) == 1);
    }
    if (uVar6 < 0x1c) {
      uVar3 = FUN_00471b9c(uVar6);
      FUN_004c4530(uVar3,param_1 + 0x22U & 0xff);
    }
    uVar4 = 0;
  }
  return CONCAT44(local_18,uVar4);
}

