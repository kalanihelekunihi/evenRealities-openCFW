
undefined4 pt_cmd_64_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 *puVar4;
  undefined1 *puVar5;
  
  puVar4 = param_3;
  puVar5 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00577358,DAT_00577354,DAT_00577670,0xd9c,DAT_0057766c,puVar4,puVar5);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_00576c24;
  }
  compress_log_output(0xc000000,DAT_00577674,DAT_00577674);
LAB_00576c24:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     (param_2 < 9)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00577358,DAT_00577354,DAT_00577670,0xd9f,DAT_00577360,DAT_00577670);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00577470,DAT_00577470,DAT_00577670);
    }
    uVar3 = 0xffffffff;
  }
  else {
    *param_3 = 99;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    uVar3 = *(undefined4 *)(param_1 + 4);
    uVar1 = *(undefined1 *)(param_1 + 8);
    nvdbBuzzerUpdate(uVar3,uVar1);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00577358,DAT_00577354,DAT_00577670,0xdac,DAT_00577784,uVar3,uVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_005779c8,DAT_005779c8,uVar3,uVar1);
    }
    param_3[4] = 0;
    *param_4 = 5;
    uVar3 = 0;
  }
  return uVar3;
}

