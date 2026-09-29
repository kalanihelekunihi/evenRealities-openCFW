
undefined4 atFsListRecursive(undefined4 param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined1 auStack_98 [132];
  
  if (*DAT_005a56f4 == 1) {
    iVar2 = file_opendir(param_1);
    if (iVar2 == 0) {
      at_core_output(DAT_005a5700,param_1);
      uVar1 = 0;
    }
    else {
      FUN_0043c0e4(auStack_98,0x81,0);
      while (iVar3 = file_readdir(iVar2), iVar3 != 0) {
        iVar4 = FUN_0046cacc(iVar3,&DAT_005a56d0);
        if ((iVar4 != 0) && (iVar4 = FUN_0046cacc(iVar3,&DAT_005a56d4), iVar4 != 0)) {
          FUN_004b4728(auStack_98,&DAT_005a56d8,param_1);
          FUN_00567c80(auStack_98,iVar3);
          if (*(char *)(iVar3 + 0x100) == '\x04') {
            osDelay(0x1e);
            at_core_output(DAT_005a5704,auStack_98);
            atFsListRecursive(auStack_98);
          }
          else {
            osDelay(0x1e);
            iVar3 = file_open(auStack_98,&DAT_005a56dc);
            iVar4 = 0;
            if (iVar3 != 0) {
              file_seek(iVar3,0,2);
              iVar4 = file_tell(iVar3);
              file_close(iVar3);
            }
            at_core_output(DAT_005a5708,auStack_98,iVar4,iVar4 / 0x400);
          }
        }
      }
      file_closedir(iVar2);
      uVar1 = 1;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

