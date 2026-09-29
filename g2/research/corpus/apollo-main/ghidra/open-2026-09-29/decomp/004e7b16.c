
void FUN_004e7b16(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int local_78;
  int local_74;
  int local_70;
  int local_6c;
  int local_68;
  undefined4 local_58;
  undefined4 local_48;
  undefined4 uStack_18;
  
  piVar1 = DAT_004e8454;
  if (*DAT_004e8454 != 0) {
    uStack_18 = param_4;
    FUN_0043f66c(*DAT_004e8454);
    piVar2 = DAT_004e8458;
    iVar3 = FUN_0043fce0(*piVar1);
    *piVar2 = iVar3;
    if ((param_1 == 1) && (*DAT_004e80dc + -1 <= *DAT_004e7ff4)) {
      iVar4 = *piVar2 - *DAT_004e813c;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_70 = *piVar2;
        local_74 = DAT_004e8468;
        local_78 = 499;
        local_6c = iVar4;
        FUN_0043d574(4,DAT_004e7fe8,DAT_004e7fe4,DAT_004e846c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        local_78 = iVar4;
        compress_log_output(0x10800000,DAT_004e8470,DAT_004e8470,*piVar2);
      }
    }
    else {
      if (param_1 != -1) {
        return;
      }
      if (0 < *DAT_004e7ff4) {
        return;
      }
      iVar4 = *DAT_004e813c + *piVar2;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_70 = *piVar2;
        local_74 = DAT_004e8484;
        local_78 = 0x1f7;
        local_6c = iVar4;
        FUN_0043d574(4,DAT_004e7fe8,DAT_004e7fe4,DAT_004e846c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        local_78 = iVar4;
        compress_log_output(0x10800000,DAT_004e8488,DAT_004e8488,*piVar2);
      }
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_6c = *piVar2;
      local_74 = DAT_004e8474;
      local_78 = 0x1fd;
      local_70 = param_1;
      local_68 = iVar4;
      FUN_0043d574(4,DAT_004e7fe8,DAT_004e7fe4,DAT_004e846c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      local_78 = *piVar2;
      local_74 = iVar4;
      compress_log_output(0x10c00000,DAT_004e8478,DAT_004e8478,param_1);
    }
    FUN_004503d6(&local_78);
    local_78 = *piVar1;
    FUN_004506ce(&local_78,*piVar2,iVar4);
    local_48 = *DAT_004e842c;
    local_74 = DAT_004e845c;
    local_58 = DAT_004e847c;
    local_68 = DAT_004e8480;
    *DAT_004e83bc = 1;
    FUN_00450408(&local_78);
  }
  return;
}

