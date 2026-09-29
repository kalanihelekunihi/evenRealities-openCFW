
void FUN_004d00d0(int param_1,int param_2,uint param_3,uint param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = *(int *)(param_3 * 0x80 + param_1 + param_4 * 4 + 0x74);
  if (iVar3 == 0) {
    FUN_004d09b4(DAT_004d0860,DAT_004d06ac,0x261);
  }
  if (param_2 == 0) {
    FUN_004d09b4(DAT_004d0864,DAT_004d06ac,0x262);
  }
  *(int *)(param_2 + 8) = iVar3;
  *(int *)(param_2 + 0xc) = param_1;
  *(int *)(iVar3 + 0xc) = param_2;
  iVar3 = FUN_004cfe10(param_2);
  uVar1 = FUN_004cfe10(param_2);
  iVar2 = FUN_004cff18(uVar1,4);
  if (iVar3 != iVar2) {
    FUN_004d09b4(DAT_004d0950,DAT_004d06ac,0x268);
  }
  *(int *)(param_3 * 0x80 + param_1 + param_4 * 4 + 0x74) = param_2;
  *(uint *)(param_1 + 0x10) = *(uint *)(param_1 + 0x10) | 1 << (param_3 & 0xff);
  *(uint *)(param_1 + param_3 * 4 + 0x14) =
       1 << (param_4 & 0xff) | *(uint *)(param_1 + param_3 * 4 + 0x14);
  return;
}

