
undefined8 FUN_0041ac92(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  
  uVar2 = critical_save();
  *DAT_0041b0c8 = *DAT_0041b0c8 & 0xffffffbf | (param_1 & 1) << 6;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return CONCAT44(param_4,uVar2);
}

