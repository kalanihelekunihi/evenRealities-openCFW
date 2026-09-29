
undefined8 file_open(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;
  uint uVar4;
  
  puVar2 = (undefined4 *)file_heap_allocate(0x60);
  if (puVar2 == (undefined4 *)0x0) {
    puVar2 = (undefined4 *)0x0;
  }
  else {
    *puVar2 = DAT_00474e44;
    iVar3 = FUN_0044b63a(param_2,&DAT_00474804);
    uVar4 = (uint)(iVar3 != 0);
    iVar3 = FUN_0044b63a(param_2,&DAT_00474808);
    if (iVar3 != 0) {
      uVar4 = uVar4 | 0x502;
    }
    iVar3 = FUN_0044b63a(param_2,&DAT_0047480c);
    if (iVar3 != 0) {
      uVar4 = uVar4 | 0x902;
    }
    iVar3 = FUN_0044b63a(param_2,&DAT_00474810);
    puVar1 = DAT_00474e48;
    if (iVar3 != 0) {
      uVar4 = uVar4 | 3;
    }
    iVar3 = osMutexAcquire(*DAT_00474e48,1000);
    if (iVar3 == 0) {
      iVar3 = FUN_004cfa94(*puVar2,puVar2 + 1,param_1,uVar4);
      osMutexRelease(*puVar1);
      if (iVar3 < 0) {
        file_heap_free(puVar2);
        puVar2 = (undefined4 *)0x0;
      }
    }
    else {
      file_heap_free(puVar2);
      puVar2 = (undefined4 *)0x0;
    }
  }
  return CONCAT44(param_4,puVar2);
}

