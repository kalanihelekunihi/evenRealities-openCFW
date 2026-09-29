
void Cy_SCB_WriteArrayNoCheck(int param_1,int param_2,uint param_3)

{
  uint uVar1;
  
  uVar1 = *(uint *)(param_1 + 0x200) & 0x18;
  if ((*(uint *)(param_1 + 0x200) & 0x18) == 0) {
    for (; uVar1 < param_3; uVar1 = uVar1 + 1) {
      *(uint *)(param_1 + 0x240) = (uint)*(byte *)(param_2 + uVar1);
    }
  }
  else {
    for (uVar1 = 0; uVar1 < param_3; uVar1 = uVar1 + 1) {
      *(uint *)(param_1 + 0x240) = (uint)*(ushort *)(uVar1 * 2 + param_2);
    }
  }
  return;
}

