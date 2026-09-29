
void case_reset_timer_fields(int param_1)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 0x28);
  *(undefined2 *)(iVar1 + 0x5e) = 0;
  *(undefined2 *)(iVar1 + 0x56) = 0;
  FUN_08005f42();
  return;
}

