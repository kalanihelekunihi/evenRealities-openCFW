
int FUN_00454f38(int param_1,uint param_2,undefined4 *param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  iVar2 = 0x38;
  FUN_00454d7c();
  if (*DAT_004551a0 <= param_2) {
    do {
      iVar2 = iVar2 + -1;
      iVar1 = FUN_004557b0(iVar3 * 0x24 + param_1,iVar2 * 0x14 + DAT_004551b0,1);
      iVar3 = iVar1 + iVar3;
    } while (iVar2 != 0);
    iVar2 = FUN_004557b0(iVar3 * 0x24 + param_1,*DAT_00455470,2);
    iVar1 = FUN_004557b0((iVar2 + iVar3) * 0x24 + param_1,*DAT_00455474,2);
    iVar1 = iVar1 + iVar2 + iVar3;
    iVar2 = FUN_004557b0(iVar1 * 0x24 + param_1,DAT_00455318,4);
    iVar2 = iVar2 + iVar1;
    iVar3 = FUN_004557b0(param_1 + iVar2 * 0x24,DAT_00455478,3);
    iVar3 = iVar3 + iVar2;
    if (param_3 != (undefined4 *)0x0) {
      *param_3 = 0;
    }
  }
  FUN_00454dcc();
  return iVar3;
}

