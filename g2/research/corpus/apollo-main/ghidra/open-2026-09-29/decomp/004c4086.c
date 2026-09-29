
undefined8 FUN_004c4086(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

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
  iVar4 = FUN_004c37a8(5,param_1);
  if (iVar4 == 0) {
    local_1c = FUN_00473940();
    iVar4 = FUN_004c37ca(5);
    if (iVar4 == 0) {
      *DAT_004c4694 = '\x01';
    }
    FUN_004c37fe(5,param_1,1);
    pcVar2 = DAT_004c44b8;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_1c & 1) == 1);
    }
    uVar5 = 0;
    if ((*DAT_004c44b8 != '\0') && (uVar5 = 0, *DAT_004c44a8 != 0)) {
      if (*DAT_004c44b4 == '\0') {
        iVar6 = FUN_004c3d9e(0x36);
      }
      else {
        iVar6 = FUN_004c3cd4(0x36);
      }
      uVar5 = 0;
      if (iVar6 != 0) {
        local_1c = FUN_00473940();
        FUN_004c37fe(5,param_1,0);
        bVar1 = (bool)isCurrentModePrivileged();
        uVar5 = local_1c;
        if (bVar1) {
          enableIRQinterrupts((local_1c & 1) == 1);
        }
      }
    }
    if (iVar6 == 0) {
      local_1c = FUN_00473940(uVar5);
      pcVar3 = DAT_004c468c;
      if (*DAT_004c468c != '\0') {
        local_20 = *(undefined4 *)*DAT_004c4690;
      }
      if (*pcVar2 == '\0') {
        iVar6 = 1;
      }
      if ((iVar6 == 0) && (*DAT_004c4694 != '\0')) {
        *DAT_004c4694 = '\0';
        FUN_004d3952(1);
        if (*DAT_004c44a8 != 0) {
          iVar6 = FUN_004d3992(DAT_004c44b4);
          if (iVar6 == 0) {
            if (*pcVar3 == '\0') {
              *pcVar3 = '\x01';
            }
          }
          else {
            FUN_004d3952(0);
          }
        }
      }
      if (iVar6 != 0) {
        FUN_004c37fe(5,param_1,0);
      }
      if (*pcVar3 != '\0') {
        *DAT_004c4690 = &local_20;
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_1c & 1) == 1);
      }
    }
    if (((iVar6 != 0) && (*pcVar2 != '\0')) && (*DAT_004c44a8 != 0)) {
      if (*DAT_004c44b4 == '\0') {
        iVar6 = FUN_004c3e9a(0x36);
      }
      else {
        iVar6 = FUN_004c3d28(0x36);
      }
    }
    FUN_004c4058(&local_20);
  }
  else {
    local_1c = FUN_00473940();
    if (*DAT_004c468c != '\0') {
      local_20 = *(undefined4 *)*DAT_004c4690;
    }
    *DAT_004c4690 = &local_20;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_1c & 1) == 1);
    }
    FUN_004c4058(&local_20);
    iVar6 = 0;
  }
  return CONCAT44(local_20,iVar6);
}

