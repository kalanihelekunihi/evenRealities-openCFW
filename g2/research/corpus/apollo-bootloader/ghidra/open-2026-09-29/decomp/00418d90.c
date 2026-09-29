
int FUN_00418d90(void)

{
  int *piVar1;
  
  piVar1 = DAT_00419220;
  if (*DAT_00419220 != 0) {
    *(int *)(*DAT_00419220 + 100) = *(int *)(*DAT_00419220 + 100) + 1;
  }
  return *piVar1;
}

