
undefined8 FUN_00421d28(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  bool bVar1;
  char *pcVar2;
  undefined4 local_10;
  
  pcVar2 = DAT_00422298;
  local_10 = param_3;
  if (*DAT_00422298 != '\0') {
    FUN_004216b2(DAT_00422298,param_1);
    local_10 = critical_save();
    *DAT_0042244c = 1;
    *pcVar2 = '\0';
    *DAT_0042229c = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
  }
  return CONCAT44(param_4,local_10);
}

