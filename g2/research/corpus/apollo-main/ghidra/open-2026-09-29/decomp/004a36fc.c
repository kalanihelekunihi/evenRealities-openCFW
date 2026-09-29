
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 semantic_apply_odr_config(byte *param_1)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 4);
  if (iVar1 == 1000) {
    *_DAT_004a4278 = 6;
    *_DAT_004a427c = 6;
    *_DAT_004a3818 = 5;
  }
  else if (iVar1 == 0x9c4) {
    *_DAT_004a4278 = 7;
    *_DAT_004a427c = 7;
    *_DAT_004a3818 = 4;
  }
  else if (iVar1 == 5000) {
    *_DAT_004a4278 = 8;
    *_DAT_004a427c = 8;
    *_DAT_004a3818 = 3;
  }
  else if (iVar1 == 10000) {
    *_DAT_004a4278 = 9;
    *_DAT_004a427c = 9;
    *_DAT_004a3818 = 2;
  }
  else if (iVar1 == 20000) {
    *_DAT_004a4278 = 10;
    *_DAT_004a427c = 10;
    *_DAT_004a3818 = 1;
  }
  else {
    if (iVar1 != 40000) {
      return 0xffffffff;
    }
    *_DAT_004a4278 = 0xb;
    *_DAT_004a427c = 0xb;
    *_DAT_004a3818 = 0;
  }
  *_DAT_004a4280 = (byte)(((uint)*param_1 << 0x1e) >> 0x1f);
  *_DAT_004a4284 = *(undefined4 *)(param_1 + 8);
  *_DAT_004a381c = (short)*(undefined4 *)(param_1 + 0xc);
  return 0;
}

