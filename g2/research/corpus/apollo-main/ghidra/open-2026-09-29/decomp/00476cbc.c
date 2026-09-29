
void _bleSlaveConnUpdate(char param_1,int param_2)

{
  undefined4 uVar1;
  undefined2 uVar2;
  int iVar3;
  undefined4 uVar4;
  bool bVar5;
  undefined2 local_1c;
  undefined2 local_1a;
  undefined2 local_18;
  undefined2 local_16;
  undefined2 local_14;
  undefined2 local_12;
  
  iVar3 = DmConnCheckIdle(*(undefined1 *)(param_2 + 4));
  bVar5 = iVar3 == 0;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    uVar2 = DmConnCheckIdle(*(undefined1 *)(param_2 + 4));
    FUN_0043d574(4,DAT_0047774c,DAT_00477748,DAT_00477744,0xa0,DAT_00477740,bVar5,
                 *(undefined1 *)(param_2 + 10),uVar2);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    uVar2 = DmConnCheckIdle(*(undefined1 *)(param_2 + 4));
    compress_log_output(0x10c00000,DAT_00477750,DAT_00477750,bVar5,*(undefined1 *)(param_2 + 10),
                        uVar2);
  }
  if ((bVar5) && (*(char *)(param_2 + 10) != '\0')) {
    *(char *)(param_2 + 0xc) = *(char *)(param_2 + 0xc) + '\x01';
    local_1c = *(undefined2 *)(*DAT_00477754 + 4);
    local_1a = *(undefined2 *)(*DAT_00477754 + 6);
    local_18 = *(undefined2 *)(*DAT_00477754 + 8);
    local_16 = *(undefined2 *)(*DAT_00477754 + 10);
    local_14 = 0;
    local_12 = 0xffff;
    DmConnUpdate(*(undefined1 *)(param_2 + 4),&local_1c);
  }
  else {
    *(bool *)(param_2 + 10) = bVar5;
    uVar1 = DAT_00477758;
    fw_event_loop_remove_delayed(DAT_00477758);
    if (param_1 == -0x5d) {
      uVar4 = 2000;
    }
    else {
      uVar4 = 4000;
    }
    fw_event_loop_push_delayed(uVar1,param_1,uVar4);
  }
  return;
}

