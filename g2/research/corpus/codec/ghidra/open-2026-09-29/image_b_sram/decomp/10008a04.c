
int FUN_10008a04(uint param_1,undefined4 param_2,int param_3,undefined4 param_4,int param_5,
                uint param_6,uint param_7,uint param_8)

{
  int iVar1;
  undefined1 *puVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  iVar4 = param_3;
  if (((param_8 & 3) == 0) && (param_6 < param_7)) {
    iVar1 = param_3;
    do {
      iVar4 = iVar1 + 1;
      (*(code *)(param_1 & 0xfffffffe))(0x20,param_2,iVar1,param_4);
      iVar1 = iVar4;
    } while (iVar4 != (param_7 - param_6) + param_3);
  }
  if (param_6 != 0) {
    puVar2 = (undefined1 *)(param_5 + (param_6 - 1));
    iVar5 = param_6 + iVar4;
    iVar1 = iVar4;
    do {
      iVar6 = iVar1 + 1;
      (*(code *)(param_1 & 0xfffffffe))(*puVar2,param_2,iVar1,param_4);
      puVar2 = puVar2 + -1;
      iVar1 = iVar6;
      iVar4 = iVar5;
    } while (iVar6 != iVar5);
  }
  if ((param_8 & 2) != 0) {
    uVar3 = iVar4 - param_3;
    while (uVar3 < param_7) {
      (*(code *)(param_1 & 0xfffffffe))(0x20,param_2,iVar4,param_4);
      uVar3 = (iVar4 + 1) - param_3;
      iVar4 = iVar4 + 1;
    }
  }
  return iVar4;
}

