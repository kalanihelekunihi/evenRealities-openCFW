
undefined8 FUN_00421d5e(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  char *pcVar2;
  char cVar3;
  int iVar4;
  uint uVar5;
  undefined4 local_18;
  uint local_14;
  
  local_18 = 1000;
  local_14 = param_4;
  iVar4 = FUN_004215dc(4,param_1);
  if (iVar4 == 0) {
    local_14 = critical_save();
    pcVar2 = DAT_00422298;
    if (*DAT_00422298 != '\0') {
      local_18 = *(undefined4 *)*DAT_0042229c;
    }
    uVar5 = (uint)(*DAT_004222d4 == '\0');
    if (uVar5 == 0) {
      cVar3 = FUN_004215fe(4);
      if ((cVar3 == '\0') && (clkgen_hfadj_enable_426c58(1), *DAT_00422290 != 0)) {
        uVar5 = clkgen_hfadj_config_426c72(*DAT_00422294);
        if (uVar5 == 0) {
          if ((*pcVar2 == '\0') && (*DAT_0042244c == '\0')) {
            *pcVar2 = '\x01';
          }
        }
        else {
          clkgen_hfadj_enable_426c58(0);
        }
      }
      if (uVar5 == 0) {
        FUN_00421632(4,param_1,1);
      }
      if (*pcVar2 != '\0') {
        *DAT_0042229c = &local_18;
      }
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_14 & 1) == 1);
    }
    FUN_00421d28(&local_18);
  }
  else {
    local_14 = critical_save();
    if (*DAT_00422298 != '\0') {
      local_18 = *(undefined4 *)*DAT_0042229c;
    }
    *DAT_0042229c = &local_18;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_14 & 1) == 1);
    }
    FUN_00421d28(&local_18);
    uVar5 = 0;
  }
  return CONCAT44(local_18,uVar5);
}

