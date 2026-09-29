
undefined8 FUN_00421eba(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  char *pcVar2;
  char *pcVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  undefined4 local_20;
  uint local_1c;
  undefined4 uStack_18;
  
  iVar6 = 0;
  local_20 = 0x32;
  local_1c = param_3;
  uStack_18 = param_4;
  iVar4 = FUN_004215dc(5,param_1);
  if (iVar4 == 0) {
    local_1c = critical_save();
    iVar4 = FUN_004215fe(5);
    if (iVar4 == 0) {
      *DAT_00422458 = '\x01';
    }
    FUN_00421632(5,param_1,1);
    pcVar2 = DAT_004222ec;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_1c & 1) == 1);
    }
    uVar5 = 0;
    if ((*DAT_004222ec != '\0') && (uVar5 = 0, *DAT_004222dc != 0)) {
      if (*DAT_004222e8 == '\0') {
        iVar6 = FUN_00421bd2(0x36);
      }
      else {
        iVar6 = FUN_00421b08(0x36);
      }
      uVar5 = 0;
      if (iVar6 != 0) {
        local_1c = critical_save();
        FUN_00421632(5,param_1,0);
        bVar1 = (bool)isCurrentModePrivileged();
        uVar5 = local_1c;
        if (bVar1) {
          enableIRQinterrupts((local_1c & 1) == 1);
        }
      }
    }
    if (iVar6 == 0) {
      local_1c = critical_save(uVar5);
      pcVar3 = DAT_00422450;
      if (*DAT_00422450 != '\0') {
        local_20 = *(undefined4 *)*DAT_00422454;
      }
      if (*pcVar2 == '\0') {
        iVar6 = 1;
      }
      if ((iVar6 == 0) && (*DAT_00422458 != '\0')) {
        *DAT_00422458 = '\0';
        dual_switch_426c8c(1);
        if (*DAT_004222dc != 0) {
          iVar6 = clkgen_config_426ccc(DAT_004222e8);
          if (iVar6 == 0) {
            if (*pcVar3 == '\0') {
              *pcVar3 = '\x01';
            }
          }
          else {
            dual_switch_426c8c(0);
          }
        }
      }
      if (iVar6 != 0) {
        FUN_00421632(5,param_1,0);
      }
      if (*pcVar3 != '\0') {
        *DAT_00422454 = &local_20;
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_1c & 1) == 1);
      }
    }
    if (((iVar6 != 0) && (*pcVar2 != '\0')) && (*DAT_004222dc != 0)) {
      if (*DAT_004222e8 == '\0') {
        iVar6 = FUN_00421cce(0x36);
      }
      else {
        iVar6 = FUN_00421b5c(0x36);
      }
    }
    FUN_00421e8c(&local_20);
  }
  else {
    local_1c = critical_save();
    if (*DAT_00422450 != '\0') {
      local_20 = *(undefined4 *)*DAT_00422454;
    }
    *DAT_00422454 = &local_20;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_1c & 1) == 1);
    }
    FUN_00421e8c(&local_20);
    iVar6 = 0;
  }
  return CONCAT44(local_20,iVar6);
}

