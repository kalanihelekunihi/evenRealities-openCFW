
undefined4 FUN_004b26a4(int param_1,int param_2,int param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  bool bVar7;
  
  bVar7 = param_3 == 9;
  if (bVar7) {
    param_3 = 0x20;
  }
  iVar6 = *(int *)(param_1 + 0x18);
  iVar2 = FUN_004b2774(param_1,param_3);
  if (iVar2 == 0) {
    uVar3 = 0;
  }
  else {
    cVar1 = '\0';
    if ((*(int *)(iVar6 + 0xc) != 0) && (iVar4 = FUN_004b2774(param_1,param_4), iVar4 != 0)) {
      cVar1 = FUN_004b28ee(param_1,iVar2,iVar4);
    }
    iVar5 = iVar2 * 0x10 + *(int *)(iVar6 + 4);
    iVar4 = *(int *)(iVar5 + 4);
    if (bVar7) {
      iVar4 = iVar4 << 1;
    }
    *(short *)(param_2 + 4) =
         (short)(((int)((uint)*(ushort *)(iVar6 + 0x10) * (int)cVar1) >> 4) + iVar4 + 8U >> 4);
    *(undefined2 *)(param_2 + 8) = *(undefined2 *)(iVar5 + 10);
    *(undefined2 *)(param_2 + 6) = *(undefined2 *)(iVar5 + 8);
    *(undefined2 *)(param_2 + 10) = *(undefined2 *)(iVar5 + 0xc);
    *(undefined2 *)(param_2 + 0xc) = *(undefined2 *)(iVar5 + 0xe);
    *(byte *)(param_2 + 0xe) = (byte)((ushort)*(undefined2 *)(iVar6 + 0x12) >> 9) & 0xf;
    if (*(ushort *)(iVar6 + 0x12) >> 0xe == 3) {
      *(char *)(param_2 + 0xe) = *(char *)(param_2 + 0xe) + '\x10';
    }
    *(byte *)(param_2 + 0xf) = *(byte *)(param_2 + 0xf) & 0xfe;
    *(int *)(param_2 + 0x18) = iVar2;
    if (bVar7) {
      *(short *)(param_2 + 6) = *(short *)(param_2 + 6) << 1;
    }
    uVar3 = 1;
  }
  return uVar3;
}

