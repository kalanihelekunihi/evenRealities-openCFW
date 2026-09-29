
undefined8 FUN_004739fc(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_004742f8;
  uVar1 = osMessageQueueNew(0x60,0x24,DAT_00474318);
  *(undefined4 *)(iVar2 + 0xc) = uVar1;
  if (*(int *)(iVar2 + 0xc) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x6e;
      param_2 = DAT_0047431c;
      FUN_0043d574(1,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_00474320,0x6e,DAT_0047431c,
                   param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00474324);
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0x70;
      param_2 = DAT_00474328;
      FUN_0043d574(4,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_00474320,0x70,DAT_00474328,
                   *(undefined4 *)(iVar2 + 0xc),param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0047447c,DAT_0047447c,*(undefined4 *)(iVar2 + 0xc));
    }
  }
  return CONCAT44(param_2,param_1);
}

