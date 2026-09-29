
void touch_state_28c0_cap_object(int param_1,int param_2)

{
  int *piVar1;
  uint uVar2;
  ushort *puVar3;
  ushort uVar4;
  
  piVar1 = (int *)(*(int *)(param_2 + 0xc) + param_1 * 0x90);
  puVar3 = (ushort *)piVar1[1];
  uVar4 = *(ushort *)(*piVar1 + 4);
  for (uVar2 = 0; uVar2 < *(ushort *)(piVar1 + 0xe); uVar2 = uVar2 + 1) {
    if ((*(char *)((int)piVar1 + 0x7a) == '\x01') && (*(byte *)((int)piVar1 + 0x3a) <= uVar2)) {
      uVar4 = *(ushort *)(*piVar1 + 6);
    }
    if (uVar4 < *puVar3) {
      *puVar3 = uVar4;
    }
    puVar3 = puVar3 + 5;
  }
  return;
}

