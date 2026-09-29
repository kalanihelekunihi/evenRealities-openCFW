
/* WARNING: Removing unreachable block (ram,0x0800aec0) */
/* WARNING: Removing unreachable block (ram,0x0800aec2) */

void FUN_0800ae96(undefined4 param_1,int param_2,int param_3,undefined4 param_4,uint param_5,
                 undefined4 *param_6,undefined4 *param_7)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  FUN_080001d8(param_7[0xc],param_3 << 2,0xa5);
  iVar1 = param_7[0xc];
  if (param_2 == 0) {
    *(undefined1 *)(param_7 + 0xd) = 0;
  }
  else {
    uVar3 = 0;
    do {
      *(undefined1 *)((int)param_7 + uVar3 + 0x34) = *(undefined1 *)(param_2 + uVar3);
      if (*(char *)(param_2 + uVar3) == '\0') break;
      uVar3 = uVar3 + 1;
    } while (uVar3 < 0x10);
    *(undefined1 *)((int)param_7 + 0x43) = 0;
  }
  if (0x37 < param_5) {
    param_5 = 0x37;
  }
  param_7[0xb] = param_5;
  param_7[0x13] = param_5;
  param_7[0x14] = 0;
  FUN_0800bfaa(param_7 + 1);
  FUN_0800bfaa(param_7 + 6);
  param_7[4] = param_7;
  param_7[6] = 0x38 - param_5;
  param_7[9] = param_7;
  param_7[0x15] = 0;
  *(undefined1 *)(param_7 + 0x16) = 0;
  uVar2 = pxPortInitialiseStack(iVar1 + (param_3 + -1) * 4 & 0xfffffff8,param_1,param_4);
  *param_7 = uVar2;
  if (param_6 != (undefined4 *)0x0) {
    *param_6 = param_7;
  }
  return;
}

