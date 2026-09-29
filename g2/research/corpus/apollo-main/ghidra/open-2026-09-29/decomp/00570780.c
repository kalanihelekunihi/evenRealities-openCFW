
undefined8 pt_cmd_13_handler(int param_1,uint param_2,undefined1 *param_3,byte *param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  byte bVar4;
  uint uVar5;
  byte *pbVar6;
  
  uVar5 = param_2;
  pbVar6 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar5 = 0x4d7;
    FUN_0043d574(3,DAT_00571054,DAT_00571050,DAT_0057104c,0x4d7,DAT_00571048,pbVar6);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_005707c0:
    compress_log_output(0xc000000,DAT_00571058,DAT_00571058);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_005707c0;
  }
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (byte *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 4)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar5 = 0x4da;
      FUN_0043d574(1,DAT_00571054,DAT_00571050,DAT_0057104c,0x4da,DAT_0057105c,DAT_0057104c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00571060,DAT_00571060,DAT_0057104c);
    }
    uVar2 = 0xffffffff;
    goto LAB_005709ae;
  }
  *param_3 = 0x17;
  param_3[1] = 1;
  param_3[2] = 3;
  param_3[3] = 0x24;
  bVar4 = 4;
  iVar1 = semantic_get_latest_complete_sample();
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar5 = 0x4ea;
      FUN_0043d574(1,DAT_00571054,DAT_00571050,DAT_0057104c,0x4ea,DAT_00571334);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00571338,DAT_00571338);
    }
    *param_4 = 4;
    uVar2 = 0xffffffff;
    goto LAB_005709ae;
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    uVar5 = 0x4ef;
    FUN_0043d574(4,DAT_00571054,DAT_00571050,DAT_0057104c,0x4ef,DAT_0057133c,4);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00571340,DAT_00571340,4);
  }
  for (iVar3 = 0; iVar3 < 0x24; iVar3 = iVar3 + 1) {
    param_3[bVar4] = *(undefined1 *)(iVar1 + iVar3);
    bVar4 = bVar4 + 1;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar5 = 0x4f6;
    FUN_0043d574(4,DAT_00571054,DAT_00571050,DAT_0057104c,0x4f6,DAT_00571344,bVar4);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_0057094e:
    compress_log_output(0x10400000,DAT_00571348,DAT_00571348,bVar4);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_0057094e;
  }
  *param_4 = bVar4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar5 = 0x4f9;
    FUN_0043d574(4,DAT_00571054,DAT_00571050,DAT_0057104c,0x4f9,DAT_0057134c,*param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00571350,DAT_00571350,*param_4);
  }
  uVar2 = 0;
LAB_005709ae:
  return CONCAT44(uVar5,uVar2);
}

