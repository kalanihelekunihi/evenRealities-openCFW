
void td_session_bind_store(undefined4 param_1)

{
  int iVar1;
  
  iVar1 = DAT_00597c08;
  *(undefined4 *)(DAT_00597c08 + 0x9564) = param_1;
  if (*(int *)(iVar1 + 0x9560) != 0) {
    *(undefined1 *)(iVar1 + 0xa1d9) = 1;
  }
  return;
}

