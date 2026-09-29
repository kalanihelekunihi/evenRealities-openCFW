
void even_ai_stream_phase_update(char param_1,ushort param_2)

{
  int *piVar1;
  char *pcVar2;
  int *piVar3;
  ushort uVar4;
  ushort uVar5;
  uint uVar6;
  undefined4 uVar7;
  int iVar8;
  
  pcVar2 = DAT_004e607c;
  piVar1 = DAT_004e5f90;
  if ((((*DAT_004e607c != '\0') && (param_1 != '\0')) && (DAT_004e607c[1] == param_1)) &&
     (*DAT_004e5f90 != 0)) {
    FUN_004e1fa6();
    uVar4 = text_stream_pending_length(*piVar1);
    if (uVar4 < param_2) {
      param_2 = uVar4;
    }
    uVar6 = text_stream_current_length(*piVar1);
    if (uVar6 != param_2) {
      text_stream_copy_bytes(*piVar1,param_2,0);
      uVar7 = text_stream_current_text(*piVar1);
      piVar3 = DAT_004e60ec;
      if (pcVar2[1] == '\x01') {
        if (((*DAT_004e60ec != 0) && (*(int *)*DAT_004e60ec != 0)) &&
           (iVar8 = FUN_0043e2ea(*(undefined4 *)*DAT_004e60ec), iVar8 != 0)) {
          FUN_0049942e(*(undefined4 *)*piVar3,uVar7);
        }
      }
      else if (((pcVar2[1] == '\x02') && (*DAT_004e60ec != 0)) &&
              ((*(int *)(*DAT_004e60ec + 8) != 0 &&
               (iVar8 = FUN_0043e2ea(*(undefined4 *)(*DAT_004e60ec + 8)), iVar8 != 0)))) {
        FUN_0049942e(*(undefined4 *)(*piVar3 + 8),uVar7);
      }
      even_ai_layout_refresh();
    }
    *(ushort *)(pcVar2 + 4) = param_2;
    pcVar2[6] = '\0';
    pcVar2[7] = '\0';
    uVar7 = even_ai_tick_get();
    *(undefined4 *)(pcVar2 + 0xc) = uVar7;
    pcVar2[0x14] = '\0';
    uVar4 = text_stream_pending_length(*piVar1);
    uVar5 = text_stream_current_length(*piVar1);
    if (uVar4 <= uVar5) {
      if (pcVar2[1] == '\x02') {
        *pcVar2 = '\x02';
        uVar7 = even_ai_tick_get();
        *(undefined4 *)(pcVar2 + 0x1c) = uVar7;
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
    FUN_004e1fbe();
  }
  return;
}

