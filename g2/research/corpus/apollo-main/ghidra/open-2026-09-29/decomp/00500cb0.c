
undefined4 FUN_00500cb0(int param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00501188,DAT_00501184,DAT_005017c0,0x16d,DAT_005017bc,param_1,param_2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_005017c4,DAT_005017c4,param_1,param_2);
    }
    uVar3 = 0xffffffff;
  }
  else {
    iVar2 = FUN_00558632();
    uVar3 = DAT_005017d0;
    if (iVar2 == 0) {
      file_remove(DAT_005017d0);
      iVar2 = file_open(uVar3,&LAB_00500efc);
      if (iVar2 == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00501188,DAT_00501184,DAT_005017c0,0x17d,DAT_005017d4,uVar3);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_005017d8,DAT_005017d8,uVar3);
        }
        uVar3 = 0xffffffff;
      }
      else {
        iVar4 = file_write(param_1,1,param_2,iVar2);
        iVar2 = file_close(iVar2);
        uVar1 = DAT_005017e4;
        if ((iVar4 == param_2) && (iVar2 == 0)) {
          iVar2 = file_rename(uVar3,DAT_005017e4);
          if (iVar2 == 0) {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(3,DAT_00501188,DAT_00501184,DAT_005017c0,0x195,DAT_005017f0,param_2,uVar1
                          );
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0xc800000,DAT_005017f4,DAT_005017f4,param_2,uVar1);
            }
            uVar3 = 0;
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(1,DAT_00501188,DAT_00501184,DAT_005017c0,399,DAT_005017e8,uVar3,uVar1);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x4800000,DAT_005017ec,DAT_005017ec,uVar3,uVar1);
            }
            file_remove(uVar3);
            uVar3 = 0xffffffff;
          }
        }
        else {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00501188,DAT_00501184,DAT_005017c0,0x185,DAT_005017dc,iVar4,param_2,
                         iVar2);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4c00000,DAT_005017e0,DAT_005017e0,iVar4,param_2,iVar2);
          }
          file_remove(uVar3);
          uVar3 = 0xffffffff;
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00501188,DAT_00501184,DAT_005017c0,0x172,DAT_005017c8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_005017cc,DAT_005017cc);
      }
      uVar3 = 0xffffffff;
    }
  }
  return uVar3;
}

