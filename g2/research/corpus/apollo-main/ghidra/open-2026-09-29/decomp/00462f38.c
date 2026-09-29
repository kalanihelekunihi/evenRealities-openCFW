
int FUN_00462f38(int param_1)

{
  undefined1 local_28;
  undefined1 local_27;
  undefined1 local_26;
  undefined1 local_25;
  undefined1 local_24;
  undefined1 local_23;
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
  
  if (*DAT_00463b94 == '\0') {
    if (param_1 == 0x44) {
      local_10 = 0;
      local_f = 0x44;
      local_e = 1;
      local_d = 0;
      local_c = 0;
      local_b = 0;
      param_1 = FUN_00464bb2(3,&local_10,6,0);
    }
    else if (param_1 == 0x45) {
      local_18 = 0;
      local_17 = 0x45;
      local_16 = 0xff;
      local_15 = 0;
      local_14 = 0;
      local_13 = 0;
      param_1 = FUN_00464bb2(3,&local_18,6,0);
    }
    else if (param_1 == 10) {
      local_20 = 0;
      local_1f = 10;
      local_1e = 0;
      local_1d = 0;
      local_1c = 0;
      local_1b = 0;
      FUN_00464bb2(3,&local_20,6,0);
      param_1 = 1;
    }
    else if (param_1 == 0x48) {
      local_28 = 0;
      local_27 = 0x48;
      local_26 = 0;
      local_25 = 0;
      local_24 = 0;
      local_23 = 0;
      FUN_00464bb2(3,&local_28,6,0);
      param_1 = 1;
    }
  }
  else {
    param_1 = 0;
  }
  return param_1;
}

