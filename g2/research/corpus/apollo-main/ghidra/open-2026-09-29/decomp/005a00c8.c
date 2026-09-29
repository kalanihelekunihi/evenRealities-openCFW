
undefined8 FUN_005a00c8(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  
  uVar2 = FUN_00473940();
  *DAT_005a09dc = param_1;
  if (*DAT_005a09e0 == '\0') {
    FUN_005a001c(param_1);
  }
  else {
    *DAT_005a09e4 = 1;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return CONCAT44(param_4,uVar2);
}

