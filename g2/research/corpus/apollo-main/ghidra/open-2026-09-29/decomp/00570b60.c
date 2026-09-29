
undefined8 pt_cmd_2E_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined1 *puVar4;
  
  uVar3 = param_2;
  puVar4 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar3 = 0x520;
    FUN_0043d574(3,DAT_00571054,DAT_00571050,DAT_0057136c,0x520,DAT_00571368,puVar4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00570bae;
  }
  compress_log_output(0xc000000,DAT_00571370,DAT_00571370);
LAB_00570bae:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 6)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0x523;
      FUN_0043d574(1,DAT_00571054,DAT_00571050,DAT_0057136c,0x523,DAT_0057105c,DAT_0057136c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00571060,DAT_00571060,DAT_0057136c);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0x3a;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    iVar1 = productModeGet();
    if (iVar1 == 1) {
      if (*(char *)(param_1 + 5) == '\0') {
        *DAT_00571374 = 0;
      }
      else {
        *DAT_00571374 = 1;
      }
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0x532;
        FUN_0043d574(3,DAT_00571054,DAT_00571050,DAT_0057136c,0x532,DAT_00571378,*DAT_00571374);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_0057137c,DAT_0057137c,*DAT_00571374);
      }
      param_3[4] = 0;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0x537;
        FUN_0043d574(1,DAT_00571054,DAT_00571050,DAT_0057136c,0x537,DAT_00571380);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00571384,DAT_00571384);
      }
      param_3[4] = 5;
    }
    param_3[5] = *(undefined1 *)(param_1 + 4);
    *param_4 = 6;
    uVar2 = 0;
  }
  return CONCAT44(uVar3,uVar2);
}

