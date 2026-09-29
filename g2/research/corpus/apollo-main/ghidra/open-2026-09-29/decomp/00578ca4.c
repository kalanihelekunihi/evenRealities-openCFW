
undefined4
semantic_CodecDownloadBootStage1
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  iVar4 = 0;
  iVar5 = *DAT_0057965c + 0x20;
  iVar2 = FUN_0043d0ce(*DAT_0057965c,0,param_3,param_4,param_1,param_2,param_3,param_4);
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_00579664,0x1bf,DAT_00579660);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00579668,DAT_00579668);
  }
  puVar1 = DAT_005799e4;
  iVar2 = DAT_00579658;
  iVar6 = *(int *)(DAT_00579658 + 8) / 4;
  *DAT_005799e4 = 0x59;
  puVar1[1] = (char)iVar6;
  puVar1[2] = (char)((uint)iVar6 >> 8);
  puVar1[3] = (char)((uint)iVar6 >> 0x10);
  puVar1[4] = (char)((uint)iVar6 >> 0x18);
  FUN_0058fb38(puVar1,5);
  if (*(char *)(iVar2 + 2) == '\x01') {
    iVar6 = iVar6 << 2;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_00579664,0x1cd,DAT_0057966c);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00579670,DAT_00579670);
  }
  for (; iVar4 < iVar6; iVar4 = iVar4 + 0x100) {
    FUN_00439be4(puVar1,iVar5,0x100);
    iVar5 = iVar5 + 0x100;
    FUN_0058fb38(puVar1,0x100);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_00579664,0x1d6,DAT_00579674,iVar4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00579678,DAT_00579678,iVar4);
  }
  iVar2 = semantic_CodecWaitForUartToken(&DAT_00579088,10000);
  if (iVar2 < 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00579164,DAT_00579160,DAT_00579664,0x1d8,DAT_0057967c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00579680,DAT_00579680);
    }
    uVar3 = 0xffffffff;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_00579664,0x1db,DAT_00579684);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00579688,DAT_00579688);
    }
    iVar2 = semantic_CodecWaitForUartToken(&DAT_00579124,10000);
    if (iVar2 == 0) {
      FUN_004b4728(puVar1,&DAT_00579128);
      uVar3 = FUN_0044a43c(puVar1);
      FUN_0058fb38(puVar1,uVar3);
      *puVar1 = (char)param_1;
      puVar1[1] = (char)((uint)param_1 >> 8);
      puVar1[2] = (char)((uint)param_1 >> 0x10);
      puVar1[3] = (char)((uint)param_1 >> 0x18);
      FUN_0058fb38(puVar1,4);
      iVar2 = semantic_CodecWaitForUartToken(&DAT_00579128,10000);
      if (iVar2 == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_00579664,499,DAT_0057969c,param_1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_005796a0,DAT_005796a0,param_1);
        }
        iVar2 = FUN_0058fab6(param_1);
        if (iVar2 == 0) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_00579664,0x1f9,DAT_005796ac);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_005796b0,DAT_005796b0);
          }
          iVar2 = semantic_CodecWaitForUartToken(&DAT_0057913c,10000);
          if (iVar2 < 0) {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(2,DAT_00579164,DAT_00579160,DAT_00579664,0x1fb,DAT_005796b4);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_005796b8,DAT_005796b8);
            }
            uVar3 = 0xffffffff;
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_00579664,0x1fe,DAT_005796bc);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x10000000,DAT_005796c0,DAT_005796c0);
            }
            *puVar1 = 0x4f;
            puVar1[1] = 0x4b;
            FUN_0058fb38(puVar1,2);
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_00579664,0x204,DAT_005796c4);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x10000000,DAT_00579c6c,DAT_00579c6c);
            }
            uVar3 = 0;
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(2,DAT_00579164,DAT_00579160,DAT_00579664,0x1f5,DAT_005796a4);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_005796a8,DAT_005796a8);
          }
          uVar3 = 0xffffffff;
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00579164,DAT_00579160,DAT_00579664,0x1ee,DAT_00579694);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_00579698,DAT_00579698);
        }
        uVar3 = 0xffffffff;
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_00579164,DAT_00579160,DAT_00579664,0x1de,DAT_0057968c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00579690,DAT_00579690);
      }
      uVar3 = 0xffffffff;
    }
  }
  return uVar3;
}

