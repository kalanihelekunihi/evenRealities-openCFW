
int FUN_1000654c(byte *param_1,undefined4 *param_2,uint param_3)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  
  uVar1 = (uint)*param_1;
  if (uVar1 == 0x30) {
    uVar2 = (uint)param_1[1];
    if ((PTR_DAT_100065e0[uVar2] & 1) != 0) {
      uVar2 = uVar2 + 0x20 & 0xff;
    }
    if (uVar2 == 0x78) {
      uVar1 = (uint)param_1[2];
      param_3 = 0x10;
      param_1 = param_1 + 2;
    }
    else if (param_3 == 0) {
      param_3 = 8;
    }
  }
  else if (param_3 == 0) {
    param_3 = 10;
  }
  iVar3 = 0;
  do {
    if ((PTR_DAT_100065e0[uVar1] & 0x44) == 0) {
      uVar1 = 0x100;
      if (param_3 < 0x101) goto LAB_1000659a;
    }
    else {
      if ((PTR_DAT_100065e0[uVar1] & 1) != 0) {
        uVar1 = uVar1 + 0x20 & 0xff;
      }
      if (uVar1 < 0x3a) {
        uVar1 = uVar1 - 0x30;
      }
      else {
        uVar1 = uVar1 - 0x57;
      }
      if (param_3 <= uVar1) {
LAB_1000659a:
        if (param_2 != (undefined4 *)0x0) {
          *param_2 = param_1;
        }
        return iVar3;
      }
    }
    param_1 = param_1 + 1;
    iVar3 = uVar1 + iVar3 * param_3;
    uVar1 = (uint)*param_1;
  } while( true );
}

