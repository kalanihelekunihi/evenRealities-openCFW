
int file_readdir(undefined4 *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  
  puVar1 = DAT_00474e48;
  if (*DAT_00474e84 == 1) {
    if (param_1 == (undefined4 *)0x0) {
      puVar1 = (undefined4 *)FUN_00439cc4();
      *puVar1 = 9;
      iVar2 = 0;
    }
    else {
      iVar2 = osMutexAcquire(*DAT_00474e48,1000);
      if (iVar2 == 0) {
        iVar3 = FUN_004cfd02(*param_1,param_1 + 1,param_1 + 0xe);
        osMutexRelease(*puVar1);
        iVar2 = DAT_00474e88;
        if (iVar3 < 0) {
          puVar1 = (undefined4 *)FUN_00439cc4();
          *puVar1 = 5;
          iVar2 = 0;
        }
        else if (iVar3 == 0) {
          iVar2 = 0;
        }
        else {
          FUN_0044b5a0(DAT_00474e88,param_1 + 0x10,0xff);
          *(undefined1 *)(iVar2 + 0xff) = 0;
          if (*(char *)(param_1 + 0xe) == '\x02') {
            *(undefined1 *)(iVar2 + 0x100) = 4;
          }
          else if (*(char *)(param_1 + 0xe) == '\x01') {
            *(undefined1 *)(iVar2 + 0x100) = 8;
          }
          else {
            *(undefined1 *)(iVar2 + 0x100) = 0;
          }
        }
      }
      else {
        puVar1 = (undefined4 *)FUN_00439cc4();
        *puVar1 = 0x10;
        iVar2 = 0;
      }
    }
  }
  else {
    puVar1 = (undefined4 *)FUN_00439cc4();
    *puVar1 = 9;
    iVar2 = 0;
  }
  return iVar2;
}

