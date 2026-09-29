
char terminal_data_append_agent_content
               (int param_1,short *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 uVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  bool bVar8;
  char local_2c [2];
  short local_2a;
  undefined4 uStack_28;
  
  iVar4 = DAT_00597be0;
  uVar5 = 0;
  local_2a = 0;
  if (param_2 != (short *)0x0) {
    *param_2 = -1;
  }
  if (param_1 == 0) {
    local_2c[0] = '\0';
  }
  else {
    uStack_28 = param_4;
    if (*(int *)(iVar4 + 0x8504) == 0) {
      td_session_ring_reset();
    }
    bVar8 = *(int *)(param_1 + 0x208) == 0;
    if (!bVar8) {
      uVar5 = *(undefined4 *)(param_1 + 0x208);
    }
    if (*(char *)(param_1 + 0x204) != '\x01' || bVar8) {
      iVar3 = td_session_ring_append(*(char *)(param_1 + 0x204) == '\x01',local_2c);
      if (iVar3 == 0) {
        local_2c[0] = '\0';
      }
      else {
        td_record_build_from_event(iVar3,param_1,uVar5);
        if (((local_2c[0] == '\x03') && (param_2 != (short *)0x0)) &&
           (*(short *)(iVar4 + 0x8500) != 0)) {
          *param_2 = *(short *)(iVar4 + 0x8500) + -1;
        }
      }
    }
    else {
      iVar3 = td_session_find_by_id(iVar4,uVar5,&local_2a);
      if (iVar3 == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00597c2c,DAT_00597c28,DAT_00597c64,0x279,DAT_00597c60,uVar5);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_00597c68,DAT_00597c68,uVar5);
        }
        local_2c[0] = '\0';
      }
      else {
        uVar2 = td_ring_index_wrap(iVar4,local_2a);
        iVar4 = iVar4 + (uint)uVar2 * 0x214;
        uVar6 = *(undefined4 *)(iVar4 + 0x210);
        uVar7 = *(undefined4 *)(iVar4 + 0x20c);
        uVar1 = *(undefined2 *)(iVar4 + 0x206);
        FUN_0043c0e4(iVar4,0x214,0);
        *(undefined4 *)(iVar4 + 0x210) = uVar6;
        *(undefined4 *)(iVar4 + 0x20c) = uVar7;
        *(undefined2 *)(iVar4 + 0x206) = uVar1;
        td_record_build_from_event(iVar4,param_1,uVar5);
        if (param_2 != (short *)0x0) {
          *param_2 = local_2a;
        }
        local_2c[0] = '\x03';
      }
    }
  }
  return local_2c[0];
}

