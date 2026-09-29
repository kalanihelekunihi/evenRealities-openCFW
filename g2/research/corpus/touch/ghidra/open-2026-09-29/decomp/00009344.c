
void SlaveHandleHsMode(int param_1,int param_2)

{
  code *pcVar1;
  
  pcVar1 = *(code **)(param_2 + 0x4c);
  if (pcVar1 != (code *)0x0) {
    if (*(int *)(param_1 + 100) << 7 < 0) {
      (*pcVar1)(1);
      *(uint *)(param_1 + 0x60) = *(uint *)(param_1 + 0x60) | 0xb000;
      Cy_SCB_SetRxFifoLevel(param_1,8);
      *(uint *)(param_2 + 0x20) = *(uint *)(param_2 + 0x20) | 0x200;
      *(uint *)(param_1 + 0x6c) = *(uint *)(param_1 + 0x6c) & DAT_000093bc;
      *(undefined4 *)(param_1 + 0xf40) = 0x1000000;
    }
    else {
      (*pcVar1)(2);
      *(uint *)(param_1 + 0x60) = *(uint *)(param_1 + 0x60) & DAT_000093c0;
      *(uint *)(param_1 + 0x6c) = *(uint *)(param_1 + 0x6c) | 0x100;
      *(undefined4 *)(param_1 + 0xf40) = 0x2000000;
    }
  }
  *(undefined4 *)(param_1 + 0xf40) = 0x3000000;
  return;
}

