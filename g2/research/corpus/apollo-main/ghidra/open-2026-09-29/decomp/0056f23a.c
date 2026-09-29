
int FUN_0056f23a(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0056fbe8,DAT_0056fbe4,DAT_0056fbf0,0x14a,DAT_0056fbec,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0056fbf4,DAT_0056fbf4);
    }
    iVar1 = -1;
  }
  else {
    iVar2 = file_tell(param_1);
    if (iVar2 < 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0056fbe8,DAT_0056fbe4,DAT_0056fbf0,0x150,DAT_0056fbf8);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0056fbfc);
      }
      iVar1 = -1;
    }
    else {
      iVar1 = file_seek(param_1,0,2);
      if (iVar1 == 0) {
        iVar1 = file_tell(param_1);
        if (iVar1 < 0) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0056fbe8,DAT_0056fbe4,DAT_0056fbf0,0x15b,DAT_0056fc08);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_0056fd98,DAT_0056fd98);
          }
        }
        iVar2 = file_seek(param_1,iVar2,0);
        if (iVar2 != 0) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(2,DAT_0056fbe8,DAT_0056fbe4,DAT_0056fbf0,0x15f,DAT_0056fd9c);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_0056fda0,DAT_0056fda0);
          }
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0056fbe8,DAT_0056fbe4,DAT_0056fbf0,0x161,DAT_0056fda4,iVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_0056ffac,DAT_0056ffac,iVar1);
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0056fbe8,DAT_0056fbe4,DAT_0056fbf0,0x155,DAT_0056fc00);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0056fc04,DAT_0056fc04);
        }
        iVar1 = -1;
      }
    }
  }
  return iVar1;
}

