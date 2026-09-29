
int FUN_00470aac(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined *puVar3;
  byte local_14 [4];
  undefined4 uStack_10;
  
  if (*DAT_004710ac == 0) {
    iVar1 = 2;
  }
  else {
    uStack_10 = param_4;
    FUN_004703ba();
    iVar1 = FUN_00470168(5,0,0,local_14,1);
    if (iVar1 == 0) {
      if (((local_14[0] >> 6 & 1) == param_1) && ((local_14[0] & 0x3c) == 0)) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004710e4,DAT_004710e0,DAT_004710dc,0x52a,DAT_004710ec);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004710f0);
        }
        iVar1 = 0;
      }
      else {
        iVar1 = FUN_00470670();
        if (iVar1 == 0) {
          if (param_1 == 0) {
            local_14[0] = local_14[0] & 0xbf;
          }
          else {
            local_14[0] = local_14[0] | 0x40;
          }
          local_14[0] = local_14[0] & 0xc3;
          iVar1 = FUN_0047021c(1,0,0,local_14,1);
          if (iVar1 == 0) {
            FUN_004703ba();
            iVar1 = FUN_00470168(5,0,0,local_14,1);
            if (iVar1 == 0) {
              if ((local_14[0] >> 6 & 1) == param_1) {
                iVar1 = 0;
              }
              else {
                iVar1 = FUN_0043d0ce();
                if (iVar1 << 0x1e < 0) {
                  puVar3 = DAT_0047110c;
                  if (param_1 != 0) {
                    puVar3 = &DAT_00470f58;
                  }
                  FUN_0043d574(2,DAT_004710e4,DAT_004710e0,DAT_004710dc,0x550,DAT_00471110,puVar3);
                }
                iVar1 = FUN_0043d0ce();
                if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                  puVar3 = DAT_0047110c;
                  if (param_1 != 0) {
                    puVar3 = &DAT_00470f58;
                  }
                  compress_log_output(0x8400000,DAT_00471114,DAT_00471114,puVar3);
                }
                iVar1 = 1;
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                FUN_0043d574(2,DAT_004710e4,DAT_004710e0,DAT_004710dc,0x54a,DAT_00471104);
              }
              iVar2 = FUN_0043d0ce();
              if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
                compress_log_output(0x8000000,DAT_00471108,DAT_00471108);
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(2,DAT_004710e4,DAT_004710e0,DAT_004710dc,0x540,DAT_004710fc);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_00471100,DAT_00471100);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(2,DAT_004710e4,DAT_004710e0,DAT_004710dc,0x531,DAT_004710f4);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_004710f8,DAT_004710f8);
          }
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004710e4,DAT_004710e0,DAT_004710dc,0x521,DAT_004710d8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_004710e8,DAT_004710e8);
      }
    }
  }
  return iVar1;
}

