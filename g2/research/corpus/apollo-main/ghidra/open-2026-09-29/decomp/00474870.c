
undefined8 file_tell(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = DAT_00474e48;
  if (param_1 == (undefined4 *)0x0) {
    iVar2 = -1;
  }
  else {
    iVar2 = osMutexAcquire(*DAT_00474e48,1000);
    if (iVar2 == 0) {
      iVar2 = FUN_004cfbe8(*param_1,param_1 + 1);
      osMutexRelease(*puVar1);
      if (iVar2 < 0) {
        iVar2 = -1;
      }
    }
    else {
      iVar2 = -1;
    }
  }
  return CONCAT44(param_4,iVar2);
}

