
int _write_file_version_header(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_38 [40];
  undefined4 uStack_10;
  
  if (param_1 == 0) {
    iVar1 = 0;
  }
  else {
    uStack_10 = param_4;
    iVar2 = FUN_0044b728(auStack_38,0x28,DAT_0044a9d4,DAT_0044a9d0);
    if (iVar2 - 1U < 0x27) {
      file_seek(param_1,0,0);
      iVar1 = file_write(auStack_38,1,iVar2,param_1);
      if (iVar1 != iVar2) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,DAT_0044a9e4,DAT_0044a9e0,DAT_0044a9dc,0xb4,DAT_0044a9ec,iVar1,iVar2);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8800000,DAT_0044a9f0,DAT_0044a9f0,iVar1,iVar2);
        }
        iVar1 = 0;
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0044a9e4,DAT_0044a9e0,DAT_0044a9dc,0xad,DAT_0044a9d8,iVar2);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0044a9e8,DAT_0044a9e8,iVar2);
      }
      iVar1 = 0;
    }
  }
  return iVar1;
}

