
uint FUN_005075d6(undefined4 param_1,int *param_2,byte param_3)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  undefined4 local_28;
  uint local_24;
  int local_20;
  int local_1c;
  int local_18;
  
  local_28 = DAT_0050770c;
  uVar1 = FUN_00508e92(param_1,0x774,0xc,param_2);
  uVar2 = FUN_00508e92(param_1,0x974,0xc,param_2);
  local_24 = (uint)param_3;
  uVar3 = FUN_00508e92(param_1,0x770,4,&local_24);
  if (param_3 == 3) {
    local_28 = 0x9c3;
  }
  else if (param_3 == 2) {
    local_28 = 4999;
  }
  else if (param_3 == 1) {
    local_28 = 9999;
  }
  uVar4 = FUN_00508e92(param_1,0x76c,4,&local_28);
  local_20 = *param_2 >> 5;
  local_1c = param_2[1] >> 5;
  local_18 = param_2[2] >> 5;
  uVar5 = FUN_00508e92(param_1,0x780,0xc,&local_20);
  uVar6 = FUN_00508e92(param_1,0x78c,0xc,&local_20);
  return uVar1 | uVar2 | uVar3 | uVar4 | uVar5 | uVar6;
}

