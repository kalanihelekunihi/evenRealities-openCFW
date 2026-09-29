
undefined4 FUN_004e814c(int param_1,int param_2)

{
  undefined4 *puVar1;
  undefined1 local_38;
  undefined1 local_37;
  undefined1 local_36;
  undefined1 local_35;
  undefined1 local_34;
  undefined1 local_33;
  undefined1 local_30;
  undefined1 local_2f;
  undefined1 local_2e;
  undefined1 local_2d;
  undefined1 local_2c;
  undefined1 local_2b;
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
  
  if (*DAT_004e8bb8 == 0) {
    if (*DAT_004e83bc == 0) {
      if (param_1 == 0x44) {
        puVar1 = *(undefined4 **)(param_2 + 0x10);
        local_10 = 0;
        local_f = 0x44;
        local_e = (undefined1)*puVar1;
        local_d = (undefined1)((uint)*puVar1 >> 8);
        local_c = (undefined1)puVar1[1];
        local_b = (undefined1)((uint)puVar1[1] >> 8);
        FUN_00464bb2(1,&local_10,6,0);
      }
      else if (param_1 == 0x45) {
        puVar1 = *(undefined4 **)(param_2 + 0x10);
        local_18 = 0;
        local_17 = 0x45;
        local_16 = (undefined1)*puVar1;
        local_15 = (undefined1)((uint)*puVar1 >> 8);
        local_14 = (undefined1)puVar1[1];
        local_13 = (undefined1)((uint)puVar1[1] >> 8);
        FUN_00464bb2(1,&local_18,6,0);
      }
      else if (param_1 == 0x4a) {
        local_20 = 0;
        local_1f = 0x4a;
        local_1e = 0;
        local_1d = 0;
        local_1c = 0;
        local_1b = 0;
        FUN_00464bb2(1,&local_20,6,0);
      }
      else if (param_1 == 10) {
        local_28 = 0;
        local_27 = 10;
        local_26 = 0;
        local_25 = 0;
        local_24 = 0;
        local_23 = 0;
        FUN_00464bb2(1,&local_28,6,0);
      }
      else if (param_1 == 0x48) {
        local_30 = 0;
        local_2f = 0x48;
        local_2e = 0;
        local_2d = 0;
        local_2c = 0;
        local_2b = 0;
        FUN_00464bb2(1,&local_30,6,0);
      }
      else if (param_1 == 0x49) {
        local_38 = 0;
        local_37 = 0x49;
        local_36 = 0;
        local_35 = 0;
        local_34 = 0;
        local_33 = 0;
        FUN_00464bb2(1,&local_38,6,0);
      }
    }
  }
  else if (*DAT_004e83bc == 0) {
    FUN_004e80e8();
  }
  return 0;
}

