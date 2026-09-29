
undefined8
ti_opt3007_assignRegistermap
          (undefined1 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  iVar1 = FUN_0043d0ce();
  local_10 = param_3;
  local_c = param_4;
  if (iVar1 << 0x1e < 0) {
    local_c = DAT_00513734;
    local_10 = 0x45;
    FUN_0043d574(4,DAT_00513740,DAT_0051373c,DAT_00513738);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00513744,DAT_00513744);
  }
  param_1[5] = 0;
  param_1[3] = 0xf;
  param_1[4] = 0xc;
  param_1[2] = 0;
  *param_1 = 0xb;
  param_1[1] = 0;
  param_1[8] = 1;
  param_1[6] = 0xf;
  param_1[7] = 0xc;
  param_1[0xb] = 1;
  param_1[9] = 0xb;
  param_1[10] = 0xb;
  param_1[0xe] = 1;
  param_1[0xc] = 10;
  param_1[0xd] = 9;
  param_1[0x11] = 1;
  param_1[0xf] = 8;
  param_1[0x10] = 8;
  param_1[0x14] = 1;
  param_1[0x12] = 7;
  param_1[0x13] = 7;
  param_1[0x17] = 1;
  param_1[0x15] = 6;
  param_1[0x16] = 6;
  param_1[0x1a] = 1;
  param_1[0x18] = 5;
  param_1[0x19] = 5;
  param_1[0x1d] = 1;
  param_1[0x1b] = 4;
  param_1[0x1c] = 4;
  param_1[0x20] = 1;
  param_1[0x1e] = 3;
  param_1[0x1f] = 3;
  param_1[0x23] = 1;
  param_1[0x21] = 2;
  param_1[0x22] = 2;
  param_1[0x26] = 1;
  param_1[0x24] = 1;
  param_1[0x25] = 0;
  param_1[0x29] = 2;
  param_1[0x27] = 0xf;
  param_1[0x28] = 0xc;
  param_1[0x2c] = 2;
  param_1[0x2a] = 0xb;
  param_1[0x2b] = 0;
  param_1[0x2f] = 3;
  param_1[0x2d] = 0xf;
  param_1[0x2e] = 0xc;
  param_1[0x32] = 3;
  param_1[0x30] = 0xb;
  param_1[0x31] = 0;
  param_1[0x35] = 0x7e;
  param_1[0x33] = 0xf;
  param_1[0x34] = 0;
  param_1[0x38] = 0x7f;
  param_1[0x36] = 0xf;
  param_1[0x37] = 0;
  return CONCAT44(local_c,local_10);
}

