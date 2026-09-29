
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10006cb0(undefined4 param_1,undefined4 *param_2,int param_3)

{
  undefined4 *puVar1;
  
  do {
    uRam0000004c = uRam00000028 & 1;
  } while (uRam0000004c != 0);
  uRam00000000 = 0x407;
  iRam00000004 = param_3;
  uRam00000010 = 1;
  iRam00000018 = param_3 << 0x10;
  _DAT_a20000f4 = uRam0000004c;
  uRam00000008 = 1;
  uRam00000060 = param_1;
  if (param_3 != 0) {
    puVar1 = (undefined4 *)((int)param_2 + param_3);
    do {
      do {
      } while ((uRam00000028 & 2) == 0);
      uRam00000060 = *param_2;
      param_2 = (undefined4 *)((int)param_2 + 1);
    } while (param_2 != puVar1);
  }
  do {
  } while (iRam00000020 != 0);
  do {
  } while ((uRam00000028 & 1) != 0);
  return;
}

