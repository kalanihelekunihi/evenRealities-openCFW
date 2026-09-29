
undefined8 FUN_004c3d9e(undefined1 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  char *pcVar2;
  char *pcVar3;
  int iVar4;
  int iVar5;
  undefined4 local_20;
  undefined4 local_1c;
  uint local_18;
  
  pcVar2 = DAT_004c43e8;
  iVar5 = 0;
  local_1c = 0x96;
  local_20 = param_2;
  if (*(int *)(DAT_004c43e8 + 4) == 0) {
    iVar5 = 7;
  }
  else {
    local_18 = param_4;
    iVar4 = FUN_004c37a8(2,param_1);
    if (iVar4 == 0) {
      local_18 = FUN_00473940();
      FUN_00480c56(&local_20);
      pcVar3 = DAT_004c4680;
      if (*DAT_004c4680 != '\0') {
        local_1c = *(undefined4 *)*DAT_004c4684;
      }
      if ((char)local_20 == '\0') {
        if (*pcVar2 == '\x01') {
          local_20 = CONCAT22(local_20._2_2_,0x100);
          FUN_004809c4(3,(int)&local_20 + 1);
        }
        else {
          FUN_004809c4(2,0);
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
        FUN_004c37fe(2,param_1,1);
      }
      if (*pcVar3 != '\0') {
        *DAT_004c4684 = &local_1c;
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_18 & 1) == 1);
      }
      FUN_004c3d70(&local_1c);
    }
    else {
      local_20 = FUN_00473940();
      if (*DAT_004c4680 != '\0') {
        local_1c = *(undefined4 *)*DAT_004c4684;
      }
      *DAT_004c4684 = &local_1c;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_20 & 1) == 1);
      }
      FUN_004c3d70(&local_1c);
      iVar5 = 0;
    }
  }
  return CONCAT44(local_20,iVar5);
}

