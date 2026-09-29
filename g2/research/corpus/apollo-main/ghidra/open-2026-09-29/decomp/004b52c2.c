
void attcProcFindOrReadRsp(int param_1,ushort param_2,int param_3,int param_4)

{
  byte *pbVar1;
  uint uVar2;
  ushort uVar3;
  byte *pbVar4;
  ushort uVar5;
  ushort uVar6;
  byte *pbVar7;
  
  pbVar4 = (byte *)(param_3 + 9);
  pbVar1 = (byte *)((uint)param_2 + param_3 + 8);
  if (*(char *)(param_1 + 6) == '\x02') {
    if (*pbVar4 == 1) {
      uVar2 = 2;
    }
    else {
      uVar2 = 0x10;
    }
  }
  else if (*(char *)(param_1 + 6) == '\x04') {
    uVar2 = *pbVar4 - 2;
  }
  else {
    uVar2 = *pbVar4 - 4;
  }
  pbVar4 = (byte *)(param_3 + 10);
  uVar3 = *(ushort *)(param_1 + 0x12);
  do {
    if (pbVar1 <= pbVar4) goto LAB_004b53ac;
    uVar5 = (ushort)pbVar4[1] * 0x100 + (ushort)*pbVar4;
    pbVar7 = pbVar4 + 2;
    if ((((uVar5 == 0) || (uVar3 == 0)) || (uVar5 < uVar3)) || (*(ushort *)(param_1 + 0x14) < uVar5)
       ) {
      *(undefined1 *)(param_4 + 3) = 0x73;
      goto LAB_004b53ac;
    }
    uVar6 = uVar5;
    if (*(char *)(param_1 + 6) == '\b') {
      uVar6 = (ushort)pbVar4[3] * 0x100 + (ushort)*pbVar7;
      pbVar7 = pbVar4 + 4;
      if (((uVar6 == 0) || (uVar6 < uVar5)) ||
         ((uVar6 < uVar3 || (*(ushort *)(param_1 + 0x14) < uVar6)))) {
        *(undefined1 *)(param_4 + 3) = 0x73;
        goto LAB_004b53ac;
      }
    }
    if (uVar6 == 0xffff) {
      uVar3 = 0;
    }
    else {
      uVar3 = uVar6 + 1;
    }
    pbVar4 = pbVar7 + (uVar2 & 0xff);
  } while (pbVar4 <= pbVar1);
  *(undefined1 *)(param_4 + 3) = 0x73;
LAB_004b53ac:
  if ((*(char *)(param_4 + 3) == '\0') && (*(char *)(param_1 + 7) == '\x01')) {
    if ((uVar3 == 0) || ((uint)uVar3 == *(ushort *)(param_1 + 0x14) + 1)) {
      *(undefined1 *)(param_1 + 7) = 0;
    }
    else {
      *(ushort *)(param_1 + 0x12) = uVar3;
      *(ushort *)(param_1 + 0xc) = uVar3;
    }
  }
  return;
}

