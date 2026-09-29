
undefined8 _bleAdvInit(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined1 uVar4;
  int iVar5;
  
  iVar5 = productModeGet();
  puVar1 = DAT_0046dfe8;
  if (iVar5 == 1) {
    *DAT_0046dfe8 = 0;
    puVar1[3] = 0xa0;
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      param_2 = 0xc1;
      param_3 = DAT_0046dfec;
      FUN_0043d574(3,DAT_0046dff8,DAT_0046dff4,DAT_0046dff0,0xc1,DAT_0046dfec,param_4);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_0046dffc,DAT_0046dffc);
    }
  }
  else {
    *DAT_0046dfe8 = 30000;
    puVar1[3] = 0xa0;
    puVar1[4] = 0x640;
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      param_2 = 199;
      param_3 = DAT_0046e000;
      FUN_0043d574(3,DAT_0046dff8,DAT_0046dff4,DAT_0046dff0,199,DAT_0046e000,param_4);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_0046e004,DAT_0046e004);
    }
  }
  uVar2 = DAT_0046e008;
  AppAdvSetData(2,0x1c,DAT_0046e008);
  uVar3 = DAT_0046e00c;
  uVar4 = FUN_0044a43c(DAT_0046e00c);
  AppAdvSetData(3,uVar4,uVar3);
  AppAdvSetData(0,0x1c,uVar2);
  uVar4 = FUN_0044a43c(uVar3);
  AppAdvSetData(1,uVar4,uVar3);
  DmDevSetRandAddr(*DAT_0046e010 + 0xf);
  DmAdvSetAddrType(1);
  AppAdvStart(1);
  FUN_004b467c(1);
  return CONCAT44(param_3,param_2);
}

