
uint FUN_0054ee90(uint *param_1,uint param_2,int param_3)

{
  uint uVar1;
  uint uVar2;
  
  if ((param_3 == 0) || (*param_1 < param_2)) {
    uVar1 = (uint)*(byte *)*param_1;
    *param_1 = *param_1 + 1;
    if (param_2 < *param_1) {
      uVar1 = *DAT_0054f358;
    }
    else {
      uVar2 = uVar1;
      if (uVar1 < 0x80000000) {
        do {
          if (uVar2 != 0xff) {
            return uVar1;
          }
          uVar2 = (uint)*(byte *)*param_1;
          *param_1 = *param_1 + 1;
          uVar1 = uVar2 + uVar1;
          if (param_2 < *param_1) {
            return *DAT_0054f358;
          }
        } while (uVar1 < 0x80000000);
        uVar1 = *DAT_0054f358;
      }
      else {
        uVar1 = *DAT_0054f358;
      }
    }
  }
  else {
    uVar1 = *DAT_0054f358;
  }
  return uVar1;
}

