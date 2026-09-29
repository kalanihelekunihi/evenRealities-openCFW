
undefined4 pt_cmd_48_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  byte bVar1;
  undefined1 *puVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 uVar5;
  
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575ac8,0xb65,DAT_00575ac4);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00575acc,DAT_00575acc);
  }
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     (param_2 < 5)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00575414,DAT_00575410,DAT_00575ac8,0xb68,DAT_00575418,DAT_00575ac8);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0057541c,DAT_0057541c,DAT_00575ac8);
    }
    uVar4 = 0xffffffff;
  }
  else {
    *param_3 = 0x48;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 4;
    puVar2 = DAT_00575ad8;
    uVar5 = 4;
    bVar1 = *(byte *)(param_1 + 4);
    if (bVar1 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575ac8,0xb78,DAT_00575ad0,*DAT_00575ac0,
                     DAT_00575ac0[1],DAT_00575ac0[2],DAT_00575ac0[3]);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xd000000,DAT_00575ad4,DAT_00575ad4,*DAT_00575ac0,DAT_00575ac0[1],
                            DAT_00575ac0[2],DAT_00575ac0[3]);
      }
      puVar2 = DAT_00575ac0;
      param_3[4] = *DAT_00575ac0;
      param_3[5] = puVar2[1];
      param_3[6] = puVar2[2];
      param_3[7] = puVar2[3];
      uVar5 = 8;
    }
    else if (bVar1 == 2) {
      uVar4 = FUN_0052dee6();
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575ac8,0xb8d,DAT_00575ae4,uVar4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00575e74,DAT_00575e74,uVar4);
      }
      param_3[4] = (char)uVar4;
      param_3[5] = (char)((uint)uVar4 >> 8);
      param_3[6] = (char)((uint)uVar4 >> 0x10);
      param_3[7] = (char)((uint)uVar4 >> 0x18);
      uVar5 = 8;
    }
    else if (bVar1 < 2) {
      param_3[4] = *DAT_00575ad8;
      param_3[5] = puVar2[1];
      param_3[6] = puVar2[2];
      param_3[7] = puVar2[3];
      uVar5 = 8;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575ac8,0xb86,DAT_00575adc,*puVar2,puVar2[1],
                     puVar2[2],puVar2[3]);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xd000000,DAT_00575ae0,DAT_00575ae0,*puVar2,puVar2[1],puVar2[2],
                            puVar2[3]);
      }
    }
    else {
      *param_3 = 0x48;
      param_3[1] = 1;
      param_3[2] = 3;
      param_3[3] = 1;
      param_3[4] = 3;
    }
    *param_4 = uVar5;
    uVar4 = 0;
  }
  return uVar4;
}

