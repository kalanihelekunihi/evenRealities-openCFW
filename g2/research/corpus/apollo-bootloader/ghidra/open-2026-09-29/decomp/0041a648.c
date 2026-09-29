
void FUN_0041a648(void)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_0041a6e0;
  if (*DAT_0041a6e0 == 0) {
    iVar2 = bl_runtime_flags_create(DAT_0041a6e4);
    *piVar1 = iVar2;
  }
  return;
}

