
void FUN_00515148(int *param_1)

{
  int iVar1;
  byte bVar2;
  undefined4 uVar3;
  int iVar4;
  undefined2 uVar5;
  undefined2 uVar6;
  undefined1 uVar7;
  undefined4 uVar8;
  
  switch(*(undefined1 *)((int)param_1 + 0xd5)) {
  case 1:
  case 4:
    bVar2 = *(byte *)(param_1 + 0x33) | 1;
    uVar8 = 0;
    uVar7 = 1;
    uVar6 = 1;
    uVar5 = 0x40;
    uVar3 = *(undefined4 *)(param_1[0xc] + 0xc);
    break;
  case 2:
    iVar1 = *param_1;
    if (iVar1 != 0) {
      if ((char)param_1[0xb] == '\0') {
        bVar2 = *(byte *)(iVar1 + 0x1d);
        uVar8 = *(undefined4 *)(iVar1 + 0x14);
        uVar7 = *(undefined1 *)(iVar1 + 0x1c);
        uVar6 = *(undefined2 *)(iVar1 + 0x12);
        uVar5 = *(undefined2 *)(iVar1 + 0x10);
        uVar3 = *(undefined4 *)(iVar1 + 0xc);
        break;
      }
      iVar4 = param_1[1];
      if (iVar4 != 0) {
        FUN_004b1794(*(undefined4 *)(iVar1 + 0xc),*(undefined2 *)(iVar1 + 0x10),
                     *(undefined2 *)(iVar1 + 0x12),*(undefined1 *)(iVar1 + 0x1c),
                     *(undefined4 *)(iVar1 + 0x14),*(undefined1 *)(iVar1 + 0x1d),
                     *(undefined4 *)(iVar4 + 0xc),*(undefined1 *)(iVar4 + 0x1c));
        return;
      }
    }
    FUN_0051565c(2);
    return;
  case 3:
    iVar1 = FUN_0052261a();
    if (-1 < iVar1 << 0x17) {
      FUN_0051565c(0x20);
      *(undefined1 *)((int)param_1 + 0xd5) = 0;
      return;
    }
    uVar5 = 1;
    bVar2 = *(byte *)(param_1 + 0x33) | 0x81;
    uVar8 = 4;
    uVar7 = 1;
    uVar6 = 0x40;
    uVar3 = *(undefined4 *)(param_1[0xc] + 0xc);
    break;
  default:
    return;
  }
  FUN_004b1298(1,uVar3,uVar5,uVar6,uVar7,uVar8,bVar2);
  return;
}

