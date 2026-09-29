
undefined8 FUN_004704ac(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if (*DAT_004708a4 == 0) {
    iVar1 = 2;
  }
  else {
    iVar1 = FUN_004703ba();
    if (iVar1 == 0) {
      iVar1 = FUN_00470670();
      if (iVar1 == 0) {
        param_3 = 0;
        iVar1 = FUN_0047021c(0xb7,0,0,0,0,param_4);
        if (iVar1 == 0) {
          FUN_004703ba();
          iVar1 = FUN_004703c6();
          if (iVar1 == 0) {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              param_3 = 0x3de;
              FUN_0043d574(2,DAT_00470a7c,DAT_00470a78,DAT_00470d60,0x3de,DAT_00470d78);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_00470e84,DAT_00470e84);
            }
            iVar1 = 1;
          }
          else {
            iVar1 = FUN_004706e0();
            if (iVar1 == 0) {
              iVar1 = 0;
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                param_3 = 0x3e4;
                FUN_0043d574(2,DAT_00470a7c,DAT_00470a78,DAT_00470d60,0x3e4,DAT_00470e88);
              }
              iVar2 = FUN_0043d0ce();
              if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
                compress_log_output(0x8000000,DAT_0047100c,DAT_0047100c);
              }
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            param_3 = 0x3d6;
            FUN_0043d574(2,DAT_00470a7c,DAT_00470a78,DAT_00470d60,0x3d6,DAT_00470d70);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_00470d74,DAT_00470d74);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_3 = 0x3cf;
          FUN_0043d574(2,DAT_00470a7c,DAT_00470a78,DAT_00470d60,0x3cf,DAT_00470d68);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_00470d6c);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_3 = 0x3c8;
        FUN_0043d574(2,DAT_00470a7c,DAT_00470a78,DAT_00470d60,0x3c8,DAT_00470d5c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00470d64,DAT_00470d64);
      }
      iVar1 = 3;
    }
  }
  return CONCAT44(param_3,iVar1);
}

