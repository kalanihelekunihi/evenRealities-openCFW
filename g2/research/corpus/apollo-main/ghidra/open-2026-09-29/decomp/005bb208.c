
void FUN_005bb208(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 local_5c;
  undefined4 local_58;
  undefined1 auStack_54 [64];
  undefined4 uStack_14;
  
  if ((param_1 < 3) && ((int)param_1 < (int)(uint)*DAT_005bbcd4)) {
    iVar3 = DAT_005bbcd8 + param_1 * 0x1c;
    uStack_14 = param_4;
    FUN_005bad98(*(undefined4 *)(DAT_005bbcdc + param_1 * 4),param_2,param_3,&local_58,&local_5c);
    if ((*(int *)(iVar3 + 4) != 0) && (iVar1 = FUN_0043e2ea(*(undefined4 *)(iVar3 + 4)), iVar1 == 1)
       ) {
      uVar2 = FUN_005bac8c(local_58);
      FUN_00498680(*(undefined4 *)(iVar3 + 4),uVar2);
    }
    if ((*(int *)(iVar3 + 8) != 0) && (iVar1 = FUN_0043e2ea(*(undefined4 *)(iVar3 + 8)), iVar1 == 1)
       ) {
      uVar2 = FUN_005bad10(local_5c);
      FUN_00498680(*(undefined4 *)(iVar3 + 8),uVar2);
    }
    if ((*(int *)(iVar3 + 0x14) != 0) &&
       (iVar1 = FUN_0043e2ea(*(undefined4 *)(iVar3 + 0x14)), iVar1 == 1)) {
      FUN_0043c0e4(auStack_54,0x40,0);
      if (*(int *)(iVar3 + 0x10) == 0) {
        iVar1 = DAT_005bbce0 + param_1 * 0x20;
      }
      else {
        iVar1 = 0;
      }
      FUN_005bae52(iVar1,local_58,local_5c,auStack_54,0x40);
      FUN_0049942e(*(undefined4 *)(iVar3 + 0x14),auStack_54);
    }
  }
  return;
}

