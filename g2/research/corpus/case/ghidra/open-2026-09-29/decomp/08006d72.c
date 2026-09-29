
int case_wait_controller_ready(int *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = *param_1;
  iVar3 = 0;
  if (-1 < *(int *)(iVar1 + 0xc) << 0x19) {
    *(uint *)(iVar1 + 0xc) = *(uint *)(iVar1 + 0xc) | 0x80;
    iVar1 = case_tick_word2();
    while ((-1 < *(int *)(*param_1 + 0xc) << 0x19 && (iVar3 != 3))) {
      iVar2 = case_tick_word2();
      if (1000 < (uint)(iVar2 - iVar1)) {
        iVar3 = 3;
        *(undefined1 *)((int)param_1 + 0x29) = 3;
      }
    }
  }
  return iVar3;
}

