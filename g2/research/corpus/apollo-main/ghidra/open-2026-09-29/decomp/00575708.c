
undefined4 pt_cmd_54_handler(int param_1,byte param_2,int param_3,int param_4)

{
  byte bVar1;
  ushort uVar2;
  byte *pbVar3;
  uint *puVar4;
  ushort uVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  bool bVar9;
  uint uVar10;
  
  if ((((param_1 == 0) || (param_3 == 0)) || (param_4 == 0)) || (param_2 < 4)) {
    uVar6 = 0xffffffff;
  }
  else {
    uVar2 = *(ushort *)(param_1 + 3);
    bVar9 = *(char *)(param_1 + 5) != '\0';
    bVar1 = *(byte *)(param_1 + 6);
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00575e98,DAT_00575e94,DAT_00576108,0xc3a,DAT_00576104,bVar1,*DAT_00575ea0,
                   bVar9);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_0057610c,DAT_0057610c,bVar1,*DAT_00575ea0,bVar9);
    }
    pbVar3 = DAT_00575ea0;
    if (bVar1 == *DAT_00575ea0) {
      if (uVar2 < 3) {
        iVar7 = 0;
      }
      else {
        iVar7 = uVar2 - 4;
      }
      param_1 = param_1 + 7;
      uVar2 = CONCAT11(*(undefined1 *)(param_1 + iVar7 + 1),*(undefined1 *)(param_1 + iVar7));
      uVar5 = FUN_0049acd4(param_1,iVar7,0);
      uVar10 = (uint)uVar5;
      if (uVar5 == uVar2) {
        if ((bVar9) || (iVar7 == 1000)) {
          if (iVar7 != 0) {
            *pbVar3 = bVar1 + 1;
            puVar4 = DAT_005760ec;
            FUN_00439be4(DAT_00576128 + *DAT_005760ec,param_1,iVar7);
            *puVar4 = iVar7 + *puVar4;
          }
          iVar7 = DAT_00576128;
          puVar4 = DAT_005760ec;
          if ((5999 < *DAT_005760ec) || (bVar9)) {
            FUN_00439be4(DAT_005764e0,DAT_00576128,*DAT_005760ec);
            *DAT_005764e4 = *puVar4;
            *DAT_005764e8 = 1;
            *puVar4 = 0;
            FUN_0043c0e4(iVar7,0x1b70,0);
          }
          uVar6 = pt_handler_result(0x54,0,3,param_3,param_4);
        }
        else {
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00575e98,DAT_00575e94,DAT_00576108,0xc53,DAT_00576120,iVar7);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_00576124,DAT_00576124,iVar7);
          }
          uVar6 = pt_handler_result(0x54,1,3,param_3,param_4);
        }
      }
      else {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00575e98,DAT_00575e94,DAT_00576108,0xc4d,DAT_00576118,uVar10 & 0xffff,
                       uVar2);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_0057611c,DAT_0057611c,uVar10 & 0xffff,uVar2);
        }
        uVar6 = pt_handler_result(0x54,1,3,param_3,param_4);
      }
    }
    else if ((uint)*DAT_00575ea0 == (bVar1 + 1) % 0x100) {
      *DAT_00575ea0 = bVar1 + 1;
      uVar6 = pt_handler_result(0x54,0,3,param_3,param_4);
    }
    else {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00575e98,DAT_00575e94,DAT_00576108,0xc40,DAT_00576110,bVar1,*pbVar3);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_00576114,DAT_00576114,bVar1,*pbVar3);
      }
      uVar6 = pt_handler_result(0x54,1,3,param_3,param_4);
    }
  }
  return uVar6;
}

