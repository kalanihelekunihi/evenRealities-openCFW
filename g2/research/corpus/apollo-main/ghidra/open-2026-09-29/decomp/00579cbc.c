
int SVC_CodecDfu(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 local_14;
  
  uVar1 = DAT_0057a3c4;
  iVar4 = -1;
  local_14 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_3 = 0x38400;
    param_1 = 0x29b;
    param_2 = DAT_0057a3c8;
    FUN_0043d574(4,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a3cc,0x29b,DAT_0057a3c8,0x38400);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0057a3d8,DAT_0057a3d8,0x38400,param_1,param_2,param_3);
  }
  iVar2 = semantic_CodecLoadFirmwarePackage();
  if (iVar2 < 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a3cc,0x29f,DAT_0057a3dc);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0057a3e0);
    }
    iVar4 = -1;
  }
  else {
    uart_init();
    iVar2 = FUN_0058fab6(0x38400);
    if (iVar2 == 0) {
      DRV_Gx8002_Reboot(1);
      iVar2 = 10000;
      local_14 = CONCAT31(local_14._1_3_,0xef);
      FUN_0058fb38(&local_14,1);
      while( true ) {
        iVar3 = FUN_0058fb2a((int)&local_14 + 1,1);
        if ((iVar3 != 0) && (local_14._1_1_ == 'M')) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a3cc,0x2c2,DAT_0057a3ec);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_0057a3f0,DAT_0057a3f0);
          }
          iVar2 = semantic_CodecReadBootHeader();
          if ((((-1 < iVar2) && (iVar2 = semantic_CodecDownloadBootStage1(uVar1), -1 < iVar2)) &&
              (iVar2 = semantic_CodecDownloadBootStage2(), -1 < iVar2)) &&
             (iVar2 = semantic_CodecFlashImage(), -1 < iVar2)) {
            uart_close();
            iVar4 = 0;
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(3,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a3cc,0x2d3,DAT_0057a3fc);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_0057a400,DAT_0057a400);
            }
          }
          goto LAB_00579ef4;
        }
        FUN_0058fb38(&local_14,1);
        FUN_004910f4(1);
        if (iVar2 < 1) break;
        iVar2 = iVar2 + -1;
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a3cc,700,DAT_0057a3f4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0057a3f8,DAT_0057a3f8);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a3cc,0x2a5,DAT_0057a3e4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0057a3e8,DAT_0057a3e8);
      }
    }
LAB_00579ef4:
    if (iVar4 != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a3cc,0x2d7,DAT_0057a404);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0057a408,DAT_0057a408);
      }
      uart_close();
    }
    DRV_Gx8002_Reboot(0);
    semantic_CodecFreeFirmwareBuffers();
  }
  return iVar4;
}

