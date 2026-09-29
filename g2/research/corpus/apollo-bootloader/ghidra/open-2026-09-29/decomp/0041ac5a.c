
undefined8 FUN_0041ac5a(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = critical_save();
  if (param_1 == '\0') {
    uVar3 = 0x80000000;
  }
  else {
    uVar3 = 0xc0000000;
  }
  *DAT_0041b0c4 = *DAT_0041b0c4 & 0x3fffffff | uVar3;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return CONCAT44(param_4,uVar2);
}

