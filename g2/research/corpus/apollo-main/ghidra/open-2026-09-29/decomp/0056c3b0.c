
void attcProcFindByTypeRsp(int param_1,ushort param_2,int param_3,int param_4)

{
  byte *pbVar1;
  ushort uVar2;
  byte *pbVar3;
  ushort uVar4;
  ushort uVar5;
  
  pbVar3 = (byte *)(param_3 + 9);
  pbVar1 = (byte *)((uint)param_2 + param_3 + 8);
  uVar2 = *(ushort *)(param_1 + 0x12);
  do {
    if (pbVar1 <= pbVar3) goto LAB_0056c428;
    uVar4 = (ushort)pbVar3[1] * 0x100 + (ushort)*pbVar3;
    uVar5 = (ushort)pbVar3[3] * 0x100 + (ushort)pbVar3[2];
    pbVar3 = pbVar3 + 4;
    if ((((uVar5 < uVar4) || (uVar4 < uVar2)) || (*(ushort *)(param_1 + 0x14) < uVar4)) ||
       (uVar2 == 0)) {
      *(undefined1 *)(param_4 + 3) = 0x73;
      goto LAB_0056c428;
    }
    if (uVar5 == 0xffff) {
      uVar2 = 0;
    }
    else {
      uVar2 = uVar5 + 1;
    }
  } while (pbVar3 <= pbVar1);
  *(undefined1 *)(param_4 + 3) = 0x73;
LAB_0056c428:
  if ((*(char *)(param_4 + 3) == '\0') && (*(char *)(param_1 + 7) == '\x01')) {
    if ((uVar2 == 0) || (*(ushort *)(param_1 + 0x14) < uVar2)) {
      *(undefined1 *)(param_1 + 7) = 0;
    }
    else {
      *(ushort *)(param_1 + 0x12) = uVar2;
      *(ushort *)(param_1 + 0xc) = uVar2;
    }
  }
  return;
}

