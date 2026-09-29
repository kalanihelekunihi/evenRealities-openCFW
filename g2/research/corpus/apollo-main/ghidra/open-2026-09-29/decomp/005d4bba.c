
void FUN_005d4bba(int param_1,undefined4 param_2,undefined4 param_3,int *param_4,char *param_5,
                 int param_6)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined1 local_3c [4];
  int local_38;
  int local_34;
  undefined4 local_30;
  undefined4 local_2c;
  int *piStack_28;
  
  piStack_28 = param_4;
  uVar1 = FUN_005d6e44(param_2);
  if (((*(char *)(param_1 + 8) == '\0') && ((uVar1 & 1) != 0)) && (*param_5 == '\0')) {
    iVar2 = FUN_005d6f38(param_2,0);
    iVar3 = FUN_005d3500(*(undefined4 *)(param_1 + 0xb0));
    *param_4 = iVar3 + iVar2;
  }
  if (*(char *)(*(int *)(param_1 + 0xb0) + 0x224) == '\0') {
    if ((uVar1 & 1) == 0) {
      uVar4 = 0;
    }
    else {
      uVar4 = 1;
    }
    for (; uVar4 < uVar1; uVar4 = uVar4 + 2) {
      iVar2 = FUN_005d6f38(param_2,uVar4);
      local_38 = iVar2 + param_6;
      iVar3 = FUN_005d6f38(param_2,uVar4 + 1);
      param_6 = iVar3 + iVar2 + param_6;
      local_3c[0] = 0;
      local_30 = 0;
      local_2c = 0;
      local_34 = param_6;
      FUN_005d23da(param_3,local_3c);
    }
    FUN_005d709c(param_2);
  }
  *param_5 = '\x01';
  return;
}

