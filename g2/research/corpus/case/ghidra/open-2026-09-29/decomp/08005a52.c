
void case_mark_controller_ready(int *param_1)

{
  int iVar1;
  
  iVar1 = *param_1;
  if (*(int *)(iVar1 + 0x50) << 0x1d < 0) {
    *(uint *)(iVar1 + 0x5c) = *(uint *)(iVar1 + 0x5c) | 4;
    case_hook_08005a50(param_1);
  }
  *(undefined1 *)((int)param_1 + 0x29) = 1;
  return;
}

