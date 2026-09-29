
undefined8
file_heap_reallocate(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = DAT_00474e8c;
  uVar3 = 0;
  iVar2 = osMutexAcquire(*DAT_00474e8c,1000);
  if (iVar2 == 0) {
    uVar3 = FUN_004d0868(*DAT_00474e90,param_1,param_2);
    osMutexRelease(*puVar1);
  }
  else {
    FUN_004733ee(DAT_00474e9c);
    FUN_004d09b4(&DAT_00474e40,DAT_00474e54,0x449);
  }
  return CONCAT44(param_4,uVar3);
}

