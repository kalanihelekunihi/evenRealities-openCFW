
/* WARNING: Instruction at (ram,0x005982f6) overlaps instruction at (ram,0x005982f4)
    */

undefined4 FUN_00598284(int param_1,int param_2,int param_3,undefined4 param_4,undefined2 *param_5)

{
  int iVar1;
  int iVar2;
  int iVar3;
  bool bVar4;
  
  if (((1 < param_1) && (2 < param_2)) && (param_2 < 5)) {
    iVar1 = DAT_00598458 + param_1 * 0x20 + param_2 * 8;
    iVar3 = *(int *)(iVar1 + -0x58);
    bVar4 = SBORROW4(param_3,iVar3);
    iVar2 = param_3 - iVar3;
    if (iVar3 <= param_3) {
      iVar2 = *(int *)(iVar1 + -0x54);
      bVar4 = SBORROW4(iVar2,param_3);
      iVar2 = iVar2 - param_3;
    }
    if (iVar2 < 0 == bVar4) {
      if (param_2 != 3) {
        do {
          loopEnd();
        } while( true );
      }
      do {
        param_5 = param_5 + 4;
        loopEnd();
        *param_5 = (short)param_5;
      } while( true );
    }
  }
  return 0;
}

