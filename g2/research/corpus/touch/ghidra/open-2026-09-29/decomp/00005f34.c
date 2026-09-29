
void touch_sub_2c34(int param_1,undefined4 param_2,int param_3)

{
  uint uVar1;
  ushort *puVar2;
  int iVar3;
  uint uVar4;
  
  iVar3 = *(int *)(param_3 + 0xc) + param_1 * 0x90;
  puVar2 = *(ushort **)(iVar3 + 4);
  uVar1 = 0xffffffff;
  uVar4 = (uint)*(ushort *)(iVar3 + 0x38);
  while (uVar4 != 0) {
    if (*puVar2 < uVar1) {
      uVar1 = (uint)*puVar2;
    }
    puVar2 = puVar2 + 5;
    uVar4 = uVar4 - 1;
  }
  return;
}

