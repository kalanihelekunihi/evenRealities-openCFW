
undefined8 pt_cmd_67_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined1 *puVar4;
  
  uVar3 = param_2;
  puVar4 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar3 = 0xdea;
    FUN_0043d574(3,DAT_00577358,DAT_00577354,DAT_00577b80,0xdea,DAT_005779d8,puVar4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_0057701e;
  }
  compress_log_output(0xc000000,DAT_005779dc,DAT_005779dc);
LAB_0057701e:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 4)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0xded;
      FUN_0043d574(1,DAT_00577358,DAT_00577354,DAT_00577b80,0xded,DAT_00577360,DAT_00577b80);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00577470,DAT_00577470,DAT_00577b80);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0x66;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    param_3[4] = 0;
    *param_4 = 5;
    uVar2 = 0;
  }
  return CONCAT44(uVar3,uVar2);
}

