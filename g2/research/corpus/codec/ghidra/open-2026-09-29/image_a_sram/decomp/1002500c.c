
/* WARNING: Restarted to delay deadcode elimination for space: register */

undefined4 gx8002_clock_pll_wait_timeout(int *param_1,int param_2)

{
  longlong lVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  
  iVar5 = param_2;
  _clk_set_pll();
  if (*param_1 == 1) {
    uVar3 = gx8002_clock_time_us();
    iVar2 = iRam1002505c;
    iVar6 = iVar5;
    do {
      if ((*(uint *)(iVar2 + 0x18) & 8) != 0) goto LAB_1002501c;
      uVar4 = gx8002_clock_time_us();
      lVar1 = CONCAT44(iVar6,uVar4) - CONCAT44(iVar5,uVar3);
    } while (((int)((ulonglong)lVar1 >> 0x20) == 0) &&
            (iVar6 = 0, (uint)lVar1 <= (uint)(param_2 * 1000)));
    uVar3 = 0xffffffff;
  }
  else {
LAB_1002501c:
    uVar3 = 0;
  }
  return uVar3;
}

