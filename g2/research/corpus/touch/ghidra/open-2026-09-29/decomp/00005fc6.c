
void FUN_00005fc6(int param_1,uint param_2,undefined4 param_3,int param_4,int param_5)

{
  undefined4 uVar1;
  
  uVar1 = Cy_SysLib_EnterCriticalSection();
  if (param_4 == 0) {
    FUN_00005cf8(param_1,param_2,0);
    FUN_00005d34(param_1,param_2,param_3);
  }
  else {
    FUN_00005d34(param_1,param_2,param_3);
    FUN_00005cf8(param_1,param_2,param_4);
  }
  if (param_5 == 0) {
    if (7 < param_2) {
      software_bkpt(1);
    }
    *(uint *)(param_1 + 0x24) = *(uint *)(param_1 + 0x24) & ~(1 << (param_2 & 0xff) & 0xffU);
  }
  else {
    if (7 < param_2) {
      software_bkpt(1);
    }
    *(uint *)(param_1 + 0x24) = *(uint *)(param_1 + 0x24) | 1 << (param_2 & 0xff) & 0xffU;
  }
  Cy_SysLib_ExitCriticalSection(uVar1);
  return;
}

