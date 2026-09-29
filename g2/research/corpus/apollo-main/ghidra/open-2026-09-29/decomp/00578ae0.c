
/* WARNING: Removing unreachable block (ram,0x00578b4a) */

undefined8 semantic_CodecWaitForUartToken(int param_1,uint param_2,undefined4 param_3,uint param_4)

{
  ulonglong uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  ulonglong uVar7;
  uint local_28;
  
  local_28 = param_4;
  iVar2 = FUN_0044a43c(param_1);
  uVar7 = FUN_0058fac8();
  uVar1 = uVar7 >> 0x20;
  uVar3 = (uint)uVar7;
  do {
    if (CONCAT44(((int)param_2 >> 0x1f) + (int)uVar1 + (uint)CARRY4(uVar3,param_2),uVar3 + param_2)
        <= uVar7) {
      uVar5 = 0xffffffff;
LAB_00578b6c:
      return CONCAT44(local_28,uVar5);
    }
    iVar6 = 0;
    while ((iVar6 < iVar2 &&
           (iVar4 = FUN_0058fad2(&local_28,(uVar3 + param_2) - (int)uVar7), iVar4 == 1))) {
      if ((char)local_28 == '\r') {
        local_28 = CONCAT31(local_28._1_3_,10);
      }
      if ((local_28 & 0xff) != (uint)*(byte *)(param_1 + iVar6)) break;
      if (iVar6 + 1 == iVar2) {
        uVar5 = 0;
        goto LAB_00578b6c;
      }
      iVar6 = iVar6 + 1;
    }
    uVar7 = FUN_0058fac8();
  } while( true );
}

