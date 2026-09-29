
undefined8 FUN_0050c288(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  char cVar2;
  int iVar3;
  
  puVar1 = DAT_0050c30c;
  osMutexAcquire(*DAT_0050c30c,0xffffffff);
  cVar2 = FUN_0050b18c(DAT_0050c9a8);
  osMutexRelease(*puVar1);
  if (cVar2 == '\0') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x88d;
      param_3 = DAT_0050c9ac;
      FUN_0043d574(2,DAT_0050c2fc,DAT_0050c2f8,DAT_0050c9b0,0x88d,DAT_0050c9ac,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050c9b4,DAT_0050c9b4);
    }
  }
  return CONCAT44(param_3,param_2);
}

