
uint * FUN_004e84b0(byte *param_1,uint param_2)

{
  byte bVar1;
  int iVar2;
  uint *puVar3;
  
  if ((param_2 == 0) || (param_1 == (byte *)0x0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004e8a7c,DAT_004e8a78,DAT_004e8dbc,0x455,DAT_004e8db8,param_2,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_004e8dc0,DAT_004e8dc0,param_2,param_1);
    }
    puVar3 = (uint *)0x0;
  }
  else if (*param_1 == 0) {
    puVar3 = DAT_004e8bc8;
    if (*DAT_004e8bc8 < 5) {
      puVar3 = (uint *)(uint)*(byte *)(DAT_004e8bc4 + *DAT_004e8bc8);
      if (puVar3 == (uint *)0x0) {
        puVar3 = (uint *)FUN_004f3440(param_1,param_2);
      }
      else if (puVar3 == (uint *)0x2) {
        puVar3 = (uint *)FUN_004eebdc(param_1,param_2);
      }
      else if (puVar3 < (uint *)0x2) {
        puVar3 = (uint *)FUN_004eb4a4(param_1,param_2);
      }
      else if (puVar3 == (uint *)&Reset) {
        puVar3 = (uint *)FUN_004f8ffc(param_1,param_2);
      }
      else if (puVar3 < &Reset) {
        puVar3 = (uint *)FUN_004fc360(param_1,param_2);
      }
    }
  }
  else {
    puVar3 = (uint *)(uint)*param_1;
    if (puVar3 == (uint *)0x1) {
      puVar3 = (uint *)FUN_004e8970(param_1 + 1,param_2 - 1);
    }
    else if (puVar3 == (uint *)0x2) {
      puVar3 = (uint *)FUN_004ed9b6(param_1 + 1,param_2 - 1);
    }
    else if (puVar3 != (uint *)0x3) {
      if (puVar3 == (uint *)&Reset) {
        puVar3 = (uint *)FUN_004ebf5c(param_1 + 1,param_2 - 1);
      }
      else if (puVar3 == (uint *)0x5) {
        puVar3 = (uint *)FUN_004f8644(param_1 + 1,param_2 - 1);
      }
      else if (puVar3 == (uint *)0x6) {
        FUN_004fb5e8(param_1 + 1,param_2 - 1);
        puVar3 = (uint *)dashboard_watchface_manager_call_30();
      }
      else if (puVar3 == (uint *)0x7) {
        if (param_2 < 4) {
          bVar1 = param_1[1];
        }
        else {
          bVar1 = param_1[3];
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e8a7c,DAT_004e8a78,DAT_004e8dbc,0x4c0,DAT_004e9350,param_1[1],
                       param_1[2],bVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xcc00000,DAT_004e9354,DAT_004e9354,param_1[1],param_1[2],bVar1);
        }
        puVar3 = (uint *)dashboard_watchface_manager_call_0c(param_1[1],param_1[2],bVar1);
      }
      else if (puVar3 == (uint *)&NMI) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e8a7c,DAT_004e8a78,DAT_004e8dbc,0x4ab,DAT_004e9230);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004e9234,DAT_004e9234);
        }
        puVar3 = (uint *)FUN_004e8a90();
      }
      else if (puVar3 == (uint *)0x9) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004e8a7c,DAT_004e8a78,DAT_004e8dbc,0x4b0,DAT_004e9238);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004e9270,DAT_004e9270);
        }
        bVar1 = param_1[1];
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e8a7c,DAT_004e8a78,DAT_004e8dbc,0x4b2,DAT_004e9274,bVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_004e9278,DAT_004e9278,bVar1);
        }
        puVar3 = (uint *)dashboard_watchface_manager_call_20(bVar1);
      }
      else if (puVar3 == (uint *)0xa) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004e8a7c,DAT_004e8a78,DAT_004e8dbc,0x4b7,DAT_004e927c);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004e92e8,DAT_004e92e8);
        }
        bVar1 = param_1[1];
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e8a7c,DAT_004e8a78,DAT_004e8dbc,0x4b9,DAT_004e92ec,bVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_004e92f0,DAT_004e92f0,bVar1);
        }
        puVar3 = (uint *)FUN_004efcb8(bVar1);
      }
      else if (puVar3 == (uint *)&HardFault) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e8a7c,DAT_004e8a78,DAT_004e8dbc,0x472,DAT_004e8dc4);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004e8dc8,DAT_004e8dc8);
        }
        puVar3 = (uint *)FUN_004f3084();
      }
      else if (puVar3 == (uint *)0xd) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e8a7c,DAT_004e8a78,DAT_004e8dbc,0x477,DAT_004e8dcc);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004e8dd0,DAT_004e8dd0);
        }
        puVar3 = (uint *)FUN_004f3128();
      }
      else if (puVar3 == (uint *)0xe) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e8a7c,DAT_004e8a78,DAT_004e8dbc,0x47c,DAT_004e8dd4);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004e8dd8,DAT_004e8dd8);
        }
        puVar3 = (uint *)FUN_004f2ec0();
      }
      else if (puVar3 == (uint *)0xf) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e8a7c,DAT_004e8a78,DAT_004e8dbc,0x481,DAT_004e8ddc);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004e8de0,DAT_004e8de0);
        }
        puVar3 = (uint *)FUN_004f31c8();
      }
      else if (puVar3 == (uint *)0x12) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e8a7c,DAT_004e8a78,DAT_004e8dbc,0x486,DAT_004e8de4);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004e8de8,DAT_004e8de8);
        }
        puVar3 = (uint *)FUN_004f326c();
      }
    }
  }
  return puVar3;
}

