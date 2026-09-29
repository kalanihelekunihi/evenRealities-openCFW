
void touch_sub_2e70(uint param_1,int param_2)

{
  uint uVar1;
  uint uVar2;
  uint *puVar3;
  ushort *puVar4;
  ushort uVar5;
  
  uVar5 = *(ushort *)(*(int *)(param_2 + 0x10) + param_1 * 0x3c + 0x36);
  if (uVar5 != 0) {
    uVar5 = uVar5 - 1;
  }
  if (*(char *)(*(int *)(param_2 + 0xc) + param_1 * 0x90 + 0x7b) == '\a') {
    puVar4 = *(ushort **)(param_2 + 0x34);
    puVar3 = (uint *)(*(int *)(param_2 + 0x2c) + 0x20);
    for (uVar2 = 0; uVar2 < 4; uVar2 = uVar2 + 1) {
      if (*puVar4 == param_1) {
        uVar1 = *puVar3 & DAT_000061ec;
        *puVar3 = uVar1;
        *puVar3 = uVar1 | (uint)uVar5 << 0x10;
      }
      puVar4 = puVar4 + 2;
      puVar3 = puVar3 + 0xb;
    }
  }
  else {
    puVar4 = *(ushort **)(param_2 + 0x30);
    puVar3 = (uint *)(*(int *)(param_2 + 0x28) + 0xc);
    for (uVar2 = 0; uVar2 < 5; uVar2 = uVar2 + 1) {
      if (*puVar4 == param_1) {
        uVar1 = *puVar3 & DAT_000061ec;
        *puVar3 = uVar1;
        *puVar3 = uVar1 | (uint)uVar5 << 0x10;
      }
      puVar4 = puVar4 + 2;
      puVar3 = puVar3 + 7;
    }
  }
  return;
}

