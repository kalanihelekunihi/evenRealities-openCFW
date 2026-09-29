
void FUN_0050c7a8(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int local_78;
  undefined4 local_74;
  undefined4 local_68;
  undefined4 local_58;
  undefined4 local_48;
  undefined4 uStack_18;
  
  iVar1 = DAT_0050c97c;
  if (*(int *)(DAT_0050c97c + 200) != 0) {
    *DAT_0050c960 = 2;
    *DAT_0050c964 = 0;
    uStack_18 = param_4;
    for (iVar3 = 0; iVar3 < 4; iVar3 = iVar3 + 1) {
      if (*(int *)(iVar1 + iVar3 * 0x30) == 0) {
        *(undefined4 *)(DAT_0050ca10 + iVar3 * 4) = 0;
      }
      else {
        uVar2 = FUN_0043fce0(*(undefined4 *)(iVar1 + iVar3 * 0x30));
        *(undefined4 *)(DAT_0050ca10 + iVar3 * 4) = uVar2;
      }
    }
    uVar2 = DAT_0050c864;
    if (param_1 < 1) {
      uVar2 = 0x120;
    }
    iVar3 = FUN_0050c476(0);
    if ((iVar3 != 0) && (*(int *)(iVar3 + 4) != 0)) {
      FUN_0044e368(*(undefined4 *)(iVar3 + 4),0);
    }
    FUN_004503d6(&local_78);
    local_78 = iVar1;
    FUN_004506ce(&local_78,0,uVar2);
    local_74 = DAT_0050ca14;
    local_58 = DAT_0050c9a0;
    local_68 = DAT_0050ca18;
    *DAT_0050ca1c = 1;
    local_48 = param_2;
    FUN_00450408(&local_78);
  }
  return;
}

