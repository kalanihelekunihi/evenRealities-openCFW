
void conversate_ui_action_tag_to_main_page(void)

{
  char *pcVar1;
  int iVar2;
  
  pcVar1 = DAT_005b6958;
  FUN_0043dfa4(*(undefined4 *)(DAT_005b6958 + 8),1);
  FUN_0044d90e(*(undefined4 *)(pcVar1 + 0x1c));
  pcVar1[0x1c] = '\0';
  pcVar1[0x1d] = '\0';
  pcVar1[0x1e] = '\0';
  pcVar1[0x1f] = '\0';
  pcVar1[0x98] = '\0';
  if (((*pcVar1 == '\x02') && (pcVar1[0x96] == '\0')) && (iVar2 = FUN_005967bc(), iVar2 == 1)) {
    FUN_005b02e4(8,1);
  }
  return;
}

