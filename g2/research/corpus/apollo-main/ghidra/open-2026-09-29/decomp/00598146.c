
bool FUN_00598146(int param_1)

{
  return (*(int *)(param_1 + 0xc) - *(int *)(param_1 + 8) & *(uint *)(param_1 + 4)) ==
         *(uint *)(param_1 + 4);
}

