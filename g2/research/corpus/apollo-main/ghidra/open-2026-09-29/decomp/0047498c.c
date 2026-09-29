
undefined8 file_remove(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  int iVar3;
  
  puVar2 = DAT_00474e48;
  if (*DAT_00474e84 == 1) {
    if (param_1 == 0) {
      puVar2 = (undefined4 *)FUN_00439cc4();
      *puVar2 = 0x16;
      uVar1 = 0xffffffff;
    }
    else {
      iVar3 = osMutexAcquire(*DAT_00474e48,1000);
      if (iVar3 == 0) {
        iVar3 = FUN_004cfa76(DAT_00474e44,param_1);
        osMutexRelease(*puVar2);
        if (iVar3 < 0) {
          if (iVar3 == -2) {
            uVar1 = 0;
          }
          else {
            puVar2 = (undefined4 *)FUN_00439cc4();
            *puVar2 = 5;
            uVar1 = 0xffffffff;
          }
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
  }
  else {
    uVar1 = 0;
  }
  return CONCAT44(param_4,uVar1);
}

