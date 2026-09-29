
undefined8 FUN_005b2652(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_005b2d38;
  if (*(char *)(DAT_005b2d38 + 0x98) == '\0') {
    if (*(char *)(DAT_005b2d38 + 0x96) == '\0') {
      if (param_1 == 0x48) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0x8c;
          param_3 = DAT_005b30b8;
          FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b30b0);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_005b30bc);
        }
        system_close_page_factory_0046ae9c(1,0xb);
      }
      else if (*(int *)(DAT_005b2d38 + 0x7c) == 0) {
        if (*(char *)(DAT_005b2d38 + 0x8c) == '\0') {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            param_2 = 0x93;
            param_3 = DAT_005b32a4;
            FUN_0043d574(2,DAT_005b2d30,DAT_005b2d2c,DAT_005b30b0);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_005b32a8,DAT_005b32a8);
          }
        }
        else {
          iVar1 = FUN_0044ddea(*(undefined4 *)(DAT_005b2d38 + 100));
          if (iVar1 == 0) {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              param_2 = 0x95;
              param_3 = DAT_005b32ac;
              FUN_0043d574(2,DAT_005b2d30,DAT_005b2d2c,DAT_005b30b0);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_005b32b0,DAT_005b32b0);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              param_2 = 0x97;
              param_3 = DAT_005b3338;
              FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b30b0);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_005b333c,DAT_005b333c);
            }
            FUN_005b02e4(0xc,0);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0x90;
          param_3 = DAT_005b30c0;
          FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b30b0);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_005b30c4,DAT_005b30c4);
        }
        FUN_005b02e4(0xc,0);
      }
    }
    else {
      FUN_005b3c70();
      if (param_1 == 10) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_2 = 0xa2;
          param_3 = DAT_005b3384;
          FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b30b0,0xa2,DAT_005b3384,
                       *(undefined4 *)(iVar1 + 0x84));
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_005b3388,DAT_005b3388,*(undefined4 *)(iVar1 + 0x84));
        }
        if (*(int *)(iVar1 + 0x84) == -1) {
          FUN_005b02e4(6,0);
        }
        else {
          FUN_005b02e4(8,0);
        }
      }
      else if (param_1 == 0x48) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0xa9;
          param_3 = DAT_005b338c;
          FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b30b0);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_005b3390,DAT_005b3390);
        }
        FUN_005b02e4(0xd,0);
      }
      else if (param_1 == 0x44) {
        iVar1 = FUN_005b23e4();
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_2 = 0xad;
          param_3 = DAT_005b3394;
          FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b30b0,0xad,DAT_005b3394,iVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_005b349c,DAT_005b349c,iVar1);
        }
        if (iVar1 != 0) {
          FUN_005b02e4(0xe,iVar1);
        }
      }
      else if (param_1 == 0x45) {
        iVar1 = FUN_005b24e8();
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_2 = 0xb3;
          param_3 = DAT_005b34cc;
          FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b30b0,0xb3,DAT_005b34cc,iVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__conversate_ui_main_input_select_005b34d0,
                              PTR_s__conversate_ui_main_input_select_005b34d0,iVar1);
        }
        if (iVar1 != 0) {
          FUN_005b02e4(0xf,iVar1);
        }
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x85;
      param_3 = DAT_005b30ac;
      param_4 = param_1;
      FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b30b0,0x85,DAT_005b30ac,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_005b30b4,DAT_005b30b4,param_1,param_2,param_3,param_4);
    }
  }
  return CONCAT44(param_3,param_2);
}

