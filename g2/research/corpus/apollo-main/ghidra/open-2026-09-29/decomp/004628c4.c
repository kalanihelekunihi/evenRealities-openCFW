
int FUN_004628c4(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004631bc,DAT_004631b8,DAT_004631b4,0x49e,DAT_004631b0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004631c0);
    }
  }
  else {
    FUN_0046018e();
    for (iVar2 = 0; iVar2 < *DAT_00462f28; iVar2 = iVar2 + 1) {
      uVar3 = FUN_00460084(param_1);
      uVar3 = FUN_0045fffe(param_1,uVar3);
      iVar1 = DAT_00463014;
      uVar4 = FUN_00460084(iVar2 * 0x34 + DAT_00463014 + 4);
      uVar4 = FUN_0045fffe(iVar2 * 0x34 + iVar1 + 4,uVar4);
      iVar5 = FUN_0046cacc(uVar4,uVar3);
      if (iVar5 == 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004631bc,DAT_004631b8,DAT_004631b4,0x4a5,DAT_004631c4,param_1,
                       *(undefined4 *)(iVar2 * 0x34 + iVar1 + 0x24),iVar2);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10c00000,DAT_004631c8,DAT_004631c8,param_1,
                              *(undefined4 *)(iVar1 + iVar2 * 0x34 + 0x24),iVar2);
        }
        FUN_004601ea();
        return iVar2;
      }
    }
    FUN_004601ea();
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004631bc,DAT_004631b8,DAT_004631b4,0x4ac,DAT_004631cc,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004631d0,DAT_004631d0,param_1);
    }
  }
  return -1;
}

