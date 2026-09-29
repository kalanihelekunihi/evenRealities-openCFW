
undefined8 FUN_00421bd2(undefined1 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  char *pcVar2;
  char *pcVar3;
  int iVar4;
  int iVar5;
  undefined4 local_20;
  undefined4 local_1c;
  uint local_18;
  
  pcVar2 = DAT_0042221c;
  iVar5 = 0;
  local_1c = 0x96;
  local_20 = param_2;
  if (*(int *)(DAT_0042221c + 4) == 0) {
    iVar5 = 7;
  }
  else {
    local_18 = param_4;
    iVar4 = FUN_004215dc(2,param_1);
    if (iVar4 == 0) {
      local_18 = critical_save();
      FUN_0041d676(&local_20);
      pcVar3 = DAT_00422444;
      if (*DAT_00422444 != '\0') {
        local_1c = *(undefined4 *)*DAT_00422448;
      }
      if ((char)local_20 == '\0') {
        if (*pcVar2 == '\x01') {
          local_20 = CONCAT22(local_20._2_2_,0x100);
          FUN_0041d3e4(3,(int)&local_20 + 1);
        }
        else {
          FUN_0041d3e4(2,0);
          if (*pcVar3 == '\0') {
            *pcVar3 = '\x01';
          }
        }
      }
      else if (((char)local_20 == '\x02') && (*pcVar2 == '\0')) {
        iVar5 = 3;
      }
      else if (((char)local_20 == '\x01') && (*pcVar2 == '\x01')) {
        iVar5 = 3;
      }
      if (iVar5 == 0) {
        FUN_00421632(2,param_1,1);
      }
      if (*pcVar3 != '\0') {
        *DAT_00422448 = &local_1c;
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_18 & 1) == 1);
      }
      FUN_00421ba4(&local_1c);
    }
    else {
      local_20 = critical_save();
      if (*DAT_00422444 != '\0') {
        local_1c = *(undefined4 *)*DAT_00422448;
      }
      *DAT_00422448 = &local_1c;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_20 & 1) == 1);
      }
      FUN_00421ba4(&local_1c);
      iVar5 = 0;
    }
  }
  return CONCAT44(local_20,iVar5);
}

