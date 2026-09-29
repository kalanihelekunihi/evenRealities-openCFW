
void FUN_08002f88(int param_1)

{
  uint *puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = DAT_08002fc4;
  uVar2 = *DAT_08002fc4;
  uVar4 = DAT_08002fc4[1];
  uVar3 = 8;
  do {
    *(char *)(param_1 + uVar3 + -1) = (char)uVar2;
    uVar2 = uVar2 >> 8 | uVar4 << 0x18;
    uVar4 = uVar4 >> 8;
    uVar3 = uVar3 - 1 & 0xff;
  } while (uVar3 != 0);
  uVar2 = puVar1[2];
  uVar4 = puVar1[3];
  uVar3 = 8;
  do {
    *(char *)(param_1 + uVar3 + 7) = (char)uVar2;
    uVar2 = uVar2 >> 8 | uVar4 << 0x18;
    uVar4 = uVar4 >> 8;
    uVar3 = uVar3 - 1 & 0xff;
  } while (uVar3 != 0);
  return;
}

