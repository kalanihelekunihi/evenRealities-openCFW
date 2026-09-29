
void touch_sub_2bcc(int param_1,int param_2,int param_3)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  uint *puVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  iVar7 = *(int *)(param_3 + 0xc) + param_1 * 0x90;
  iVar6 = *(int *)(iVar7 + 4);
  iVar4 = *(int *)(param_3 + 0x28) + 0x10;
  if (*(char *)(iVar7 + 0x7b) == '\a') {
    iVar4 = *(int *)(param_3 + 0x2c) + 0x24;
    iVar8 = 0xb;
  }
  else {
    iVar8 = 7;
  }
  puVar5 = (uint *)(iVar4 + iVar8 * (uint)*(ushort *)(iVar7 + 0x80) * 4);
  uVar1 = (uint)*(ushort *)(iVar7 + 0x38);
  while (uVar1 != 0) {
    uVar2 = *puVar5;
    uVar3 = DAT_00005f30 & uVar2;
    *puVar5 = uVar3;
    if (param_2 == 1) {
      *puVar5 = uVar2 | 0xff00;
    }
    else if (param_2 == 2) {
      *puVar5 = uVar3 | (uint)*(byte *)(iVar6 + 9) << 8;
    }
    puVar5 = puVar5 + iVar8;
    iVar6 = iVar6 + 10;
    uVar1 = uVar1 - 1;
  }
  return;
}

