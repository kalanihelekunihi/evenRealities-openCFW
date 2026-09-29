
void FUN_005b8402(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_38 [32];
  undefined4 uStack_18;
  
  piVar1 = DAT_005b8864;
  if ((*DAT_005b8864 != 0) && (uStack_18 = param_4, iVar2 = FUN_0043e2ea(*DAT_005b8864), iVar2 != 0)
     ) {
    FUN_0043c0e4(auStack_38,0x20,0);
    iVar2 = DAT_005b8868;
    uVar3 = FUN_00460084(*(undefined4 *)(DAT_005b8868 + param_1 * 4));
    uVar3 = FUN_0045fffe(*(undefined4 *)(iVar2 + param_1 * 4),uVar3);
    FUN_004b4728(auStack_38,DAT_005b886c,uVar3,param_3);
    FUN_0049942e(*piVar1,auStack_38);
  }
  return;
}

