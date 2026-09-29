
int FUN_00514aec(int param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  piVar1 = DAT_00514d94;
  iVar3 = *DAT_00514d94;
  iVar2 = *(int *)(iVar3 + 4);
  if (iVar2 == 0) {
    FUN_004b127c(0x80);
    return 0;
  }
  *(uint *)(iVar2 + 0x18) = *(uint *)(iVar2 + 0x18) & 0xfffffff7;
  if ((int)((uint)*(byte *)(iVar2 + 0x18) << 0x1a) < 0) {
    iVar4 = *(int *)(iVar2 + 0x2c);
    iVar4 = iVar4 * (*(int *)(iVar2 + 0x14) / iVar4) + (iVar4 - *(int *)(iVar2 + 0x14));
  }
  else {
    iVar4 = *(int *)(iVar2 + 0x10) - *(int *)(iVar2 + 0x14);
  }
  if ((int)((uint)*(byte *)(iVar2 + 0x18) << 0x1a) < 0) {
    if (iVar4 / 2 < param_1 + 1) {
      *(undefined1 *)(iVar3 + 0xf9) = 0;
      FUN_005147b0(*(undefined4 *)(*piVar1 + 4));
    }
  }
  else if ((iVar4 / 2 + -2 < param_1) && (iVar2 = FUN_00514504(param_1), iVar2 < 0)) {
    return 0;
  }
  iVar2 = *(int *)(*piVar1 + 4);
  iVar3 = *(int *)(iVar2 + 0x14);
  *(int *)(iVar2 + 0x14) = iVar3 + param_1 * 2;
  return *(int *)(iVar2 + 8) + iVar3 * 4;
}

