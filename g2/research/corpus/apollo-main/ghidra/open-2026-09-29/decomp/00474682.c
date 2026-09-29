
uint file_write(undefined4 param_1,uint param_2,int param_3,undefined4 *param_4)

{
  undefined4 *puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = DAT_00474e48;
  uVar4 = param_3 * param_2;
  if (param_4 == (undefined4 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00474e58,DAT_00474e54,DAT_00474e50,0x236,DAT_00474e4c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00474e5c,DAT_00474e5c);
    }
    uVar3 = 0;
  }
  else {
    iVar2 = osMutexAcquire(*DAT_00474e48,1000,param_3,param_4,param_1,param_2,param_3,param_4);
    if (iVar2 == 0) {
      uVar3 = FUN_004cfb7c(*param_4,param_4 + 1,param_1,uVar4);
      osMutexRelease(*puVar1);
      if ((int)uVar3 < 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00474e58,DAT_00474e54,DAT_00474e50,0x24a,DAT_00474e68,uVar3,uVar4);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_00474e6c,DAT_00474e6c,uVar3,uVar4);
        }
        uVar3 = 0;
      }
      else {
        if (uVar3 < uVar4) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(2,DAT_00474e58,DAT_00474e54,DAT_00474e50,0x24e,DAT_00474e70,uVar3,uVar4);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x8800000,DAT_00474e74,DAT_00474e74,uVar3,uVar4);
          }
        }
        uVar3 = uVar3 / param_2;
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00474e58,DAT_00474e54,DAT_00474e50,0x23c,DAT_00474e60,uVar4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00474e64,DAT_00474e64,uVar4);
      }
      uVar3 = 0;
    }
  }
  return uVar3;
}

