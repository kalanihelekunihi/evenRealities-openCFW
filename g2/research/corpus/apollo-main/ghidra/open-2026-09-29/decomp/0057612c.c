
undefined4 pt_cmd_5A_handler(int param_1,byte param_2,undefined1 *param_3,char *param_4)

{
  byte bVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  char cVar7;
  uint uVar8;
  uint local_10c [60];
  
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005768bc,DAT_005768b8,DAT_00576bbc,0xccc,DAT_00576bb8);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00576bc0,DAT_00576bc0);
  }
  piVar2 = DAT_00576a3c;
  if ((((param_1 == 0) || (param_3 == (undefined1 *)0x0)) || (param_4 == (char *)0x0)) ||
     (param_2 < 9)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005768bc,DAT_005768b8,DAT_00576bbc,0xcce,DAT_00576bc4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00576bc8,DAT_00576bc8);
    }
    uVar4 = 0xffffffff;
  }
  else if (*DAT_00576a3c == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005768bc,DAT_005768b8,DAT_00576bbc,0xcd4,DAT_00576bcc);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00576bd0,DAT_00576bd0);
    }
    uVar4 = pt_handler_result(0x5a,1,2,param_3,param_4);
  }
  else {
    uVar8 = *(int *)(param_1 + 4) + 0x20;
    bVar1 = *(byte *)(param_1 + 8);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_10c[0] = (uint)bVar1;
      FUN_0043d574(3,DAT_005768bc,DAT_005768b8,DAT_00576bbc,0xcdc,DAT_00576d3c,uVar8);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_00576d40,DAT_00576d40,uVar8,bVar1);
    }
    if (bVar1 < 0xf1) {
      iVar3 = file_seek(*piVar2,uVar8,0);
      if (iVar3 == 0) {
        uVar5 = file_tell(*piVar2);
        if (uVar5 == uVar8) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_005768bc,DAT_005768b8,DAT_00576bbc,0xcee,DAT_00576dec,uVar8);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_00576df0,DAT_00576df0,uVar8);
          }
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            local_10c[0] = uVar5;
            FUN_0043d574(2,DAT_005768bc,DAT_005768b8,DAT_00576bbc,0xcec,DAT_00576de4,uVar8);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x8800000,DAT_00576de8,DAT_00576de8,uVar8,uVar5);
          }
        }
        uVar8 = file_read(local_10c,1,bVar1,*piVar2);
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(3,DAT_005768bc,DAT_005768b8,DAT_00576bbc,0xcf5,DAT_00576df4,uVar8);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_005770b4,DAT_005770b4,uVar8);
        }
        cVar7 = '\0';
        *param_3 = 0x5a;
        param_3[1] = 1;
        param_3[2] = 2;
        param_3[3] = (char)uVar8 + '\x01';
        uVar5 = 4;
        if (uVar8 != 0) {
          FUN_00439be4(param_3 + 4,local_10c,uVar8);
          uVar5 = uVar8 + 4;
        }
        for (uVar6 = 0; uVar6 < uVar8; uVar6 = uVar6 + 1) {
          cVar7 = *(char *)((int)local_10c + uVar6) + cVar7;
        }
        param_3[uVar5 & 0xff] = cVar7;
        *param_4 = (char)uVar5 + '\x01';
        uVar4 = 0;
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005768bc,DAT_005768b8,DAT_00576bbc,0xce5,DAT_00576ddc);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00576de0,DAT_00576de0);
        }
        uVar4 = pt_handler_result(0x5a,1,2,param_3,param_4);
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005768bc,DAT_005768b8,DAT_00576bbc,0xcdf,DAT_00576d44);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00576dd8,DAT_00576dd8);
      }
      uVar4 = pt_handler_result(0x5a,1,2,param_3,param_4);
    }
  }
  return uVar4;
}

