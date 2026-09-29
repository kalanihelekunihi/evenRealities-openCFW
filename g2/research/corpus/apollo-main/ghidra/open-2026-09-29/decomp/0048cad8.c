
void FUN_0048cad8(int param_1,undefined4 *param_2)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  uint uVar8;
  
  iVar2 = FUN_0044dce2(param_1,0);
  if (iVar2 == 0) {
    FUN_0048c80e(param_2,0x20);
  }
  else {
    FUN_0048cdec(param_1,param_2);
    FUN_0048cbf8(param_1,param_2);
    uVar3 = FUN_0048c860(param_1,0);
    uVar4 = FUN_0048c856(param_1,0);
    iVar2 = FUN_0048c8a8(param_1,0);
    iVar5 = FUN_0048c81a(param_1,0);
    iVar6 = FUN_0048c824(param_1,0);
    if (iVar5 == 0x3fffffff) {
      uVar8 = (*(ushort *)(param_1 + 0x2a) & 0xfff) >> 0xb ^ 1;
    }
    else {
      uVar8 = 0;
    }
    uVar7 = FUN_0043fe16(param_1);
    uVar1 = FUN_0048c9cc(param_1);
    uVar3 = FUN_0048d3c8(uVar7,uVar8,uVar1,uVar3,param_2[4],param_2[2],*param_2,iVar2 == 1);
    param_2[6] = uVar3;
    if (iVar6 == 0x3fffffff) {
      uVar8 = (*(ushort *)(param_1 + 0x2a) & 0x7ff) >> 10 ^ 1;
    }
    else {
      uVar8 = 0;
    }
    uVar3 = FUN_0043fe70(param_1);
    uVar1 = FUN_0048c9d6(param_1);
    uVar3 = FUN_0048d3c8(uVar3,uVar8,uVar1,uVar4,param_2[5],param_2[3],param_2[1],0);
    param_2[7] = uVar3;
  }
  return;
}

