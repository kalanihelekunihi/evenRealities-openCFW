
undefined8
file_runtime_initialize(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  
  piVar1 = DAT_00474e48;
  iVar3 = osMutexNew(0);
  *piVar1 = iVar3;
  piVar2 = DAT_00474e8c;
  iVar3 = osMutexNew(0);
  *piVar2 = iVar3;
  if ((*piVar1 == 0) || (*piVar2 == 0)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x47a;
      FUN_0043d574(1,DAT_00474e58,DAT_00474e54,DAT_00474ea4,0x47a,DAT_00474ea0,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00474ea8,DAT_00474ea8);
    }
    uVar4 = 0xffffffff;
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x47e;
      FUN_0043d574(3,DAT_00474e58,DAT_00474e54,DAT_00474ea4,0x47e,DAT_00474eac,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_00474eb0,DAT_00474eb0);
    }
    uVar4 = 0;
  }
  return CONCAT44(param_2,uVar4);
}

