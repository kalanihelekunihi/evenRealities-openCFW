
void touch_state_2568_reset_object(int param_1,int param_2)

{
  byte bVar1;
  ushort uVar2;
  uint uVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  
  piVar5 = (int *)(*(int *)(param_2 + 0xc) + param_1 * 0x90);
  iVar6 = *piVar5;
  iVar4 = piVar5[1];
  uVar2 = *(ushort *)(piVar5 + 0xe);
  if (*(char *)((int)piVar5 + 0x7b) == '\a') {
    return;
  }
  *(byte *)(iVar6 + 0x23) = *(byte *)(iVar6 + 0x23) & 0xfe;
  uVar3 = (uint)uVar2;
  while (uVar3 != 0) {
    *(byte *)(iVar4 + 6) = *(byte *)(iVar4 + 6) & 0xfc;
    iVar4 = iVar4 + 10;
    uVar3 = uVar3 - 1;
  }
  bVar1 = *(byte *)((int)piVar5 + 0x7b);
  if (bVar1 != 5) {
    if (5 < bVar1) {
      if (bVar1 == 6) {
        memset(piVar5[10],*(undefined1 *)(iVar6 + 0x20),(uint)uVar2 << 1);
      }
      goto LAB_000058bc;
    }
    if (1 < (byte)(bVar1 - 2)) goto LAB_000058bc;
  }
  if (*(char *)((int)piVar5 + 0x7a) == '\x01') {
    *(undefined1 *)piVar5[10] = *(undefined1 *)(iVar6 + 0x20);
  }
LAB_000058bc:
  if ((*(byte *)((int)piVar5 + 0x7b) - 2 < 4) &&
     (*(undefined1 *)(iVar6 + 0x28) = 0, (piVar5[0x1c] & 0xffU) != 0)) {
    *(undefined1 *)(piVar5[0xf] + 4) = 0;
  }
  return;
}

