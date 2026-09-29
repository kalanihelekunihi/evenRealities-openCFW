
void APP_BleRingProcMsg(undefined4 param_1,undefined2 *param_2)

{
  char cVar1;
  char *pcVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  short sVar6;
  
  if (param_2 != (undefined2 *)0x0) {
    cVar1 = *(char *)(param_2 + 1);
    if (((cVar1 == '\x05') || (cVar1 == '\r')) || (cVar1 == '\x0e')) {
      iVar4 = DmConnRole(*DAT_004c4c68);
      if (iVar4 == 0) {
        _bleRingReceiveData(param_2);
      }
    }
    else if (cVar1 == '\'') {
      iVar4 = DmConnRole((char)*param_2);
      pcVar2 = DAT_004c4c68;
      if (iVar4 == 0) {
        *DAT_004c4c68 = (char)*param_2;
        *(short *)(pcVar2 + 8) = *(short *)(pcVar2 + 8) + 1;
        **(undefined2 **)(pcVar2 + 4) = 0x10;
        *(undefined2 *)(*(int *)(pcVar2 + 4) + 2) = 0x12;
        *(undefined2 *)(*(int *)(pcVar2 + 4) + 4) = 0x13;
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004c4c78,DAT_004c4c74,DAT_004c4cb4,0x110,DAT_004c4ccc,
                       *(undefined2 *)(*(int *)(pcVar2 + 4) + 4));
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_004c4cd0,DAT_004c4cd0,
                              *(undefined2 *)(*(int *)(pcVar2 + 4) + 4));
        }
        uVar3 = DAT_004c4cd4;
        if (*(short *)(*(int *)(pcVar2 + 4) + 4) != 0) {
          fw_event_loop_remove_delayed(DAT_004c4cd4);
          uVar5 = ringPackCccdEpochValue(*pcVar2,0,*(undefined2 *)(pcVar2 + 8));
          fw_event_loop_push_delayed(uVar3,uVar5,500);
          uVar5 = ringPackCccdEpochValue(*pcVar2,0,*(undefined2 *)(pcVar2 + 8));
          fw_event_loop_push_delayed(uVar3,uVar5,700);
          uVar5 = ringPackCccdEpochValue(*pcVar2,1,*(undefined2 *)(pcVar2 + 8));
          fw_event_loop_push_delayed(uVar3,uVar5,900);
        }
      }
    }
    else if (cVar1 == '(') {
      iVar4 = DmConnRole((char)*param_2);
      pcVar2 = DAT_004c4c68;
      if (iVar4 == 0) {
        *DAT_004c4c68 = '\0';
        *(short *)(pcVar2 + 8) = *(short *)(pcVar2 + 8) + 1;
        if (*(int *)(pcVar2 + 4) != 0) {
          **(undefined2 **)(pcVar2 + 4) = 0;
          *(undefined2 *)(*(int *)(pcVar2 + 4) + 2) = 0;
          *(undefined2 *)(*(int *)(pcVar2 + 4) + 4) = 0;
        }
        fw_event_loop_remove_delayed(DAT_004c4cd4);
        Thread_SendEvtToRingTask(8);
      }
    }
    else if (cVar1 == -0x54) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004c4c78,DAT_004c4c74,DAT_004c4cb4,0xe7,DAT_004c4cb0);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004c4cb8);
      }
      pcVar2 = DAT_004c4c68;
      if (*(int *)(DAT_004c4c68 + 4) == 0) {
        sVar6 = 0;
      }
      else {
        sVar6 = **(short **)(DAT_004c4c68 + 4);
      }
      cVar1 = (char)*param_2;
      if (((cVar1 == '\0') || (cVar1 != *DAT_004c4c68)) || (sVar6 == 0)) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004c4c78,DAT_004c4c74,DAT_004c4cb4,0xf6,DAT_004c4cbc,cVar1,*pcVar2,
                       sVar6);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8c00000,DAT_004c4cc0,DAT_004c4cc0,cVar1,*pcVar2,sVar6);
        }
        thread_ble_wsf_tx_complete_notify();
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004c4c78,DAT_004c4c74,DAT_004c4cb4,0xfa,DAT_004c4cc4,0,sVar6);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_004c4cc8,DAT_004c4cc8,0,sVar6);
        }
        AttcWriteCmd(cVar1,sVar6,param_2[4],*(undefined4 *)(param_2 + 2));
      }
    }
  }
  return;
}

