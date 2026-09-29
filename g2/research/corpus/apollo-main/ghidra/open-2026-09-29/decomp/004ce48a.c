
int FUN_004ce48a(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_38 [32];
  undefined4 uStack_18;
  undefined4 local_14;
  
  uStack_18 = param_1;
  local_14 = param_2;
  iVar2 = FUN_004cc04a(param_1,auStack_38,&local_14,0);
  if (-1 < iVar2) {
    iVar3 = FUN_00481818(local_14,0x2f);
    if ((iVar3 == 0) || (iVar3 = FUN_004cae98(iVar2), iVar3 == 2)) {
      uVar1 = FUN_004caeb0(iVar2);
      iVar2 = FUN_004cbf38(param_1,auStack_38,uVar1,param_3);
    }
    else {
      iVar2 = -0x14;
    }
  }
  return iVar2;
}

