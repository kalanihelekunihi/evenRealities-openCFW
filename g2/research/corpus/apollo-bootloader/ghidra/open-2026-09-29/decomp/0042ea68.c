
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
hw_profile_apply_42ea68(uint *param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != _DAT_0042f17c)) {
    iVar1 = 2;
  }
  else if (*param_2 == 2) {
    iVar1 = clock_request(4,0xf);
    if (iVar1 == 0) {
      *_DAT_0042f180 =
           (*param_2 & 7) << 0x18 | (param_2[1] & 1) << 0x14 | (param_2[2] & 1) << 0x13 |
           (param_2[3] & 7) << 0x10 | 0x1000 | (param_2[4] & 1) << 4 | (param_2[5] & 1) << 3 |
           (param_2[6] & 1) << 2;
      iVar1 = 0;
    }
  }
  else {
    iVar1 = 6;
  }
  return CONCAT44(param_4,iVar1);
}

