
undefined4
file_heap_free(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = DAT_00474e8c;
  iVar2 = osMutexAcquire(*DAT_00474e8c,1000);
  if (iVar2 == 0) {
    FUN_004d0808(*DAT_00474e90,param_1);
    osMutexRelease(*puVar1);
  }
  else {
    FUN_004733ee(DAT_00474e98);
    FUN_004d09b4(&DAT_00474e40,DAT_00474e54,0x43e);
  }
  return param_4;
}

