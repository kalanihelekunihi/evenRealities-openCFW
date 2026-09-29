
undefined8 FUN_004bd054(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  local_10 = param_3;
  local_c = param_4;
  if (param_1 != '\0') {
    if (param_1 == '\x01') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bda30;
        local_10 = 0x3b;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bda44,DAT_004bda44);
      }
    }
    else if (param_1 == '\x03') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bda48;
        local_10 = 0x3f;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bda58);
      }
    }
    else if (param_1 == '\x04') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bda5c;
        local_10 = 0x43;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bda60,DAT_004bda60);
      }
    }
    else if (param_1 == '\x05') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bda64;
        local_10 = 0x47;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bda68,DAT_004bda68);
      }
    }
    else if (param_1 == '\x06') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bda6c;
        local_10 = 0x4b;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bda70,DAT_004bda70);
      }
    }
    else if (param_1 == '\a') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bda74;
        local_10 = 0x4f;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bda78,DAT_004bda78);
      }
    }
    else if (param_1 == '\b') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bda7c;
        local_10 = 0x53;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bda80,DAT_004bda80);
      }
    }
    else if (param_1 == '\t') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bda84;
        local_10 = 0x57;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bda88,DAT_004bda88);
      }
    }
    else if (param_1 == '\n') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bda8c;
        local_10 = 0x5b;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bda90,DAT_004bda90);
      }
    }
    else if (param_1 == '\v') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bda94;
        local_10 = 0x5f;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bda98,DAT_004bda98);
      }
    }
    else if (param_1 == '\f') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bda9c;
        local_10 = 99;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdaa0,DAT_004bdaa0);
      }
    }
    else if (param_1 == '\r') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdaa4;
        local_10 = 0x67;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdaa8,DAT_004bdaa8);
      }
    }
    else if (param_1 == '\x0e') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdaac;
        local_10 = 0x6b;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdab0,DAT_004bdab0);
      }
    }
    else if (param_1 == '\x12') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdab4;
        local_10 = 0x6f;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdab8,DAT_004bdab8);
      }
    }
    else if (param_1 == '\x13') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdabc;
        local_10 = 0x73;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdac0,DAT_004bdac0);
      }
    }
    else if (param_1 == '\x14') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdac4;
        local_10 = 0x77;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdac8,DAT_004bdac8);
      }
    }
    else if (param_1 == '\x15') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdacc;
        local_10 = 0x7b;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdad0,DAT_004bdad0);
      }
    }
    else if (param_1 == '\x16') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdad4;
        local_10 = 0x7f;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdad8,DAT_004bdad8);
      }
    }
    else if (param_1 == '\x17') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdadc;
        local_10 = 0x83;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdae0,DAT_004bdae0);
      }
    }
    else if (param_1 == '\x18') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdae4;
        local_10 = 0x87;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdae8,DAT_004bdae8);
      }
    }
    else if (param_1 == '\x19') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdaec;
        local_10 = 0x8b;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdaf0,DAT_004bdaf0);
      }
    }
    else if (param_1 == '\x1a') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdaf4;
        local_10 = 0x8f;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdaf8,DAT_004bdaf8);
      }
    }
    else if (param_1 == '\x1b') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdafc;
        local_10 = 0x93;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdb00,DAT_004bdb00);
      }
    }
    else if (param_1 == '\x1c') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdb04;
        local_10 = 0x97;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdb08,DAT_004bdb08);
      }
    }
    else if (param_1 == '\x1d') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdb0c;
        local_10 = 0x9b;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdb10,DAT_004bdb10);
      }
    }
    else if (param_1 == '\x1e') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004bdb14;
        local_10 = 0x9f;
        FUN_0043d574(4,DAT_004bda54,DAT_004bda50,DAT_004bda4c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bdb18,DAT_004bdb18);
      }
    }
  }
  if (*(int *)(DAT_004bdb1c + 4) != 0) {
    (**(code **)(DAT_004bdb1c + 4))(param_1,0);
  }
  return CONCAT44(local_c,local_10);
}

