
undefined4 pt_cmd_47_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  byte bVar1;
  undefined1 *puVar2;
  ushort uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  undefined1 uVar7;
  uint uVar8;
  uint local_6c;
  uint local_68;
  uint local_64;
  undefined4 local_60;
  uint local_5c;
  undefined1 auStack_58 [60];
  
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575364,0xac5,DAT_00575360);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00575368,DAT_00575368);
  }
  if ((((param_3 != (undefined1 *)0x0) && (param_4 != (undefined1 *)0x0)) && (param_1 != 0)) &&
     (4 < param_2)) {
    *param_3 = 0x47;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 4;
    uVar7 = 4;
    bVar1 = *(byte *)(param_1 + 4);
    if (bVar1 == 0) {
      local_64 = 0;
      iVar4 = input_tick_read(&local_64);
      if (iVar4 != 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00575414,DAT_00575410,DAT_00575364,0xadc,DAT_00575420,iVar4);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00575424,DAT_00575424,iVar4);
        }
      }
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575364,0xade,DAT_00575524,local_64);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00575528,DAT_00575528,local_64);
      }
      param_3[4] = (char)local_64;
      param_3[5] = (char)(local_64 >> 8);
      param_3[6] = (char)(local_64 >> 0x10);
      param_3[7] = (char)(local_64 >> 0x18);
      uVar7 = 8;
    }
    else if (bVar1 == 2) {
      local_5c = 0;
      iVar4 = FUN_00512b20(&local_5c);
      if (iVar4 != 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00575414,DAT_00575410,DAT_00575364,0xafb,DAT_0057553c,iVar4);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00575540,DAT_00575540,iVar4);
        }
      }
      uVar6 = local_5c;
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575364,0xafe,DAT_00575544,uVar6 & 0xff);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_005756d4,DAT_005756d4,uVar6 & 0xff);
      }
      param_3[4] = (char)uVar6;
      param_3[5] = 0;
      param_3[6] = 0;
      param_3[7] = 0;
      uVar7 = 8;
    }
    else if (bVar1 < 2) {
      local_60 = 0;
      iVar4 = FUN_004700b4(&local_60);
      if (iVar4 != 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00575414,DAT_00575410,DAT_00575364,0xaec,DAT_0057552c,iVar4);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00575530,DAT_00575530,iVar4);
        }
      }
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575364,0xaee,DAT_00575534,local_60);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00575538,DAT_00575538,local_60);
      }
      param_3[4] = (char)local_60;
      param_3[5] = (char)((uint)local_60 >> 8);
      param_3[6] = (char)((uint)local_60 >> 0x10);
      param_3[7] = 0;
      uVar7 = 8;
    }
    else if (bVar1 == 4) {
      local_6c = 0;
      iVar4 = DRV_MAGReadWhoAmI(&local_6c);
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575364,0xb1a,DAT_005756e8,local_6c);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_005756ec,DAT_005756ec,local_6c);
      }
      if (iVar4 != 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00575414,DAT_00575410,DAT_00575364,0xb1d,DAT_005756f0,iVar4);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_005756f4,DAT_005756f4,iVar4);
        }
      }
      param_3[4] = (char)local_6c;
      param_3[5] = (char)(local_6c >> 8);
      param_3[6] = (char)(local_6c >> 0x10);
      param_3[7] = (char)(local_6c >> 0x18);
      uVar7 = 8;
    }
    else if (bVar1 < 4) {
      local_68 = 0;
      iVar4 = DRV_IMUReadWhoAmI(&local_68);
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575364,0xb0a,DAT_005756d8,local_68);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_005756dc,DAT_005756dc,local_68);
      }
      if (iVar4 != 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00575414,DAT_00575410,DAT_00575364,0xb0d,DAT_005756e0,iVar4);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_005756e4,DAT_005756e4,iVar4);
        }
      }
      param_3[4] = (char)local_68;
      param_3[5] = (char)(local_68 >> 8);
      param_3[6] = (char)(local_68 >> 0x10);
      param_3[7] = (char)(local_68 >> 0x18);
      uVar7 = 8;
    }
    else if (bVar1 == 6) {
      FUN_0058f936();
      ti_opt3007_assignRegistermap(auStack_58);
      FUN_0058f8cc(auStack_58);
      FUN_0058f8d8(auStack_58);
      uVar3 = FUN_0058f922(auStack_58);
      uVar6 = FUN_0058f92c(auStack_58);
      uVar8 = (uint)uVar3 | uVar6 << 0x10;
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_68 = uVar6 & 0xffff;
        local_6c = (uint)uVar3;
        FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575364,0xb43,DAT_00575700,uVar8);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xcc00000,DAT_00575704,DAT_00575704,uVar8,uVar3,uVar6 & 0xffff);
      }
      param_3[4] = (char)uVar3;
      param_3[5] = (char)(uVar3 >> 8);
      param_3[6] = (char)uVar6;
      param_3[7] = (char)(uVar6 >> 8);
      uVar7 = 8;
    }
    else if (bVar1 < 6) {
      uVar6 = uled_safe_get_chip_id();
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575364,0xb29,DAT_005756f8,uVar6 & 0xffff);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_005756fc,DAT_005756fc,uVar6 & 0xffff);
      }
      param_3[4] = (char)uVar6;
      param_3[5] = (char)(uVar6 >> 8);
      param_3[6] = 0;
      param_3[7] = 0;
      uVar7 = 8;
    }
    else if (bVar1 == 7) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_64 = (uint)(byte)DAT_00575ac0[3];
        local_68 = (uint)(byte)DAT_00575ac0[2];
        local_6c = (uint)(byte)DAT_00575ac0[1];
        FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575364,0xb4d,DAT_005759f4,*DAT_00575ac0);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xd000000,DAT_005759f8,DAT_005759f8,*DAT_00575ac0,DAT_00575ac0[1],
                            DAT_00575ac0[2],DAT_00575ac0[3]);
      }
      puVar2 = DAT_00575ac0;
      param_3[4] = *DAT_00575ac0;
      param_3[5] = puVar2[1];
      param_3[6] = puVar2[2];
      param_3[7] = puVar2[3];
      uVar7 = 8;
    }
    else {
      *param_3 = 0x48;
      param_3[1] = 1;
      param_3[2] = 3;
      param_3[3] = 1;
      param_3[4] = 3;
    }
    *param_4 = uVar7;
    return 0;
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(1,DAT_00575414,DAT_00575410,DAT_00575364,0xac8,DAT_00575418,DAT_00575364);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x4400000,DAT_0057541c,DAT_0057541c,DAT_00575364);
  }
  return 0xffffffff;
}

