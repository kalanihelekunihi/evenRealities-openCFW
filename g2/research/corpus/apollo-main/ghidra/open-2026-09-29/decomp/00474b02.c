
undefined4 * file_opendir(int param_1)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 uVar4;
  
  if (*DAT_00474e84 == 1) {
    if (param_1 == 0) {
      puVar2 = (undefined4 *)FUN_00439cc4();
      *puVar2 = 0x16;
      puVar2 = (undefined4 *)0x0;
    }
    else {
      puVar2 = (undefined4 *)file_heap_allocate(0x240);
      if (puVar2 == (undefined4 *)0x0) {
        puVar2 = (undefined4 *)FUN_00439cc4();
        *puVar2 = 0xc;
        puVar2 = (undefined4 *)0x0;
      }
      else {
        *puVar2 = DAT_00474e44;
        FUN_0044b5a0(puVar2 + 0x50,param_1,0xff);
        *(undefined1 *)((int)puVar2 + 0x23f) = 0;
        puVar1 = DAT_00474e48;
        iVar3 = osMutexAcquire(*DAT_00474e48,1000);
        if (iVar3 == 0) {
          iVar3 = FUN_004cfc66(*puVar2,puVar2 + 1,param_1);
          osMutexRelease(*puVar1);
          if (iVar3 < 0) {
            file_heap_free(puVar2);
            puVar2 = (undefined4 *)FUN_00439cc4();
            if (iVar3 == -2) {
              uVar4 = 2;
            }
            else {
              uVar4 = 5;
            }
            *puVar2 = uVar4;
            puVar2 = (undefined4 *)0x0;
          }
        }
        else {
          file_heap_free(puVar2);
          puVar2 = (undefined4 *)FUN_00439cc4();
          *puVar2 = 0x10;
          puVar2 = (undefined4 *)0x0;
        }
      }
    }
  }
  else {
    puVar2 = (undefined4 *)FUN_00439cc4();
    *puVar2 = 2;
    puVar2 = (undefined4 *)0x0;
  }
  return puVar2;
}

