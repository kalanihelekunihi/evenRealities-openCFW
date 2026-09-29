
undefined2 DmSizeOfEvt(int param_1)

{
  undefined2 uVar1;
  
  if (*(byte *)(param_1 + 2) - 0x20 < 0x5c) {
    uVar1 = *(undefined2 *)(DAT_004d2afc + (uint)*(byte *)(param_1 + 2) * 2 + -0x40);
  }
  else {
    uVar1 = 4;
  }
  return uVar1;
}

