
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int system_close_dispatch_page_action_00469e66(int param_1,int param_2)

{
  undefined4 *puVar1;
  undefined1 uStack_38;
  undefined1 uStack_37;
  undefined1 uStack_36;
  undefined1 uStack_35;
  undefined1 uStack_34;
  undefined1 uStack_33;
  undefined1 uStack_30;
  undefined1 uStack_2f;
  undefined1 uStack_2e;
  undefined1 uStack_2d;
  undefined1 uStack_2c;
  undefined1 uStack_2b;
  undefined1 uStack_28;
  undefined1 uStack_27;
  undefined1 uStack_26;
  undefined1 uStack_25;
  undefined1 uStack_24;
  undefined1 uStack_23;
  undefined1 uStack_20;
  undefined1 uStack_1f;
  undefined1 uStack_1e;
  undefined1 uStack_1d;
  undefined1 uStack_1c;
  undefined1 uStack_1b;
  undefined1 uStack_18;
  undefined1 uStack_17;
  undefined1 uStack_16;
  undefined1 uStack_15;
  undefined1 uStack_14;
  undefined1 uStack_13;
  undefined1 uStack_10;
  undefined1 uStack_f;
  undefined1 uStack_e;
  undefined1 uStack_d;
  undefined1 uStack_c;
  undefined1 uStack_b;
  
  if (*_DAT_0046aabc == '\0') {
    if (param_1 == 0x44) {
      puVar1 = *(undefined4 **)(param_2 + 0x10);
      uStack_10 = 0;
      uStack_f = 0x44;
      uStack_e = (undefined1)*puVar1;
      uStack_d = (undefined1)((uint)*puVar1 >> 8);
      uStack_c = (undefined1)puVar1[1];
      uStack_b = (undefined1)((uint)puVar1[1] >> 8);
      param_1 = FUN_00464bb2(0x22,&uStack_10,6,0);
    }
    else if (param_1 == 0x45) {
      puVar1 = *(undefined4 **)(param_2 + 0x10);
      uStack_18 = 0;
      uStack_17 = 0x45;
      uStack_16 = (undefined1)*puVar1;
      uStack_15 = (undefined1)((uint)*puVar1 >> 8);
      uStack_14 = (undefined1)puVar1[1];
      uStack_13 = (undefined1)((uint)puVar1[1] >> 8);
      param_1 = FUN_00464bb2(0x22,&uStack_18,6,0);
    }
    else if (param_1 == 0x4a) {
      uStack_20 = 0;
      uStack_1f = 0x4a;
      uStack_1e = 0;
      uStack_1d = 0;
      uStack_1c = 0;
      uStack_1b = 0;
      param_1 = FUN_00464bb2(0x22,&uStack_20,6,0);
    }
    else if (param_1 == 10) {
      uStack_28 = 0;
      uStack_27 = 10;
      uStack_26 = 0;
      uStack_25 = 0;
      uStack_24 = 0;
      uStack_23 = 0;
      param_1 = FUN_00464bb2(0x22,&uStack_28,6,0);
    }
    else if (param_1 == 0x48) {
      uStack_30 = 0;
      uStack_2f = 0x48;
      uStack_2e = 0;
      uStack_2d = 0;
      uStack_2c = 0;
      uStack_2b = 0;
      param_1 = FUN_00464bb2(0x22,&uStack_30,6,0);
    }
    else if (param_1 == 0x49) {
      uStack_38 = 0;
      uStack_37 = 0x49;
      uStack_36 = 0;
      uStack_35 = 0;
      uStack_34 = 0;
      uStack_33 = 0;
      param_1 = FUN_00464bb2(0x22,&uStack_38,6,0);
    }
  }
  else {
    param_1 = 0;
  }
  return param_1;
}

