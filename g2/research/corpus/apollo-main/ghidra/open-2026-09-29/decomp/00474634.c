
uint file_read(undefined4 param_1,uint param_2,int param_3,undefined4 *param_4)

{
  undefined4 *puVar1;
  int iVar2;
  uint uVar3;
  
  puVar1 = DAT_00474e48;
  iVar2 = osMutexAcquire(*DAT_00474e48,1000);
  if (iVar2 == 0) {
    uVar3 = FUN_004cfb40(*param_4,param_4 + 1,param_1,param_3 * param_2);
    osMutexRelease(*puVar1);
    if ((int)uVar3 < 0) {
      uVar3 = 0;
    }
    else {
      uVar3 = uVar3 / param_2;
    }
  }
  else {
    uVar3 = 0;
  }
  return uVar3;
}

