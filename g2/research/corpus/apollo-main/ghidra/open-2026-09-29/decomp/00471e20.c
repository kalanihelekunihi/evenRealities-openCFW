
undefined8 FUN_00471e20(uint param_1,uint param_2,uint param_3)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  uint *puVar4;
  undefined4 local_18;
  
  if ((param_1 < 0xe0) && (param_2 < 0x28)) {
    iVar3 = (param_1 & 3) << 3;
    local_18 = FUN_00473940();
    puVar4 = (uint *)(DAT_00471ed8 + (param_1 & 0xfffffffc));
    *puVar4 = param_2 << iVar3 | *puVar4 & ~(0x7f << iVar3);
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_18 & 1) == 1);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = 6;
    local_18 = param_3;
  }
  return CONCAT44(local_18,uVar2);
}

