
undefined8
FUN_005d21e4(int param_1,int param_2,undefined4 param_3,undefined4 param_4,byte param_5,
            undefined1 param_6,undefined4 param_7,undefined4 param_8)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar3 = *(int *)(param_2 + 0x2a4);
  FUN_0043c0e4(param_1,0x308,0,param_4,param_1);
  uVar1 = (uint)param_5;
  FUN_005d1512(param_1,param_2,param_3,param_4);
  *(int *)(param_1 + 0x6c) = iVar3;
  *(undefined4 *)(param_1 + 0x2dc) = *(undefined4 *)(iVar3 + 0x78);
  *(undefined4 *)(param_1 + 0x2ec) = *(undefined4 *)(iVar3 + 0x548);
  uVar2 = FUN_005d2170(*(undefined4 *)(iVar3 + 0x588),*(undefined4 *)(param_1 + 0x2dc));
  *(undefined4 *)(param_1 + 0x2e4) = uVar2;
  *(undefined1 *)(param_1 + 0x2f8) = param_6;
  *(undefined4 *)(param_1 + 0x300) = param_7;
  *(undefined4 *)(param_1 + 0x304) = param_8;
  return CONCAT44(param_2,uVar1);
}

