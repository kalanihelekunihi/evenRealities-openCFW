
undefined4 FUN_004c5dbc(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  ushort local_20 [2];
  int local_1c;
  undefined1 local_18;
  undefined1 local_17;
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  iVar2 = FUN_0045a568();
  if (iVar2 != 2) {
    FUN_0043c0e4(local_20,0xc,0);
    FUN_00439be4(local_20,param_2,param_3);
    if ((local_1c == 4) || (local_1c == 5)) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = FUN_004c5892(local_1c);
        uVar4 = FUN_004c58ee(local_20[0]);
        FUN_0043d574(3,DAT_004c6184,DAT_004c6180,DAT_004c61f8,0x122,DAT_004c61f4,uVar4,local_20[0],
                     uVar3,local_1c,local_18,local_17);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        uVar3 = FUN_004c5892(local_1c);
        uVar4 = FUN_004c58ee(local_20[0]);
        compress_log_output(0xd800000,DAT_004c61fc,DAT_004c61fc,uVar4,local_20[0],uVar3,local_1c,
                            local_18,local_17);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = FUN_004c5892(local_1c);
        uVar4 = FUN_004c58ee(local_20[0]);
        FUN_0043d574(3,DAT_004c6184,DAT_004c6180,DAT_004c61f8,0x128,DAT_004c6200,uVar4,local_20[0],
                     uVar3,local_1c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        uVar3 = FUN_004c5892(local_1c);
        uVar4 = FUN_004c58ee(local_20[0]);
        compress_log_output(0xd000000,DAT_004c6204,DAT_004c6204,uVar4,local_20[0],uVar3,local_1c);
      }
    }
    iVar2 = osKernelGetTickCount();
    FUN_004c5a58(local_20[0],local_1c,iVar2);
    FUN_004c5c6e(local_20[0],local_1c,iVar2);
    puVar1 = DAT_004c6208;
    if ((*DAT_004c6208 == 0xffff) || (*DAT_004c6208 == (uint)local_20[0])) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004c6184,DAT_004c6180,DAT_004c61f8,0x135,DAT_004c620c,*puVar1);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004c6210,DAT_004c6210,*puVar1);
      }
    }
    else {
      if ((uint)(iVar2 - *DAT_004c6214) < 0x3e9) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004c6184,DAT_004c6180,DAT_004c61f8,0x13f,DAT_004c6220);
        }
        iVar2 = FUN_0043d0ce();
        if ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d)) {
          return 0;
        }
        compress_log_output(0x8000000,DAT_004c6224,DAT_004c6224);
        return 0;
      }
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004c6184,DAT_004c6180,DAT_004c61f8,0x13a,DAT_004c6218);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004c621c,DAT_004c621c);
      }
    }
    *DAT_004c6214 = iVar2;
    if (local_1c == 0xe) {
      *puVar1 = 0xffff;
    }
    else {
      *puVar1 = (uint)local_20[0];
    }
    iVar2 = FUN_004c5c30();
    if (iVar2 == 0) {
      iVar2 = SVC_Settings_InputEventCheck();
      if (iVar2 == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004c6184,DAT_004c6180,DAT_004c61f8,0x157,DAT_004c6230);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004c6234,DAT_004c6234);
        }
      }
      else if (local_1c == 0x1010) {
        FUN_00464b2e(0x109,0,0,0);
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          uVar3 = FUN_004c5886(local_18,local_17);
          FUN_0043d574(4,DAT_004c6184,DAT_004c6180,DAT_004c61f8,0x161,DAT_004c6238,local_20[0],
                       local_1c,uVar3);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          uVar3 = FUN_004c5886(local_18,local_17);
          compress_log_output(0x10c00000,DAT_004c623c,DAT_004c623c,local_20[0],local_1c,uVar3);
        }
        uVar3 = FUN_004c5886(local_18,local_17);
        FUN_00465748(local_20[0],local_1c,uVar3,0);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004c6184,DAT_004c6180,DAT_004c61f8,0x151,DAT_004c6228);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_004c622c,DAT_004c622c);
      }
    }
  }
  return 0;
}

