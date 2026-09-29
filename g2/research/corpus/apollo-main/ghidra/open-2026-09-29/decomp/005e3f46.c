
undefined8 smprScActPkCalcCa(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  uint uVar2;
  undefined4 uVar3;
  
  WStrReverseCpy(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14),*(int *)(param_2 + 4) + 9,0x10,
                 param_4,param_2,param_3,param_4);
  bVar1 = smpGetPkBit(param_1);
  uVar3 = *(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14);
  uVar2 = (uint)bVar1;
  SmpScCalcF4(param_1,param_2,*(undefined4 *)(*(int *)(param_1 + 0x48) + 8),
              *(undefined4 *)(*(int *)(param_1 + 0x48) + 0xc));
  return CONCAT44(uVar3,uVar2);
}

