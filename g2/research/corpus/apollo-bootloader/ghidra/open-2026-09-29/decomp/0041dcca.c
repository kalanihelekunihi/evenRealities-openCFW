
undefined4 FUN_0041dcca(char param_1,char param_2,uint *param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  undefined4 uVar3;
  uint local_34 [7];
  undefined4 uStack_18;
  
  uVar3 = 0;
  for (uVar2 = 0; uVar2 < 7; uVar2 = uVar2 + 1) {
    local_34[uVar2] = 0xffffffff;
  }
  uStack_18 = param_4;
  uVar2 = critical_save();
  if (param_1 == '\0') {
    if (param_2 != '\0') {
      local_34[0] = *DAT_0041e138;
      local_34[1] = *DAT_0041e13c;
      local_34[2] = *DAT_0041e140;
      local_34[3] = *DAT_0041e144;
      local_34[4] = *DAT_0041e148;
      local_34[5] = *DAT_0041e14c;
      local_34[6] = *DAT_0041e150;
    }
    *param_3 = *DAT_0041e170 & local_34[0];
    param_3[1] = *DAT_0041e174 & local_34[1];
    param_3[2] = *DAT_0041e178 & local_34[2];
    param_3[3] = *DAT_0041e17c & local_34[3];
    param_3[4] = *DAT_0041e180 & local_34[4];
    param_3[5] = *DAT_0041e184 & local_34[5];
    param_3[6] = *DAT_0041e188 & local_34[6];
  }
  else if (param_1 == '\x01') {
    if (param_2 != '\0') {
      local_34[0] = *DAT_0041e154;
      local_34[1] = *DAT_0041e158;
      local_34[2] = *DAT_0041e15c;
      local_34[3] = *DAT_0041e160;
      local_34[4] = *DAT_0041e164;
      local_34[5] = *DAT_0041e168;
      local_34[6] = *DAT_0041e16c;
    }
    *param_3 = *DAT_0041e18c & local_34[0];
    param_3[1] = *DAT_0041e190 & local_34[1];
    param_3[2] = *DAT_0041e194 & local_34[2];
    param_3[3] = *DAT_0041e198 & local_34[3];
    param_3[4] = *DAT_0041e19c & local_34[4];
    param_3[5] = *DAT_0041e1a0 & local_34[5];
    param_3[6] = *DAT_0041e1a4 & local_34[6];
  }
  else {
    uVar3 = 6;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return uVar3;
}

