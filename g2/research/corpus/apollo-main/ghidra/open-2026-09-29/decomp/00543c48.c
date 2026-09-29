
void FUN_00543c48(int param_1,char *param_2)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0x40;
  uVar1 = 0;
  while( true ) {
    if (0x3f < uVar1) {
      if ((*param_2 != '\0') && (uVar2 < 0x40)) {
        FUN_00439be4(param_1 + uVar2 * 0x18 + 0x2a8,param_2,0x18);
      }
      return;
    }
    if (*(int *)(uVar1 * 0x18 + param_1 + 0x2ac) == *(int *)(param_2 + 4)) break;
    if (*(int *)(param_1 + uVar1 * 0x18 + 0x2ac) == -1) {
      uVar2 = uVar1;
    }
    uVar1 = uVar1 + 1;
  }
  if (*param_2 != '\0') {
    FUN_00439be4(param_1 + uVar1 * 0x18 + 0x2a8,param_2,0x18);
    return;
  }
  *(undefined4 *)(param_1 + uVar1 * 0x18 + 0x2ac) = 0xffffffff;
  return;
}

