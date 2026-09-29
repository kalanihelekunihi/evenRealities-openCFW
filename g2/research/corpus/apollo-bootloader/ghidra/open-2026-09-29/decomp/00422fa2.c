
undefined8 FUN_00422fa2(int param_1)

{
  bool bVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar3 = 0;
  uVar2 = critical_save();
  if (*(char *)(param_1 + 0x11a) == '\x01') {
    *(undefined1 *)(param_1 + 0x11a) = 0;
    FUN_0041560c(param_1 + 100,0x38,0);
    *(undefined4 *)(param_1 + 0x9c) = 0;
  }
  else {
    uVar3 = 7;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return CONCAT44(uVar2,uVar3);
}

