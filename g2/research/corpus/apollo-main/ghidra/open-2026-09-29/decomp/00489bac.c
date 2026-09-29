
uint FUN_00489bac(uint param_1)

{
  undefined1 uVar1;
  undefined4 local_4;
  
  if (0x7f < param_1) {
    uVar1 = (undefined1)param_1;
    if (param_1 < 0x800) {
      local_4 = (uint)(CONCAT11(uVar1,(char)(param_1 >> 6)) & 0x3f1f | 0x80c0);
      param_1 = local_4;
    }
    else if (param_1 < 0x10000) {
      local_4 = (uint)(CONCAT12(uVar1,CONCAT11((char)(param_1 >> 6),(char)(param_1 >> 0xc))) &
                       0x3f3f0f | 0x8080e0);
      param_1 = local_4;
    }
    else if (param_1 < 0x110000) {
      local_4 = CONCAT13(uVar1,CONCAT12((char)(param_1 >> 6),
                                        CONCAT11((char)(param_1 >> 0xc),(char)(param_1 >> 0x12)))) &
                0x3f3f3f07 | 0x808080f0;
      param_1 = local_4;
    }
    else {
      param_1 = 0;
    }
  }
  return param_1;
}

