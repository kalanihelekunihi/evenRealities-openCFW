
void FUN_00006a80(int *param_1)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = **(int **)(*param_1 + 8);
  touch_sub_355c();
  *(undefined4 *)(iVar3 + 0x400) = 0;
  for (uVar1 = 0; uVar1 < 3; uVar1 = uVar1 + 1) {
    iVar2 = iVar3 + uVar1 * 0x40;
    *(undefined4 *)(iVar2 + 0x608) = 0x3000000;
    *(undefined4 *)(iVar2 + DAT_00006ab8) = DAT_00006abc;
  }
  return;
}

