
undefined8 FUN_0041df48(uint param_1,char param_2,uint *param_3)

{
  bool bVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  uint *puVar5;
  uint *puVar6;
  uint *local_20;
  
  if ((((param_3 == (uint *)0x0) || (param_1 < 0x38)) || (param_1 - 0x3f < 0x3e)) ||
     (0x83 < param_1)) {
    uVar2 = 6;
    local_20 = param_3;
  }
  else {
    uVar3 = (uint)(0x3e < param_1);
    iVar4 = uVar3 * -0x45 + param_1 + -0x38;
    puVar6 = (uint *)(DAT_0041e138 + uVar3 * 0x70 + iVar4 * 0x10);
    puVar5 = (uint *)(DAT_0041e170 + uVar3 * 0x70 + iVar4 * 0x10);
    local_20 = (uint *)critical_save();
    if (param_2 == '\0') {
      uVar3 = 0xffffffff;
    }
    else {
      uVar3 = *puVar6;
    }
    *param_3 = uVar3;
    *param_3 = *param_3 & *puVar5;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts(((uint)local_20 & 1) == 1);
    }
    uVar2 = 0;
  }
  return CONCAT44(local_20,uVar2);
}

