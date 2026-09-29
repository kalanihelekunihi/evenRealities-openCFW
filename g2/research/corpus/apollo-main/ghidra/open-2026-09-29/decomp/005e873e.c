
undefined8 terminal_request_runtime_event_if_allowed(uint param_1,undefined4 param_2)

{
  char cVar1;
  int iVar2;
  char cVar3;
  undefined4 uVar4;
  int iVar5;
  
  cVar3 = FUN_005e50ea(param_1 & 0xff);
  iVar2 = DAT_005e8c04;
  cVar1 = *(char *)(DAT_005e8c04 + 0x275);
  if (cVar3 == '\x16') {
    if ((cVar1 == '\0') || (*DAT_005e904c == 0)) {
      if (*(int *)(DAT_005e8c04 + 0x288) == 0) {
        uVar4 = td_counter_b_get();
        *(undefined4 *)(iVar2 + 0x288) = uVar4;
      }
      *(undefined1 *)(iVar2 + 0x277) = 0;
      *(undefined1 *)(iVar2 + 0x27f) = 0;
      terminal_request_display(0x16,*(undefined4 *)(iVar2 + 0x288));
    }
    else {
      iVar5 = semantic_terminal_state_allows_runtime_event(cVar1);
      if (iVar5 == 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          param_1 = 0xec;
          param_2 = DAT_005e905c;
          FUN_0043d574(2,DAT_005e8c18,DAT_005e8c14,DAT_005e9060,0xec,DAT_005e905c,cVar1,
                       *(undefined4 *)(iVar2 + 0x288));
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          param_1 = *(uint *)(iVar2 + 0x288);
          compress_log_output(0x8800000,PTR_s__terminal_pb_drop_runtime_query_n_005e9318,
                              PTR_s__terminal_pb_drop_runtime_query_n_005e9318,cVar1);
        }
      }
      else {
        terminal_request_display(0x16,*(undefined4 *)(iVar2 + 0x288));
      }
    }
  }
  else {
    terminal_request_display(cVar3,0);
  }
  return CONCAT44(param_2,param_1);
}

