
undefined8 file_flush(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  int iVar3;
  
  puVar2 = DAT_00474e48;
  if ((((param_1 == (undefined4 *)0x0) || (param_1 == DAT_00474e78)) || (param_1 == DAT_00474e7c))
     || (param_1 == DAT_00474e80)) {
    uVar1 = 0;
  }
  else if (param_1 == (undefined4 *)0x0) {
    puVar2 = (undefined4 *)FUN_00439cc4();
    *puVar2 = 9;
    uVar1 = 0xffffffff;
  }
  else {
    iVar3 = osMutexAcquire(*DAT_00474e48,1000);
    if (iVar3 == 0) {
      iVar3 = FUN_004cfb08(*param_1,param_1 + 1);
      osMutexRelease(*puVar2);
      if (iVar3 < 0) {
        puVar2 = (undefined4 *)FUN_00439cc4();
        *puVar2 = 5;
        uVar1 = 0xffffffff;
      }
      else {
        uVar1 = 0;
      }
    }
    else {
      puVar2 = (undefined4 *)FUN_00439cc4();
      *puVar2 = 0x10;
      uVar1 = 0xffffffff;
    }
  }
  return CONCAT44(param_4,uVar1);
}

