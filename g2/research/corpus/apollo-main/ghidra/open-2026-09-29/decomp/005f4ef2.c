
void Ins_MPS(int *param_1,int *param_2)

{
  int iVar1;
  
  if (*(int *)(*(int *)(*param_1 + 0x60) + 0x40) == 0x23) {
    iVar1 = (*(code *)param_1[0x95])();
    *param_2 = iVar1;
  }
  else {
    *param_2 = param_1[0x36];
  }
  return;
}

