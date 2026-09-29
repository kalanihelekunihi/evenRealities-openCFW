
undefined4 pt_cmd_1C_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 *puVar4;
  undefined1 local_44 [4];
  undefined1 local_40 [4];
  undefined1 local_3c [4];
  undefined1 local_38 [4];
  undefined1 auStack_34 [20];
  undefined4 local_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00570760,DAT_0057075c,DAT_0057102c,0x49d,DAT_00571028);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_005705bc;
  }
  compress_log_output(0xc000000,DAT_00571030,DAT_00571030);
LAB_005705bc:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     (param_2 < 4)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00570760,DAT_0057075c,DAT_0057102c,0x4a0,DAT_0057076c,DAT_0057102c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00570770,DAT_00570770,DAT_0057102c);
    }
    uVar3 = 0xffffffff;
  }
  else {
    *param_3 = 0x24;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 5;
    local_20 = *DAT_00571034;
    uStack_1c = DAT_00571034[1];
    uStack_18 = DAT_00571034[2];
    iVar2 = productModeGet();
    if (iVar2 == 1) {
      FUN_004b4728(auStack_34,&DAT_00570768,&local_20);
    }
    else {
      FUN_0048d540(auStack_34,&local_20);
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00570760,DAT_0057075c,DAT_0057102c,0x4c4,DAT_00571038,auStack_34);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_0057103c,DAT_0057103c,auStack_34);
    }
    FUN_00475fc0(auStack_34,DAT_00571040,local_38,local_3c,local_40,local_44);
    param_3[4] = local_38[0];
    param_3[5] = local_3c[0];
    param_3[6] = local_40[0];
    param_3[7] = local_44[0];
    puVar4 = (undefined1 *)FUN_0050938e(1);
    uVar1 = *puVar4;
    param_3[8] = uVar1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00570760,DAT_0057075c,DAT_0057102c,0x4cf,DAT_00571044,uVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_00571330,DAT_00571330,uVar1);
    }
    *param_4 = 9;
    uVar3 = 0;
  }
  return uVar3;
}

