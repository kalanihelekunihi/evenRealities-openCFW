
undefined8 FUN_0041bae8(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  byte *pbVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 local_18;
  uint local_14;
  undefined4 uStack_10;
  
  local_18 = param_2;
  if ((param_1 == 0) || (param_1 == 3)) {
    if ((param_1 == 3) && ((*DAT_0041c488 & 0x3f) >> 4 != 3)) {
      uVar3 = 7;
    }
    else {
      local_14 = param_3;
      uStack_10 = param_4;
      iVar4 = FUN_0041c2d8(0x14,&local_18);
      pbVar2 = DAT_0041c48c;
      if (iVar4 == 0) {
        if ((char)local_18 == '\0') {
          if (param_1 == *DAT_0041c48c) {
            if (*DAT_0041c490 != *DAT_0041c48c) {
              *DAT_0041c490 = param_1;
            }
            uVar3 = 0;
          }
          else {
            local_14 = critical_save();
            if (param_1 == 3) {
              FUN_0041cde0(1,3);
              *DAT_0041c494 = *DAT_0041c494 | 1;
            }
            else {
              *DAT_0041c494 = *DAT_0041c494 & 0xfffffffe;
            }
            delay_us(1);
            *DAT_0041c498 = *DAT_0041c498 & 0xfffffffc | param_1 & 3;
            *pbVar2 = param_1;
            *DAT_0041c490 = param_1;
            delay_us(6);
            if (param_1 == 0) {
              FUN_0041cde0(1,0);
            }
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts((local_14 & 1) == 1);
            }
            uVar3 = 0;
          }
        }
        else {
          uVar3 = 3;
        }
      }
      else {
        uVar3 = 1;
      }
    }
  }
  else {
    uVar3 = 6;
  }
  return CONCAT44(local_18,uVar3);
}

