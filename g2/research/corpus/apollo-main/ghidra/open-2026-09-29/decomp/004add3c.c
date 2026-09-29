
void als_function_17(uint param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  longlong lVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = als_function_02();
  if (uVar2 < param_1) {
    lVar1 = (ulonglong)param_2 * (ulonglong)(param_1 - uVar2) + 0x200;
    uVar4 = (uint)((ulonglong)lVar1 >> 0x20);
    uVar3 = (uint)lVar1 >> 10 | uVar4 * 0x400000;
    als_function_03(uVar3 + uVar2,0,uVar3,uVar4 >> 10,param_4);
  }
  return;
}

