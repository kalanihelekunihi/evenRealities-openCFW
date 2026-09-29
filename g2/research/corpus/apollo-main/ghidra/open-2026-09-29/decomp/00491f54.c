
int FUN_00491f54(int param_1,undefined1 *param_2,ushort *param_3)

{
  ushort uVar1;
  undefined2 uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  FUN_0049172c(0);
  if ((char)param_3[1] == '\0') {
    uVar1 = *(ushort *)(param_1 + 0xe);
    *(ushort *)(param_1 + 0xe) = uVar1 + 1;
    uVar5 = uVar1 & 0x7fff;
    if (*(char *)(param_1 + 0xc) != '\0') {
      uVar5 = uVar5 | 0x8000;
    }
  }
  else {
    uVar5 = (uint)*param_3;
  }
  *param_3 = (ushort)uVar5;
  uVar2 = FUN_0049172c();
  *param_2 = 1;
  iVar4 = 1;
  uVar2 = FUN_00491730(uVar2,1);
  for (uVar6 = 1; -1 < (char)uVar6; uVar6 = uVar6 - 1) {
    uVar3 = (int)uVar5 >> ((uVar6 & 0x1f) << 3);
    param_2[iVar4] = (char)uVar3;
    iVar4 = iVar4 + 1;
    uVar2 = FUN_00491730(uVar2,uVar3 & 0xff);
  }
  for (uVar5 = 1; -1 < (char)uVar5; uVar5 = uVar5 - 1) {
    uVar6 = (int)(uint)param_3[6] >> ((uVar5 & 0x1f) << 3);
    param_2[iVar4] = (char)uVar6;
    iVar4 = iVar4 + 1;
    uVar2 = FUN_00491730(uVar2,uVar6 & 0xff);
  }
  for (uVar5 = 1; -1 < (char)uVar5; uVar5 = uVar5 - 1) {
    uVar6 = (int)(uint)param_3[2] >> ((uVar5 & 0x1f) << 3);
    param_2[iVar4] = (char)uVar6;
    iVar4 = iVar4 + 1;
    uVar2 = FUN_00491730(uVar2,uVar6 & 0xff);
  }
  uVar5 = FUN_0049174e(uVar2);
  for (uVar6 = 1; -1 < (char)uVar6; uVar6 = uVar6 - 1) {
    param_2[iVar4] = (char)((int)(uVar5 & 0xffff) >> ((uVar6 & 0x1f) << 3));
    iVar4 = iVar4 + 1;
  }
  return iVar4;
}

