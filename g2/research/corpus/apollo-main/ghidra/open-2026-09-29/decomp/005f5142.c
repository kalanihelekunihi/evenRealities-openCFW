
void Ins_RCVT(int param_1,uint *param_2)

{
  uint uVar1;
  
  if (*param_2 < *(uint *)(param_1 + 0x180)) {
    uVar1 = (**(code **)(param_1 + 600))();
    *param_2 = uVar1;
  }
  else if (*(char *)(param_1 + 0x235) == '\0') {
    *param_2 = 0;
  }
  else {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  return;
}

