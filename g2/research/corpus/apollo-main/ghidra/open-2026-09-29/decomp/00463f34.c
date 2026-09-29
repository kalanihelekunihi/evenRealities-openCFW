
void FUN_00463f34(int param_1)

{
  int iVar1;
  
  if (((param_1 != 0) && (*(char *)(param_1 + 0x18) == '\x01')) &&
     (iVar1 = osKernelGetTickCount(),
     *(uint *)(param_1 + 0x10) <= (uint)(iVar1 - *(int *)(param_1 + 0x14)))) {
    *(int *)(param_1 + 0x14) = iVar1;
    FUN_00464008(param_1);
  }
  return;
}

