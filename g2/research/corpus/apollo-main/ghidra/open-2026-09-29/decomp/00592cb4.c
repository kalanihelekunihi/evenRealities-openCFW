
undefined4
am_devices_jbd4010_QSPI_PartialReflash
          (int param_1,int param_2,int param_3,int param_4,int param_5,int param_6)

{
  undefined1 uVar1;
  undefined1 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  int local_30;
  int local_2c;
  int local_28;
  
  iVar5 = 0;
  if (0x27f < param_5) {
    param_5 = 0x27f;
  }
  local_30 = param_3;
  local_2c = param_2;
  local_28 = param_1;
  if (0x1df < param_6) {
    param_6 = 0x1df;
  }
  for (; param_4 <= param_6; param_4 = param_4 + 1) {
    iVar3 = (param_4 * 0x280) / 2 + *DAT_00593300 + local_30 / 2;
    uVar4 = DAT_0059374c & (param_4 + local_2c) * 0x400;
    iVar7 = param_5 / 2 - local_30 / 2;
    if (param_5 << 0x1f < 0) {
      iVar7 = iVar7 + 1;
    }
    uVar2 = *(undefined1 *)(iVar3 + iVar7);
    *(undefined1 *)(iVar3 + iVar7) = 0;
    uVar1 = *(undefined1 *)(iVar3 + iVar7 + 1);
    *(undefined1 *)(iVar3 + iVar7 + 1) = 0;
    iVar5 = jbd4010_write_data_block
                      (0,0x62,1,(uVar4 | local_30 + local_28 & 0x3ffU) << 8 | 0xff,iVar3,iVar7 + 2);
    *(undefined1 *)(iVar3 + iVar7) = uVar2;
    *(undefined1 *)(iVar3 + iVar7 + 1) = uVar1;
  }
  local_30 = 0;
  iVar3 = jbd4010_write_command(0x97,&local_30,0);
  if (iVar5 == 0 && iVar3 == 0) {
    uVar6 = 0;
  }
  else {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00593320,DAT_0059331c,DAT_005938d8,0x1cc,DAT_005938d4);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005938dc,DAT_005938dc);
    }
    uVar6 = 1;
  }
  FUN_004910f4(1);
  return uVar6;
}

