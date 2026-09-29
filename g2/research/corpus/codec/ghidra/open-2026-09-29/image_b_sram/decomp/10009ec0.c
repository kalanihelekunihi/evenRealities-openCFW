
int gx8002_mic_frame(int *param_1,int param_2,int param_3)

{
  int iVar1;
  
  iVar1 = *param_1;
  return *(int *)(iVar1 + 0x50) +
         (param_3 + param_2 * *(int *)(iVar1 + 0x28) +
         (param_1[2] - ((uint)param_1[2] / *(uint *)(iVar1 + 0x3c)) * *(uint *)(iVar1 + 0x3c)) *
         *(int *)(iVar1 + 0x24)) *
         ((uint)(*(int *)(iVar1 + 0x20) * *(int *)(iVar1 + 0x1c)) / 1000) * 2;
}

