
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10007790(int param_1,undefined4 *param_2,int param_3)

{
  undefined4 *puVar1;
  byte bStack_5;
  
  do {
  } while ((uRam00000028 & 1) != 0);
  uRam00000000 = 0x407;
  iRam00000004 = param_3 + -1;
  uRam00000050 = 8;
  if (param_1 != 0) {
    puVar1 = (undefined4 *)(DAT_10007880 + 0x10);
    do {
      do {
      } while ((uRam00000028 & 2) == 0);
      uRam00000060 = *puVar1;
      puVar1 = (undefined4 *)((int)puVar1 + 1);
    } while (puVar1 != (undefined4 *)(DAT_10007880 + param_1 + 0x10));
  }
  uRam00000010 = 1;
  if (param_3 != 0) {
    puVar1 = (undefined4 *)((int)param_2 + param_3);
    do {
      do {
      } while ((uRam00000028 & 2) == 0);
      uRam00000060 = *param_2;
      param_2 = (undefined4 *)((int)param_2 + 1);
    } while (puVar1 != param_2);
  }
  do {
  } while (iRam00000020 != 0);
  do {
  } while ((uRam00000028 & 1) != 0);
  uRam00000090 = 1;
  uRam00000008 = 1;
  uRam00000018 = 0;
  uRam0000004c = 0;
  _DAT_a20000f4 = 0;
  do {
    FUN_10006c30(5,&bStack_5,1);
  } while ((bStack_5 & 1) != 0);
  return;
}

