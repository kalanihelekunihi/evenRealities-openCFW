
undefined4 file_heap_allocate(undefined4 param_1)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = DAT_00474e8c;
  uVar3 = 0;
  iVar2 = osMutexAcquire(*DAT_00474e8c,1000);
  if (iVar2 == 0) {
    uVar3 = FUN_004d0722(*DAT_00474e90,param_1);
    osMutexRelease(*puVar1);
  }
  else {
    FUN_004733ee(DAT_00474e94);
    FUN_004d09b4(&DAT_00474e40,DAT_00474e54,0x432);
  }
  return uVar3;
}

