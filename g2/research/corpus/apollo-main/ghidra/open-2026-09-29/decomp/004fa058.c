
void FUN_004fa058(int param_1,undefined4 param_2,int param_3,char param_4,int param_5,
                 undefined4 param_6)

{
  int *piVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  
  if (param_4 == '\x02') {
    iVar3 = FUN_004f9f14(2,param_6);
    iVar6 = iVar3 + param_1;
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004fa710,DAT_004fa400,DAT_004fac40,0x105f,DAT_004fab0c,param_1,param_5,
                   iVar3,iVar6);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x11000000,DAT_004fab10,DAT_004fab10,param_1,param_5,iVar3,iVar6);
    }
  }
  else {
    iVar6 = param_1;
    if (param_4 == '\x03') {
      uVar5 = FUN_004f9f14(3,param_6);
      iVar6 = param_1 - param_5;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004fa710,DAT_004fa400,DAT_004fac40,0x1069,DAT_004fac44,param_1,param_5,
                     uVar5,iVar6);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x11000000,DAT_004fac48,DAT_004fac48,param_1,param_5,uVar5,iVar6);
      }
    }
  }
  piVar1 = DAT_004faa2c;
  if (((-1 < *DAT_004faa2c) && (*DAT_004faa2c < (int)(uint)*DAT_004fac4c)) &&
     (*(int *)(DAT_004faa38 + *DAT_004faa2c * 0x10) != 0)) {
    iVar3 = FUN_0043fce0(*(undefined4 *)(DAT_004faa38 + *DAT_004faa2c * 0x10));
    iVar7 = iVar3 - param_3;
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004fa710,DAT_004fa400,DAT_004fac40,0x1076,DAT_004fac50,iVar3,param_3,iVar7)
      ;
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_004fac54,DAT_004fac54,iVar3,param_3,iVar7);
    }
    if (-1 < iVar7) {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004fa710,DAT_004fa400,DAT_004fac40,0x107b,DAT_004fac58,iVar7);
      }
      iVar3 = FUN_0043d0ce();
      iVar6 = iVar7;
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004fac5c,DAT_004fac5c,iVar7);
      }
    }
  }
  puVar2 = DAT_004fac60;
  uVar5 = FUN_004f6d84(*DAT_004fac60,iVar6);
  FUN_0044ea04(*puVar2,uVar5,0);
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004fa710,DAT_004fa400,DAT_004fac40,0x1087,DAT_004fac64,param_1,uVar5,param_4,
                 *piVar1);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0x11000000,DAT_004faf84,DAT_004faf84,param_1,uVar5,param_4,*piVar1);
  }
  return;
}

