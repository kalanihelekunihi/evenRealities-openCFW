
/* WARNING: Removing unreachable block (ram,0x00541dfe) */

ulonglong FUN_00541e2c(char *param_1,undefined4 **param_2,undefined4 param_3,undefined4 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  char *pcVar4;
  char cVar5;
  ulonglong uVar6;
  undefined4 *puStack_20;
  
  pcVar4 = param_1;
  puStack_20 = param_4;
  if (param_2 == (undefined4 **)0x0) {
    param_2 = &puStack_20;
  }
  while (iVar1 = FUN_004d58ae(*pcVar4), iVar1 != 0) {
    pcVar4 = pcVar4 + 1;
  }
  cVar5 = *pcVar4;
  if (cVar5 == '-' || cVar5 == '+') {
    pcVar4 = pcVar4 + 1;
    iVar1 = FUN_004d58ae(*pcVar4);
    if (iVar1 != 0) goto LAB_00541dd6;
  }
  else {
    cVar5 = '+';
  }
  uVar6 = FUN_00541bd8(pcVar4,param_2,param_3,param_4);
  if (pcVar4 == (char *)*param_2) {
LAB_00541dd6:
    *param_2 = (undefined4 *)param_1;
    return 0;
  }
  if (cVar5 == '+') {
    if (0x7fffffffffffffff < uVar6) {
LAB_00541e02:
      FUN_00439cb2();
      if (param_4 != (undefined4 *)0x0) {
        *param_4 = 1;
      }
      if (cVar5 == '-') {
        uVar2 = 0;
        uVar3 = 0x80000000;
      }
      else {
        uVar2 = 0xffffffff;
        uVar3 = 0x7fffffff;
      }
      return CONCAT44(uVar3,uVar2);
    }
  }
  else if (cVar5 == '-') {
    if (uVar6 < 0x8000000000000001) {
      return CONCAT44(-(int)(uVar6 >> 0x20) - (uint)((int)uVar6 != 0),-(int)uVar6);
    }
    goto LAB_00541e02;
  }
  return uVar6;
}

