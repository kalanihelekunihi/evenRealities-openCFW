
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_100034a4(undefined4 param_1,undefined1 *param_2,int param_3)

{
  undefined1 *puVar1;
  
  do {
  } while ((uRam00000028 & 1) != 0);
  uRam00000000 = 0xc07;
  iRam00000004 = param_3 + -1;
  uRam00000010 = 1;
  uRam00000008 = 1;
  uRam00000018 = 0;
  _DAT_a20000f4 = uRam00000018;
  uRam00000060 = param_1;
  uRam0000004c = uRam00000018;
  if (param_3 != 0) {
    puVar1 = param_2 + param_3;
    do {
      do {
      } while ((uRam00000028 & 8) == 0);
      *param_2 = (char)uRam00000060;
      param_2 = param_2 + 1;
    } while (param_2 != puVar1);
  }
  do {
  } while (iRam00000024 != 0);
  do {
  } while ((uRam00000028 & 1) != 0);
  return;
}

