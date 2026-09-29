
void tpl_reset_receive_contexts_004b9984(void)

{
  int iVar1;
  
  fw_event_loop_remove_delayed(DAT_004b9a18);
  for (iVar1 = 0; iVar1 < 4; iVar1 = iVar1 + 1) {
    if (*(char *)(iVar1 * 0x38 + DAT_004b9a7c + 0x30) != '\0') {
      tpl_context_free_004b8ba2(DAT_004b9a7c + iVar1 * 0x38);
    }
  }
  return;
}

