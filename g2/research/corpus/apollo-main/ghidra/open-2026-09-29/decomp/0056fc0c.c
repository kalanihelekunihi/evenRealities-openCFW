
undefined4 pt_cmd_01_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined1 *puVar5;
  undefined1 *puVar6;
  
  puVar5 = param_3;
  puVar6 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00570760,DAT_0057075c,DAT_00570758,0x3cf,DAT_00570754,puVar5,puVar6);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_0056fc5c;
  }
  compress_log_output(0xc000000,DAT_00570764,DAT_00570764);
LAB_0056fc5c:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     (param_2 < 5)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00570760,DAT_0057075c,DAT_00570758,0x3d2,DAT_0057076c,DAT_00570758);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00570770,DAT_00570770,DAT_00570758);
    }
    uVar3 = 0xffffffff;
  }
  else {
    *param_3 = 1;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    bVar1 = *(byte *)(param_1 + 4);
    if ((bVar1 == 0) || (bVar1 == 1)) {
      uVar4 = productModeRead();
      if (bVar1 == uVar4) {
        param_3[4] = 4;
      }
      else {
        param_3[4] = 0;
        productModeUpdate(bVar1);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_00570760,DAT_0057075c,DAT_00570758,0x3df,DAT_00570774,DAT_00570758,0x3df)
        ;
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8800000,DAT_00570778,DAT_00570778,DAT_00570758,0x3df);
      }
      param_3[4] = 3;
    }
    *param_4 = 5;
    uVar3 = 0;
  }
  return uVar3;
}

