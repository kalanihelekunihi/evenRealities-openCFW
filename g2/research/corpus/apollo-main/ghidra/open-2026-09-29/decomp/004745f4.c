
undefined4 file_close(undefined4 *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = DAT_00474e48;
  iVar2 = osMutexAcquire(*DAT_00474e48,1000);
  if (iVar2 == 0) {
    iVar2 = FUN_004cfad0(*param_1,param_1 + 1);
    osMutexRelease(*puVar1);
    file_heap_free(param_1);
    if (iVar2 < 0) {
      uVar3 = 0xffffffff;
    }
    else {
      uVar3 = 0;
    }
  }
  else {
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

