
void FUN_004918a8(int param_1,byte param_2,undefined4 *param_3)

{
  *param_3 = 0;
  if ((uint)param_2 == *(byte *)(param_1 + 0x715a) - 1) {
    *(char *)(param_1 + 0x715a) = *(char *)(param_1 + 0x715a) + -1;
  }
  return;
}

