
undefined8 FUN_004c3f2a(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

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
  iVar4 = FUN_004c37a8(4,param_1);
  if (iVar4 == 0) {
    local_14 = FUN_00473940();
    pcVar2 = DAT_004c4464;
    if (*DAT_004c4464 != '\0') {
      local_18 = *(undefined4 *)*DAT_004c4468;
    }
    uVar5 = (uint)(*DAT_004c44a0 == '\0');
    if (uVar5 == 0) {
      cVar3 = FUN_004c37ca(4);
      if ((cVar3 == '\0') && (FUN_004d391e(1), *DAT_004c445c != 0)) {
        uVar5 = FUN_004d3938(*DAT_004c4460);
        if (uVar5 == 0) {
          if ((*pcVar2 == '\0') && (*DAT_004c4688 == '\0')) {
            *pcVar2 = '\x01';
          }
        }
        else {
          FUN_004d391e(0);
        }
      }
      if (uVar5 == 0) {
        FUN_004c37fe(4,param_1,1);
      }
      if (*pcVar2 != '\0') {
        *DAT_004c4468 = &local_18;
      }
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_14 & 1) == 1);
    }
    FUN_004c3ef4(&local_18);
  }
  else {
    local_14 = FUN_00473940();
    if (*DAT_004c4464 != '\0') {
      local_18 = *(undefined4 *)*DAT_004c4468;
    }
    *DAT_004c4468 = &local_18;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_14 & 1) == 1);
    }
    FUN_004c3ef4(&local_18);
    uVar5 = 0;
  }
  return CONCAT44(local_18,uVar5);
}

