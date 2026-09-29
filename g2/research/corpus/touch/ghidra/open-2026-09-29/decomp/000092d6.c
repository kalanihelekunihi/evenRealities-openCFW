
void Cy_SCB_WriteDefaultArrayNoCheck(int param_1,undefined4 param_2,int param_3)

{
  for (; param_3 != 0; param_3 = param_3 + -1) {
    *(undefined4 *)(param_1 + 0x240) = param_2;
  }
  return;
}

