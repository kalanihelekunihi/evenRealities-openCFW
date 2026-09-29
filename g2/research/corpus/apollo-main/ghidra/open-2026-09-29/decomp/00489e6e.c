
undefined8 FUN_00489e6e(int param_1)

{
  int iVar1;
  int local_10;
  
  iVar1 = 0;
  local_10 = 0;
  while (*(char *)(param_1 + local_10) != '\0') {
    (*(code *)*DAT_00489eac)(param_1,&local_10);
    iVar1 = iVar1 + 1;
  }
  return CONCAT44(local_10,iVar1);
}

