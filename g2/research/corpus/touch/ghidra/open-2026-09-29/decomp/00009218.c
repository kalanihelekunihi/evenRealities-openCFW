
void Cy_SCB_ReadArrayNoCheck(int param_1,int param_2,uint param_3)

{
  uint uVar1;
  
  uVar1 = *(uint *)(param_1 + 0x300) & 0x18;
  if ((*(uint *)(param_1 + 0x300) & 0x18) == 0) {
    for (; uVar1 < param_3; uVar1 = uVar1 + 1) {
      *(char *)(param_2 + uVar1) = (char)*(undefined4 *)(param_1 + 0x340);
    }
  }
  else {
    for (uVar1 = 0; uVar1 < param_3; uVar1 = uVar1 + 1) {
      *(short *)(param_2 + uVar1 * 2) = (short)*(undefined4 *)(param_1 + 0x340);
    }
  }
  return;
}

