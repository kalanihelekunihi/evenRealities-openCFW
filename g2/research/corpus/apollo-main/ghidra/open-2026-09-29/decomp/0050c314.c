
undefined8 FUN_0050c314(int param_1,uint param_2)

{
  undefined4 *puVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  
  uVar5 = param_2;
  if (param_1 == 0) {
    uVar3 = 0;
  }
  else {
    FUN_0050c3c0();
    puVar1 = DAT_0050c9b8;
    if (((int)param_2 < 0) || (*(int *)(DAT_0050c97c + 0xc0) <= (int)param_2)) {
      uVar3 = 0;
    }
    else {
      osMutexAcquire(*DAT_0050c9b8,0xffffffff);
      cVar2 = FUN_0050b19a(DAT_0050c9a8,param_2 & 0xffff);
      osMutexRelease(*puVar1);
      if (cVar2 == '\0') {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          uVar5 = 0x8b0;
          FUN_0043d574(2,DAT_0050c9c8,DAT_0050c9c4,DAT_0050c9c0,0x8b0,DAT_0050c9bc,param_2);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_0050c9cc,DAT_0050c9cc,param_2);
        }
        uVar3 = 0;
      }
      else {
        FUN_0050b438(param_1,param_2);
        uVar3 = 1;
      }
    }
  }
  return CONCAT44(uVar5,uVar3);
}

