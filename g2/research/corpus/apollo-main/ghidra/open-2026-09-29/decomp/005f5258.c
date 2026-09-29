
void Ins_SLOOP(int param_1,int *param_2)

{
  int iVar1;
  
  if (*param_2 < 0) {
    *(undefined4 *)(param_1 + 0xc) = 0x84;
  }
  else {
    if (*param_2 < 0x10000) {
      iVar1 = *param_2;
    }
    else {
      iVar1 = 0xffff;
    }
    *(int *)(param_1 + 0x134) = iVar1;
  }
  return;
}

