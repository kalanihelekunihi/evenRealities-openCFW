
void FUN_0059a910(undefined4 param_1,undefined4 *param_2)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  
  FUN_005990cc(param_1,*param_2,5);
  FUN_005990cc(param_1,param_2[1],5);
  iVar5 = param_2[2];
  FUN_005990cc(param_1,iVar5 >> 1,1);
  bVar1 = *(byte *)(param_2 + 2);
  uVar2 = param_2[3];
  iVar3 = (int)uVar2 >> (bVar1 & 1);
  if (iVar5 >> 1 == 0) {
    if ((bVar1 & 1) == 0) {
      uVar2 = (uint)*(byte *)((int)param_2 + 0x19) + (param_2[5] + 1) * 2;
    }
    else {
      uVar2 = uVar2 & 1;
    }
    iVar5 = DAT_0059a9c4 * uVar2 + param_2[4];
    FUN_005990cc(param_1,iVar3,1);
    FUN_005990cc(param_1,*(undefined1 *)(param_2 + 6),1);
    uVar4 = 0x19;
  }
  else {
    iVar5 = param_2[4];
    if ((bVar1 & 1) != 0) {
      iVar5 = (uVar2 & 1) + iVar5 * 2 + 0xe74c00;
    }
    FUN_005990cc(param_1,iVar3,2);
    FUN_005990cc(param_1,*(undefined1 *)(param_2 + 6),1);
    uVar4 = 0x18;
  }
  FUN_005990cc(param_1,iVar5,uVar4);
  return;
}

