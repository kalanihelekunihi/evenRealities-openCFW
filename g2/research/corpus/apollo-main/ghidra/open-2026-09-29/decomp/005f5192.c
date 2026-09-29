
void Ins_NROUND(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  
  uVar1 = Round_None(param_1,*param_2,
                     *(undefined4 *)(param_1 + (uint)*(byte *)(param_1 + 0x174) * 4 + -0xa4));
  *param_2 = uVar1;
  return;
}

