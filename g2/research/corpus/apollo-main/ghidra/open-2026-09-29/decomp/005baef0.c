
undefined8
FUN_005baef0(float param_1,undefined1 *param_2,int param_3,int param_4,undefined *param_5)

{
  int iVar1;
  undefined *puVar2;
  float fVar3;
  int local_20;
  undefined *local_1c;
  
  local_20 = param_4;
  local_1c = param_5;
  if ((param_2 != (undefined1 *)0x0) && (param_3 != 0)) {
    *param_2 = 0;
    if (param_1 < 0.0) {
      puVar2 = (undefined *)0x5bafc0;
      param_1 = -param_1;
    }
    else {
      puVar2 = &DAT_005bafbc;
    }
    fVar3 = (float)FUN_00577d08(param_1 * DAT_005bafac);
    local_1c = DAT_005bbb6c;
    local_20 = (int)fVar3 / 0x3c;
    iVar1 = (int)fVar3 % 0x3c;
    if (iVar1 == 0) {
      FUN_0044b728(param_2,param_3,DAT_005bbb3c,puVar2);
      local_1c = param_5;
    }
    else {
      if (iVar1 == 0xf) {
        local_1c = &DAT_005bb1fc;
      }
      else if (iVar1 == 0x1e) {
        local_1c = &DAT_005bb200;
      }
      else if (iVar1 == 0x2d) {
        local_1c = &DAT_005bb204;
      }
      else {
        FUN_0044b728(DAT_005bbb6c,4,PTR_DAT_005bbb70,(iVar1 * 100 + 0x1e) / 0x3c);
      }
      FUN_0044b728(param_2,param_3,DAT_005bbc78,puVar2);
    }
  }
  return CONCAT44(local_1c,local_20);
}

