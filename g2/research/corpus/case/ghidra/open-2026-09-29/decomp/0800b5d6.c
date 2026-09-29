
undefined4 case_collect_bits(undefined1 *param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  undefined1 uVar4;
  uint uVar5;
  undefined4 uVar6;
  int local_18;
  
  uVar6 = 1;
  uVar5 = 0;
  uVar3 = 7;
  local_18 = param_4;
  do {
    uVar4 = (undefined1)uVar5;
    iVar1 = case_probe_high_signal(&local_18);
    if (iVar1 == 0) {
      uVar6 = 0;
      break;
    }
    uVar2 = (local_18 << (uVar3 & 0xff)) + uVar5;
    uVar5 = uVar2 & 0xff;
    uVar4 = (undefined1)uVar2;
    uVar3 = uVar3 - 1;
  } while (-1 < (int)uVar3);
  *param_1 = uVar4;
  return uVar6;
}

