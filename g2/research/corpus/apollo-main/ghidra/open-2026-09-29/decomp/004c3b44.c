
int FUN_004c3b44(undefined4 param_1,char *param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  char local_24 [12];
  undefined4 uStack_18;
  
  iVar5 = 0;
  local_24[0] = '\0';
  local_24[1] = '\0';
  local_24[2] = '\0';
  local_24[3] = '\0';
  local_24[4] = '\0';
  local_24[5] = '\0';
  local_24[6] = '\0';
  local_24[7] = '\0';
  local_24[8] = '\0';
  local_24[9] = '\0';
  local_24[10] = '\0';
  local_24[0xb] = '\0';
  uStack_18 = param_4;
  if (param_2 == (char *)0x0) {
    if (*(int *)(DAT_004c43e8 + 4) == 0) {
      if (*(int *)(DAT_004c43e8 + 0x10) == 0) {
        return 7;
      }
      local_24[0] = '\x01';
      local_24[1] = '\0';
      local_24[2] = '\0';
      local_24[3] = '\0';
      uVar4 = *(undefined4 *)(DAT_004c43e8 + 0x10);
    }
    else {
      local_24[0] = '\0';
      local_24[1] = '\0';
      local_24[2] = '\0';
      local_24[3] = '\0';
      uVar4 = *(undefined4 *)(DAT_004c43e8 + 4);
    }
    iVar5 = FUN_00539794(local_24,uVar4,param_1);
    param_2 = local_24;
  }
  else {
    if ((*param_2 == '\0') && (*(int *)(DAT_004c43e8 + 4) == 0)) {
      return 7;
    }
    if ((*param_2 == '\x01') && (*(int *)(DAT_004c43e8 + 0x10) == 0)) {
      return 7;
    }
  }
  if (iVar5 == 0) {
    uVar2 = FUN_00473940();
    iVar3 = FUN_004c37ca(6);
    if (iVar3 != 0) {
      iVar5 = 3;
    }
    if (iVar5 == 0) {
      FUN_00439be4(DAT_004c4654,param_2,0xc);
      *DAT_004c4658 = param_1;
      *DAT_004c4674 = 1;
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uVar2 & 1) == 1);
    }
  }
  return iVar5;
}

