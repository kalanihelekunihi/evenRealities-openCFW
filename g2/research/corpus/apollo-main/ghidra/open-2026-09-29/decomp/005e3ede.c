
undefined8 smprScActPkCalcCb(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  
  FUN_0053634e(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10,0x10,param_3,param_4,param_2,param_3
               ,param_4);
  smpLogByteArray(PTR_s_Rand_Nb_005e4214,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10,0x10);
  *(undefined1 *)(param_1 + 0x3f) = 4;
  bVar1 = smpGetPkBit(param_1);
  iVar3 = *(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10;
  uVar2 = (uint)bVar1;
  SmpScCalcF4(param_1,param_2,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0xc),
              *(undefined4 *)(*(int *)(param_1 + 0x48) + 8));
  return CONCAT44(iVar3,uVar2);
}

