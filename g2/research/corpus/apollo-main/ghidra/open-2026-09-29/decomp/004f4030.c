
int FUN_004f4030(int param_1,int param_2)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 local_28;
  undefined4 local_24;
  undefined1 local_20;
  undefined1 local_1f;
  undefined1 local_1e;
  undefined1 local_1d;
  undefined1 local_1c;
  undefined1 local_1b;
  undefined1 local_18;
  undefined1 local_17;
  undefined1 local_16;
  undefined1 local_15;
  undefined1 local_14;
  undefined1 local_13;
  undefined1 local_10;
  undefined1 local_f;
  undefined1 local_e;
  undefined1 local_d;
  undefined1 local_c;
  undefined1 local_b;
  
  if (param_1 == 10) {
    if (*DAT_004f4638 == 1) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004f463c;
        local_28 = 0x7d5;
        FUN_0043d574(4,DAT_004f4648,DAT_004f4644,DAT_004f4640);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004f464c);
      }
      param_1 = 0;
    }
    else if (((*DAT_004f4650 == 0) && (*DAT_004f4654 == 1)) && (*DAT_004f4608 == 1)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004f4658;
        local_28 = 0x7da;
        FUN_0043d574(3,DAT_004f4648,DAT_004f4644,DAT_004f4640);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004f465c,DAT_004f465c);
      }
      param_1 = 0;
    }
    else if (((*DAT_004f4660 == 1) || (*DAT_004f4664 == 1)) &&
            ((*DAT_004f4650 == 1 && (*DAT_004f4654 == 1)))) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004f4668;
        local_28 = 0x7df;
        FUN_0043d574(4,DAT_004f4648,DAT_004f4644,DAT_004f4640);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004f466c,DAT_004f466c);
      }
      param_1 = 0;
    }
    else {
      local_10 = 0;
      local_f = 10;
      local_e = 0;
      local_d = 0;
      local_c = 0;
      local_b = 0;
      param_1 = FUN_00464bb2(1,&local_10,6,0);
    }
  }
  else if (param_1 == 0x48) {
    if (*DAT_004f4638 == 1) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004f463c;
        local_28 = 0x7ee;
        FUN_0043d574(4,DAT_004f4648,DAT_004f4644,DAT_004f4640);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004f464c,DAT_004f464c);
      }
      param_1 = 0;
    }
    else if (((*DAT_004f4650 == 0) && (*DAT_004f4654 == 1)) && (*DAT_004f4608 == 1)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004f4658;
        local_28 = 0x7f3;
        FUN_0043d574(3,DAT_004f4648,DAT_004f4644,DAT_004f4640);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004f465c,DAT_004f465c);
      }
      param_1 = 0;
    }
    else if (((*DAT_004f4660 == 1) || (*DAT_004f4664 == 1)) &&
            ((*DAT_004f4650 == 1 && (*DAT_004f4654 == 1)))) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004f4668;
        local_28 = 0x7f8;
        FUN_0043d574(4,DAT_004f4648,DAT_004f4644,DAT_004f4640);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004f466c,DAT_004f466c);
      }
      param_1 = 0;
    }
    else {
      local_18 = 0;
      local_17 = 0x48;
      local_16 = 0;
      local_15 = 0;
      local_14 = 0;
      local_13 = 0;
      param_1 = FUN_00464bb2(1,&local_18,6,0);
    }
  }
  else if (param_1 == 0x49) {
    param_1 = 0;
  }
  else if (param_1 == 0x45) {
    if (((*DAT_004f4650 == 0) && (*DAT_004f4654 == 1)) && (*DAT_004f4608 == 1)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004f4658;
        local_28 = 0x809;
        FUN_0043d574(3,DAT_004f4648,DAT_004f4644,DAT_004f4640);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004f465c,DAT_004f465c);
      }
      param_1 = 0;
    }
    else if (((*DAT_004f4ebc == 1) && (*DAT_004f4650 == 0)) && (*DAT_004f4654 == 1)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004f4ec0;
        local_28 = 0x80d;
        FUN_0043d574(4,DAT_004f4648,DAT_004f4644,DAT_004f4640);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004f4ec4,DAT_004f4ec4);
      }
      param_1 = 0;
    }
    else if (*DAT_004f4638 == 1) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004f4ec8;
        local_28 = 0x812;
        FUN_0043d574(4,DAT_004f4648,DAT_004f4644,DAT_004f4640);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004f4ecc,DAT_004f4ecc);
      }
      param_1 = 0;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004f4ed0;
        local_28 = 0x815;
        FUN_0043d574(3,DAT_004f4648,DAT_004f4644,DAT_004f4640);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004f4ed4,DAT_004f4ed4);
      }
      puVar2 = *(undefined4 **)(param_2 + 0x10);
      local_20 = 0;
      local_1f = 0x45;
      local_1e = (undefined1)*puVar2;
      local_1d = (undefined1)((uint)*puVar2 >> 8);
      local_1c = (undefined1)puVar2[1];
      local_1b = (undefined1)((uint)puVar2[1] >> 8);
      param_1 = FUN_00464bb2(1,&local_20,6,0);
    }
  }
  else if (param_1 == 0x44) {
    if (((*DAT_004f4650 == 0) && (*DAT_004f4654 == 1)) && (*DAT_004f4608 == 1)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004f4658;
        local_28 = 0x822;
        FUN_0043d574(3,DAT_004f4648,DAT_004f4644,DAT_004f4640);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004f465c,DAT_004f465c);
      }
      param_1 = 0;
    }
    else if (((*DAT_004f4ebc == 1) && (*DAT_004f4650 == 0)) && (*DAT_004f4654 == 1)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004f4ec0;
        local_28 = 0x826;
        FUN_0043d574(4,DAT_004f4648,DAT_004f4644,DAT_004f4640);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004f4ec4,DAT_004f4ec4);
      }
      param_1 = 0;
    }
    else if (*DAT_004f4638 == 1) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004f4ec8;
        local_28 = 0x82b;
        FUN_0043d574(4,DAT_004f4648,DAT_004f4644,DAT_004f4640);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004f4ecc,DAT_004f4ecc);
      }
      param_1 = 0;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_24 = DAT_004f4f5c;
        local_28 = 0x82e;
        FUN_0043d574(3,DAT_004f4648,DAT_004f4644,DAT_004f4640);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004f4f60,DAT_004f4f60);
      }
      puVar2 = *(undefined4 **)(param_2 + 0x10);
      local_28 = CONCAT13((char)((uint)*puVar2 >> 8),CONCAT12((char)*puVar2,0x4400));
      local_24._0_2_ = CONCAT11((char)((uint)puVar2[1] >> 8),(char)puVar2[1]);
      param_1 = FUN_00464bb2(1,&local_28,6,0);
    }
  }
  return param_1;
}

