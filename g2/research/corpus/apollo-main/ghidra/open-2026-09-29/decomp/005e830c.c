
undefined1 semantic_terminal_cached_session_status(int param_1)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = td_active_session();
  if (iVar1 != 0) {
    for (uVar2 = 0; uVar2 < *(uint *)(iVar1 + 8); uVar2 = uVar2 + 1) {
      if (*(int *)(uVar2 * 0x90 + iVar1 + 0x9c) == param_1) {
        return *(undefined1 *)(iVar1 + uVar2 * 0x90 + 0x122);
      }
    }
  }
  return 0;
}

