
undefined8
state_update_critical_42cea4
          (undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  
  uVar2 = critical_save();
  *DAT_0042d7b8 = param_1;
  if (*DAT_0042d7bc == '\0') {
    state_adjust_42cdf8(param_1);
  }
  else {
    *DAT_0042d7c0 = 1;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return CONCAT44(param_4,uVar2);
}

