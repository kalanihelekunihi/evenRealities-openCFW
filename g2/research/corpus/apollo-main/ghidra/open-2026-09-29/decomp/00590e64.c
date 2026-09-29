
/* WARNING: Removing unreachable block (ram,0x00590e0a) */
/* WARNING: Removing unreachable block (ram,0x00590e42) */
/* WARNING: Removing unreachable block (ram,0x00590e4a) */
/* WARNING: Removing unreachable block (ram,0x00590e12) */

int FUN_00590e64(int param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  
  if (param_1 == 0x9c4) {
    uVar1 = 0;
  }
  else if (param_1 == 5000) {
    uVar1 = 1;
  }
  else if (param_1 == 0x1d4c) {
    uVar1 = 2;
  }
  else if (param_1 == 10000) {
    uVar1 = 3;
  }
  else {
    uVar1 = 4;
  }
  if (param_2 == 8000) {
    iVar2 = 0;
  }
  else if (param_2 == 16000) {
    iVar2 = 1;
  }
  else if (param_2 == 24000) {
    iVar2 = 2;
  }
  else if (param_2 == 32000) {
    iVar2 = 3;
  }
  else {
    if (param_2 != 48000) {
      return -1;
    }
    iVar2 = 4;
  }
  if (3 < uVar1) {
    return -1;
  }
  return *(int *)(DAT_005915a8 + iVar2 * 4) * (uVar1 + 1);
}

