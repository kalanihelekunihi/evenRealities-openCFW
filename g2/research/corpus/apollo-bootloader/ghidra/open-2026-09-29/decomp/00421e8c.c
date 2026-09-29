
undefined8 FUN_00421e8c(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  bool bVar1;
  char *pcVar2;
  undefined4 local_10;
  
  pcVar2 = DAT_00422450;
  local_10 = param_3;
  if (*DAT_00422450 != '\0') {
    FUN_004216b2(DAT_00422450,param_1);
    local_10 = critical_save();
    *pcVar2 = '\0';
    *DAT_00422454 = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
  }
  return CONCAT44(param_4,local_10);
}

