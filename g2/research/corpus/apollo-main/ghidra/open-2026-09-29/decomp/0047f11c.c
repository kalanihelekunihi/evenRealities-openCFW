
undefined8 FUN_0047f11c(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

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
    if ((param_1 == 3) && ((*DAT_0047fabc & 0x3f) >> 4 != 3)) {
      uVar3 = 7;
    }
    else {
      local_14 = param_3;
      uStack_10 = param_4;
      iVar4 = FUN_0047f90c(0x14,&local_18);
      pbVar2 = DAT_0047fac0;
      if (iVar4 == 0) {
        if ((char)local_18 == '\0') {
          if (param_1 == *DAT_0047fac0) {
            if (*DAT_0047fac4 != *DAT_0047fac0) {
              *DAT_0047fac4 = param_1;
            }
            uVar3 = 0;
          }
          else {
            local_14 = FUN_00473940();
            if (param_1 == 3) {
              FUN_004803c2(1,3);
              *DAT_0047fac8 = *DAT_0047fac8 | 1;
            }
            else {
              *DAT_0047fac8 = *DAT_0047fac8 & 0xfffffffe;
            }
            FUN_004807a0(1);
            *DAT_0047facc = *DAT_0047facc & 0xfffffffc | param_1 & 3;
            *pbVar2 = param_1;
            *DAT_0047fac4 = param_1;
            FUN_004807a0(6);
            if (param_1 == 0) {
              FUN_004803c2(1,0);
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

