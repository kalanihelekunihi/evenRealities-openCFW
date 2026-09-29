
void guarded_context_teardown_42e3ca(void)

{
  int iVar1;
  
  iVar1 = DAT_0042e46c;
  if (*(int *)(DAT_0042e46c + 8) != 0) {
    bl_runtime_action(*(undefined4 *)(DAT_0042e46c + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return;
}

