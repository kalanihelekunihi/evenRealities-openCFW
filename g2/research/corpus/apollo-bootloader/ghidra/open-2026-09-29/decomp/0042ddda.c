
void runtime_action_context_deinit_42ddda(void)

{
  int iVar1;
  
  iVar1 = DAT_0042e158;
  if (*(int *)(DAT_0042e158 + 8) != 0) {
    bl_runtime_action(*(undefined4 *)(DAT_0042e158 + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return;
}

