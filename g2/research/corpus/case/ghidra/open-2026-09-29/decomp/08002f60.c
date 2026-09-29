
void FUN_08002f60(int param_1)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = *DAT_08002f84;
  uVar3 = DAT_08002f84[1];
  uVar2 = 8;
  do {
    *(char *)(param_1 + uVar2 + -1) = (char)uVar1;
    uVar1 = uVar1 >> 8 | uVar3 << 0x18;
    uVar3 = uVar3 >> 8;
    uVar2 = uVar2 - 1 & 0xff;
  } while (uVar2 != 0);
  return;
}

