
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void even_ai_stream_on_auto_reflash(void)

{
  int *piVar1;
  char *pcVar2;
  int *piVar3;
  char cVar4;
  short sVar5;
  short sVar6;
  undefined2 uVar7;
  ushort uVar8;
  ushort uVar9;
  int iVar10;
  int iVar11;
  undefined4 uVar12;
  undefined4 in_r3;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  uint uStack_28;
  uint uStack_24;
  undefined4 uStack_20;
  
  pcVar2 = DAT_004e607c;
  if (*DAT_004e607c == '\0') {
    return;
  }
  if (DAT_004e607c[1] == '\0') {
    return;
  }
  uStack_20 = in_r3;
  FUN_004e1fa6();
  piVar3 = DAT_004e60ec;
  piVar1 = DAT_004e5f90;
  if ((*DAT_004e5f90 == 0) || (*DAT_004e60ec == 0)) {
    iVar10 = FUN_0043d0ce();
    if (iVar10 << 0x1e < 0) {
      uStack_2c = DAT_004e61a8;
      uStack_30 = 0x19a;
      FUN_0043d574(1,DAT_004e5fa0,DAT_004e5f9c,_DAT_004e61ec);
    }
    iVar10 = FUN_0043d0ce();
    if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004e61b0,DAT_004e61b0);
    }
    *pcVar2 = '\0';
  }
  else {
    iVar10 = even_ai_tick_get();
    if (*pcVar2 == '\x02') {
      if ((pcVar2[1] == '\x02') &&
         ((*(char *)(DAT_004e60e4 + 0xc) == '\x01' ||
          ((*(int *)(pcVar2 + 0x1c) != 0 && (5000 < (uint)(iVar10 - *(int *)(pcVar2 + 0x1c)))))))) {
        *pcVar2 = '\0';
        service_even_ai_fn_00498310(2);
      }
    }
    else if (*(uint *)(pcVar2 + 0x10) <= (uint)(iVar10 - *(int *)(pcVar2 + 0xc))) {
      cVar4 = FUN_0045a568();
      if (*(ushort *)(pcVar2 + 8) <= *(ushort *)(pcVar2 + 6)) {
        if (pcVar2[0x14] == '\0') {
          pcVar2[0x14] = '\x01';
          *(int *)(pcVar2 + 0x18) = iVar10;
        }
        iVar11 = even_ai_stream_interval_get();
        if ((uint)(iVar10 - *(int *)(pcVar2 + 0x18)) < (uint)(iVar11 * 0xc)) goto LAB_004e5a04;
        iVar10 = FUN_0043d0ce();
        if (iVar10 << 0x1e < 0) {
          uStack_24 = (uint)*(ushort *)(pcVar2 + 8);
          uStack_28 = (uint)*(ushort *)(pcVar2 + 6);
          uStack_2c = _DAT_004e62b8;
          uStack_30 = 0x1c6;
          FUN_0043d574(2,DAT_004e5fa0,DAT_004e5f9c,_DAT_004e61ec);
        }
        iVar10 = FUN_0043d0ce();
        if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
          uStack_30 = (uint)*(ushort *)(pcVar2 + 8);
          compress_log_output(0x8800000,_DAT_004e62bc,_DAT_004e62bc,*(undefined2 *)(pcVar2 + 6));
        }
        pcVar2[0x14] = '\0';
      }
      sVar5 = text_stream_current_length(*piVar1);
      text_stream_copy_until_boundary(*piVar1,0);
      sVar6 = text_stream_current_length(*piVar1);
      if (sVar6 == sVar5) {
        if (pcVar2[1] == '\x02') {
          *pcVar2 = '\x02';
          uVar12 = even_ai_tick_get();
          *(undefined4 *)(pcVar2 + 0x1c) = uVar12;
          if (*(char *)(DAT_004e60e4 + 9) == '\x01') {
            FUN_005537cc(0);
          }
          else {
            FUN_0055389a();
          }
        }
        else if (pcVar2[1] == '\x01') {
          *pcVar2 = '\0';
        }
      }
      else {
        uVar12 = text_stream_current_text(*piVar1);
        if (pcVar2[1] == '\x01') {
          if ((*(int *)*piVar3 != 0) && (iVar10 = FUN_0043e2ea(*(undefined4 *)*piVar3), iVar10 != 0)
             ) {
            FUN_0049942e(*(undefined4 *)*piVar3,uVar12);
            even_ai_common_timer_mgr_start(8000);
            uVar7 = text_stream_current_length(*piVar1);
            even_ai_node_stream_state_init(*piVar3,1,uVar7);
            if (0x400 < *(ushort *)(DAT_004e64a8 + 0x1a)) {
              even_ai_manage_char_window();
            }
          }
        }
        else if (((pcVar2[1] == '\x02') && (*(int *)(*piVar3 + 8) != 0)) &&
                (iVar10 = FUN_0043e2ea(*(undefined4 *)(*piVar3 + 8)), iVar10 != 0)) {
          FUN_0049942e(*(undefined4 *)(*piVar3 + 8),uVar12);
          even_ai_common_timer_mgr_start(10000);
          uVar7 = text_stream_current_length(*piVar1);
          even_ai_node_stream_state_init(*piVar3,0,uVar7);
          if (0x400 < *(ushort *)(DAT_004e64a8 + 0x1a)) {
            even_ai_manage_char_window();
          }
        }
        *(short *)(pcVar2 + 6) = *(short *)(pcVar2 + 6) + 1;
        *(short *)(pcVar2 + 4) = sVar6;
        uVar12 = even_ai_tick_get();
        *(undefined4 *)(pcVar2 + 0xc) = uVar12;
        even_ai_layout_refresh();
        uVar8 = text_stream_pending_length(*piVar1);
        if ((cVar4 == '\x01') &&
           ((*(ushort *)(pcVar2 + 8) <= *(ushort *)(pcVar2 + 6) ||
            (uVar9 = text_stream_current_length(*piVar1), uVar8 <= uVar9)))) {
          uStack_30._0_2_ = CONCAT11(pcVar2[1],5);
          uVar7 = text_stream_current_length(*piVar1);
          uStack_30 = CONCAT13((char)((ushort)uVar7 >> 8),
                               CONCAT12((char)uVar7,(undefined2)uStack_30));
          FUN_00464bb2(7,&uStack_30,4,0);
        }
        uVar9 = text_stream_current_length(*piVar1);
        if (uVar8 <= uVar9) {
          if (pcVar2[1] == '\x02') {
            *pcVar2 = '\x02';
            uVar12 = even_ai_tick_get();
            *(undefined4 *)(pcVar2 + 0x1c) = uVar12;
            if (*(char *)(DAT_004e60e4 + 9) == '\x01') {
              FUN_005537cc(0);
            }
            else {
              FUN_0055389a();
            }
          }
          else {
            *pcVar2 = '\0';
          }
        }
      }
    }
  }
LAB_004e5a04:
  FUN_004e1fbe();
  return;
}

