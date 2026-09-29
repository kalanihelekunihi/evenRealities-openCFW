
undefined4 FUN_004f8644(char *param_1,int param_2)

{
  int *piVar1;
  int *piVar2;
  short *psVar3;
  int *piVar4;
  int *piVar5;
  int iVar6;
  undefined4 local_30;
  uint local_2c;
  uint local_28;
  byte local_24 [3];
  undefined1 local_21;
  undefined1 local_20;
  
  psVar3 = DAT_004f9350;
  piVar1 = DAT_004f9348;
  if (*DAT_004f92e0 == 0) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      local_2c = DAT_004f92e4;
      local_30 = 0xc55;
      FUN_0043d574(2,DAT_004f8918,DAT_004f8914,DAT_004f92e8);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004f92ec);
    }
  }
  else if ((param_1 == (char *)0x0) || (param_2 == 0)) {
    if (*(int *)(DAT_004f934c + *DAT_004f9348 * 8 + 4) != 0) {
      FUN_004fb1a4(*(undefined4 *)(DAT_004f934c + *DAT_004f9348 * 8 + 4),0);
    }
    FUN_004f891c(*piVar1);
  }
  else if (*param_1 == '\0') {
    *(char *)(DAT_004f9350 + 0x1727) = param_1[1];
    psVar3[0x1724] = *(short *)(param_1 + 2);
    piVar5 = DAT_004f935c;
    piVar4 = DAT_004f9358;
    piVar2 = DAT_004f9348;
    piVar1 = DAT_004f88d4;
    if (((*DAT_004f9354 == 1) && (*DAT_004f9358 != 0)) && (*DAT_004f935c != 0)) {
      if (*DAT_004f88d4 == 0) {
        *DAT_004f88d4 = 2;
        if ((*psVar3 == 0) || (*DAT_004f9360 == '\0')) {
          FUN_004fb1a4(*piVar5,1);
        }
        FUN_004fac74(*piVar5);
        if (*piVar1 == 2) {
          *piVar1 = 0;
        }
      }
      else {
        FUN_0043c0e4(local_24,5,0);
        local_24[0] = 0x47;
        local_24[1] = 0;
        local_24[2] = (byte)psVar3[0x1727];
        local_21 = (undefined1)psVar3[0x1724];
        local_20 = (undefined1)((ushort)psVar3[0x1724] >> 8);
        ui_common_api_fn_00509ca2(*piVar4,local_24,5);
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          local_28 = (uint)local_24[0];
          local_2c = DAT_004f9364;
          local_30 = 0xc7e;
          FUN_0043d574(3,DAT_004f8918,DAT_004f8914,DAT_004f92e8);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_004f9468,DAT_004f9468,local_24[0]);
        }
      }
    }
    else {
      if (*(int *)(DAT_004f934c + *DAT_004f9348 * 8 + 4) != 0) {
        FUN_004fb1a4(*(undefined4 *)(DAT_004f934c + *DAT_004f9348 * 8 + 4),0);
      }
      FUN_004f5596();
      FUN_004f891c(*piVar2);
    }
    *(undefined1 *)(psVar3 + 0x1727) = 0;
    psVar3[0x1724] = 0;
  }
  else if (*param_1 == '\x01') {
    if (*DAT_004f88d4 == 0) {
      if (((*DAT_004f9354 == 1) && (*DAT_004f9358 != 0)) && (*DAT_004f935c != 0)) {
        FUN_004f74f8(0,100,DAT_004f946c);
      }
    }
    else {
      local_30 = 0x147;
      local_2c = local_2c & 0xffffff00;
      ui_common_api_fn_00509ca2(*DAT_004f9358,&local_30,5);
    }
  }
  return 0;
}

