
void FUN_00489a8c(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 *puVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  if (param_1 != 0) {
    iVar2 = FUN_00454768(param_1);
    puVar1 = DAT_00489eb0;
    uVar3 = (*(code *)*DAT_00489eb0)(param_1,param_2);
    iVar4 = (*(code *)*puVar1)(param_1 + uVar3,param_3);
    for (; uVar3 <= (uint)(iVar2 - iVar4); uVar3 = uVar3 + 1) {
      *(undefined1 *)(param_1 + uVar3) = *(undefined1 *)(param_1 + iVar4 + uVar3);
    }
  }
  return;
}

