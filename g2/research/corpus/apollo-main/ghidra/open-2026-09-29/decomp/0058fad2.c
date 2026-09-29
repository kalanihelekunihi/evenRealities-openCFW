
/* WARNING: Removing unreachable block (ram,0x0058fb00) */

undefined4 FUN_0058fad2(undefined4 param_1,uint param_2)

{
  ulonglong uVar1;
  uint uVar2;
  int iVar3;
  ulonglong uVar4;
  
  uVar4 = FUN_0058fac8();
  uVar1 = uVar4 >> 0x20;
  uVar2 = (uint)uVar4;
  while( true ) {
    if (CONCAT44((int)uVar1 + ((int)param_2 >> 0x1f) + (uint)CARRY4(uVar2,param_2),uVar2 + param_2)
        <= uVar4) {
      return 0xffffffff;
    }
    iVar3 = FUN_0058fb2a(param_1,1);
    if (iVar3 == 1) break;
    osDelay(1);
    uVar4 = FUN_0058fac8();
  }
  return 1;
}

