
undefined8 pt_cmd_59_handler(int param_1,uint param_2,int param_3,uint param_4)

{
  int *piVar1;
  uint *puVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar5 = param_2;
  uVar6 = param_4;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    uVar5 = 0xca4;
    FUN_0043d574(3,DAT_005768bc,DAT_005768b8,DAT_005768b4,0xca4,DAT_005768b0,uVar6);
  }
  iVar3 = FUN_0043d0ce();
  if (-1 < iVar3 << 0x1f) {
    iVar3 = FUN_0043d0ce();
    if (-1 < iVar3 << 0x1d) goto LAB_00575f02;
  }
  compress_log_output(0xc000000,DAT_005768c0,DAT_005768c0);
LAB_00575f02:
  piVar1 = DAT_00576a3c;
  if ((((param_1 == 0) || (param_3 == 0)) || (param_4 == 0)) || ((param_2 & 0xff) < 4)) {
    iVar3 = FUN_0043d0ce();
    param_4 = uVar5;
    if (iVar3 << 0x1e < 0) {
      param_4 = 0xca6;
      FUN_0043d574(1,DAT_005768bc,DAT_005768b8,DAT_005768b4,0xca6,DAT_005768c4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00576a2c,DAT_00576a2c);
    }
    uVar4 = 0xffffffff;
  }
  else if (*(int *)(DAT_00576a30 + 4) < 0x32) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005768bc,DAT_005768b8,DAT_005768b4,0xcac,DAT_00576a34);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00576a38,DAT_00576a38);
    }
    uVar4 = pt_handler_result(0x59,1,2,param_3);
  }
  else {
    if (*DAT_00576a3c != 0) {
      file_close(*DAT_00576a3c);
      *piVar1 = 0;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_005768bc,DAT_005768b8,DAT_005768b4,0xcb4,DAT_00576a40);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00576a44,DAT_00576a44);
      }
    }
    iVar3 = file_open(DAT_00576700,&DAT_005760f8);
    if (iVar3 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005768bc,DAT_005768b8,DAT_005768b4,0xcbb,DAT_00576704);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00576708,DAT_00576708);
      }
      uVar4 = pt_handler_result(0x59,1,2,param_3);
    }
    else {
      *piVar1 = iVar3;
      *DAT_00576a48 = 1;
      puVar2 = DAT_00576a4c;
      uVar5 = xTaskGetTickCount();
      *puVar2 = uVar5 / 1000;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005768bc,DAT_005768b8,DAT_005768b4,0xcc5,DAT_00576a50,*puVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00576dd4,DAT_00576dd4,*puVar2);
      }
      uVar4 = pt_handler_result(0x59,0,2,param_3);
    }
  }
  return CONCAT44(param_4,uVar4);
}

