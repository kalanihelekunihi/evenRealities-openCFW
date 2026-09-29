
/* WARNING: Restarted to delay deadcode elimination for space: register */
/* WARNING: Restarted to delay deadcode elimination for space: stack */

void gx8002_delay_us(uint param_1,uint param_2)

{
  int iVar1;
  int iVar3;
  uint uVar4;
  undefined4 uStack_18;
  undefined4 uStack_14;
  longlong lVar2;
  
  uStack_18 = gx8002_clock_time_us();
  lVar2 = (ulonglong)param_1 + CONCAT44(param_2,uStack_18);
  iVar1 = (int)lVar2;
  uVar4 = (uint)((ulonglong)lVar2 >> 0x20);
  uStack_14 = param_2;
  if (iVar1 == -1) {
    uVar4 = uVar4 + 1;
  }
  while( true ) {
    if ((uVar4 <= uStack_14) && ((uVar4 != uStack_14 || (iVar1 + 1U <= uStack_18)))) break;
    iVar3 = 0x32;
    do {
      iVar3 = iVar3 + -1;
    } while (iVar3 != 0);
    uStack_18 = gx8002_clock_time_us(uStack_18);
  }
  return;
}

