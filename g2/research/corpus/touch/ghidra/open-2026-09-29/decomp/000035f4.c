
void sensor_read_mux(int param_1,int param_2)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  iVar3 = *(int *)(DAT_0000361c + 0xc) + param_1 * 0x90;
  iVar2 = *(int *)(iVar3 + 4);
  uVar1 = *(ushort *)(iVar3 + 0x38);
  for (uVar4 = 0; uVar4 < uVar1; uVar4 = uVar4 + 1) {
    *(undefined2 *)(param_2 + uVar4 * 2) = *(undefined2 *)(iVar2 + 4);
    iVar2 = iVar2 + 10;
  }
  return;
}

