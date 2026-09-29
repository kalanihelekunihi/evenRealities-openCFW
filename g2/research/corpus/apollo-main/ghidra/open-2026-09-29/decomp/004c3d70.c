
undefined8 FUN_004c3d70(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  bool bVar1;
  char *pcVar2;
  undefined4 local_10;
  
  pcVar2 = DAT_004c4680;
  local_10 = param_3;
  if (*DAT_004c4680 != '\0') {
    FUN_004c387e(DAT_004c4680,param_1);
    local_10 = FUN_00473940();
    *pcVar2 = '\0';
    *DAT_004c4684 = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
  }
  return CONCAT44(param_4,local_10);
}

