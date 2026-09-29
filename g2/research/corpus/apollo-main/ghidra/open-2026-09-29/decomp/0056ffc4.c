
undefined4 pt_cmd_0B_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  undefined1 uVar1;
  undefined2 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 *puVar5;
  undefined1 *puVar6;
  
  puVar5 = param_3;
  puVar6 = param_4;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00570760,DAT_0057075c,DAT_00570b58,0x42c,DAT_005709c0,puVar5,puVar6);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00570b5c,DAT_00570b5c);
  }
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     (param_2 < 4)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00570760,DAT_0057075c,DAT_00570b58,0x42f,DAT_0057076c,DAT_00570b58);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00570770,DAT_00570770,DAT_00570b58);
    }
    uVar4 = 0xffffffff;
  }
  else {
    *param_3 = 0x11;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 7;
    iVar3 = DAT_005709b0;
    param_3[4] = (char)*(undefined4 *)(DAT_005709b0 + 4);
    param_3[5] = (char)(*(int *)(iVar3 + 8) / 10) + '8';
    param_3[6] = *(int *)(iVar3 + 0xc) < 1;
    uVar1 = FUN_00509694(*(undefined4 *)(iVar3 + 0xc));
    param_3[7] = uVar1;
    param_3[8] = 0 < *(int *)(iVar3 + 0x10);
    uVar2 = FUN_00509694(*(undefined4 *)(iVar3 + 0x10));
    param_3[9] = (char)((ushort)uVar2 >> 8);
    param_3[10] = (char)uVar2;
    *param_4 = 0xb;
    uVar4 = 0;
  }
  return uVar4;
}

