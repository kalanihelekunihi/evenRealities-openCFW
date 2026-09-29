
undefined8 FUN_004920aa(int param_1,int param_2,int param_3,uint param_4,ushort param_5)

{
  undefined2 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 local_18;
  
  iVar2 = FUN_004916c8(param_1);
  local_18 = param_4;
  if (iVar2 == 0) {
    uVar3 = 0;
  }
  else {
    uVar3 = FUN_00491f54(param_1,param_1 + 0x6021,param_2);
    *(undefined4 *)(param_1 + 0x6424) = uVar3;
    *(uint *)(param_1 + 0x6428) = (uint)*(ushort *)(param_2 + 0xc);
    if (param_3 != 0) {
      local_18 = (uint)param_5;
      iVar2 = FUN_004918c2(param_1,param_2,param_3,param_4);
      if (iVar2 == 0) {
        FUN_00491722(param_1);
        uVar3 = 0;
        goto LAB_00492112;
      }
    }
    uVar1 = FUN_0049172c();
    *(undefined2 *)(param_1 + 0x642c) = uVar1;
    uVar3 = 1;
  }
LAB_00492112:
  return CONCAT44(local_18,uVar3);
}

