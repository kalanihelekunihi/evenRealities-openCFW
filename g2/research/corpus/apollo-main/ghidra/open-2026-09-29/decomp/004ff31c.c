
undefined4 FUN_004ff31c(int param_1,uint param_2)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined8 in_d0;
  float fVar4;
  
  fVar4 = (float)((ulonglong)in_d0 >> 0x20);
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ff4a8,DAT_004ff4a4,DAT_004ff87c,0x65c,DAT_004ff878);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ff880);
    }
    uVar2 = 0;
  }
  else if (param_2 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004ff4a8,DAT_004ff4a4,DAT_004ff87c,0x661,DAT_004ff884);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004ff888,DAT_004ff888);
    }
    uVar2 = 0;
  }
  else if (param_2 < 0xba) {
    if ((int)((uint)((float)in_d0 < fVar4) << 0x1f) < 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004ff4a8,DAT_004ff4a4,DAT_004ff87c,0x66b,DAT_004ff894,
                     (double)(float)in_d0,(double)fVar4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_004ff898,DAT_004ff898);
      }
      uVar2 = 0;
    }
    else {
      for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
      }
      uVar2 = 1;
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ff4a8,DAT_004ff4a4,DAT_004ff87c,0x666,DAT_004ff88c,param_2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004ff890,DAT_004ff890,param_2);
    }
    uVar2 = 0;
  }
  return uVar2;
}

