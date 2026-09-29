
undefined8 IMU_AIDStatePrint(uint param_1,uint param_2)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar4 = param_1;
  uVar5 = param_2;
  uVar1 = osKernelGetTickCount();
  if ((param_1 & 0xff) == 1) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = DAT_004a50e8;
      if ((param_2 & 0xff) != 0) {
        uVar3 = DAT_004a50e4;
      }
      uVar4 = 0x378;
      uVar5 = DAT_004a50d8;
      FUN_0043d574(3,DAT_004a5378,DAT_004a5374,DAT_004a50e0,0x378,DAT_004a50d8,uVar1,uVar3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      uVar4 = DAT_004a50e8;
      if ((param_2 & 0xff) != 0) {
        uVar4 = DAT_004a50e4;
      }
      compress_log_output(0xc800000,DAT_004a50dc,DAT_004a50dc,uVar1);
    }
  }
  else if ((param_1 & 0xff) == 2) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = DAT_004a50e8;
      if ((param_2 & 0xff) != 0) {
        uVar3 = DAT_004a50e4;
      }
      uVar4 = 0x37a;
      uVar5 = DAT_004a5294;
      FUN_0043d574(3,DAT_004a5378,DAT_004a5374,DAT_004a50e0,0x37a,DAT_004a5294,uVar1,uVar3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      uVar4 = DAT_004a50e8;
      if ((param_2 & 0xff) != 0) {
        uVar4 = DAT_004a50e4;
      }
      compress_log_output(0xc800000,DAT_004a5298,DAT_004a5298,uVar1);
    }
  }
  else if ((param_1 & 0xff) == 6) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = DAT_004a50e8;
      if ((param_2 & 0xff) != 0) {
        uVar3 = DAT_004a50e4;
      }
      uVar4 = 0x37c;
      uVar5 = DAT_004a529c;
      FUN_0043d574(3,DAT_004a5378,DAT_004a5374,DAT_004a50e0,0x37c,DAT_004a529c,uVar1,uVar3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      uVar4 = DAT_004a50e8;
      if ((param_2 & 0xff) != 0) {
        uVar4 = DAT_004a50e4;
      }
      compress_log_output(0xc800000,DAT_004a5480,DAT_004a5480,uVar1);
    }
  }
  return CONCAT44(uVar5,uVar4);
}

