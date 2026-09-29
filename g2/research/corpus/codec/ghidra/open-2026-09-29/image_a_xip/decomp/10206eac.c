
int gx8002_logfbank_index(int *param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  
  iVar2 = *param_1;
  uVar1 = *(int *)(iVar2 + 0x24) * param_2;
  return *(int *)(iVar2 + 0x70) +
         (uVar1 - *(uint *)(iVar2 + 0x30) * (uVar1 / *(uint *)(iVar2 + 0x30))) *
         *(int *)(iVar2 + 0x6c) * 2;
}

