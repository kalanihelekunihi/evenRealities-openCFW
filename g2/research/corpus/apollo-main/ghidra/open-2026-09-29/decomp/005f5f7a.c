
void Ins_INSTCTRL(int *param_1,int *param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = param_2[1];
  iVar1 = *param_2;
  if ((uVar2 == 0) || (3 < uVar2)) {
    if (*(char *)((int)param_1 + 0x235) != '\0') {
      param_1[3] = 0x86;
    }
  }
  else {
    iVar3 = 1 << (uVar2 + 0xff & 0xff);
    if ((iVar1 == 0) || (iVar1 == iVar3)) {
      *(byte *)(param_1 + 0x55) = *(byte *)(param_1 + 0x55) & ~(byte)iVar3;
      *(byte *)(param_1 + 0x55) = *(byte *)(param_1 + 0x55) | (byte)iVar1;
      if ((uVar2 == 3) && (*(int *)(*(int *)(*param_1 + 0x60) + 0x40) == 0x28)) {
        *(bool *)((int)param_1 + 0x267) = iVar1 != 4;
      }
    }
    else if (*(char *)((int)param_1 + 0x235) != '\0') {
      param_1[3] = 0x86;
    }
  }
  return;
}

