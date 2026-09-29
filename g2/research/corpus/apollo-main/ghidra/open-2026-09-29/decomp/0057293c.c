
undefined8 pt_cmd_05_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined1 *puVar4;
  
  uVar3 = param_2;
  puVar4 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar3 = 0x7de;
    FUN_0043d574(3,DAT_00572ae8,DAT_00572ae4,DAT_00573308,0x7de,DAT_00573304,puVar4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00572986;
  }
  compress_log_output(0xc000000,DAT_0057330c,DAT_0057330c);
LAB_00572986:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 4)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0x7e1;
      FUN_0043d574(1,DAT_00572ae8,DAT_00572ae4,DAT_00573308,0x7e1,DAT_00573200,DAT_00573308);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00573300,DAT_00573300,DAT_00573308);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 5;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 6;
    FUN_00439be4(param_3 + 4,*(int *)(DAT_005735e4 + 0xc) + 1,6);
    *param_4 = 10;
    uVar2 = 0;
  }
  return CONCAT44(uVar3,uVar2);
}

