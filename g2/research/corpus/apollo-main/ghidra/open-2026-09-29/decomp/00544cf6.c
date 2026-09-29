
/* WARNING: Removing unreachable block (ram,0x00544d3c) */

ulonglong FUN_00544cf6(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uStack_24;
  
  uStack_24 = param_4;
  FUN_0043c0e4(&uStack_24,1,0xff,param_4,param_3);
  uVar2 = 0;
  uVar1 = FUN_00585a52(param_1,param_2,param_3,param_4);
  return CONCAT44(uVar2,uVar1) & 0xffffffff000000ff;
}

