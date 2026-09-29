
undefined8
FUN_0055d2c2(undefined4 param_1,uint param_2,uint param_3,byte *param_4,byte *param_5,byte *param_6)

{
  uint uVar1;
  uint uVar2;
  byte bVar3;
  uint local_30;
  uint local_2c;
  byte *pbStack_28;
  
  local_2c = param_3;
  pbStack_28 = param_4;
  uVar1 = FUN_00508e74(param_1,(param_2 & 0xff) * 2 + 0xa20f,1,param_6 + 1);
  bVar3 = 0;
  local_30 = param_2;
  do {
    if (*param_6 <= bVar3) {
LAB_0055d46e:
      return CONCAT44(local_30,uVar1);
    }
    local_2c = CONCAT31(local_2c._1_3_,
                        param_6[(uint)bVar3 * 8 + 6] & 0xf | *DAT_0055d474 & 0x80 |
                        (param_6[(uint)bVar3 * 8 + 4] & 3) << 4 | (byte)((param_2 & 1) << 6));
    if (param_6[(uint)bVar3 * 8 + 4] == 0) {
      if (param_6[(uint)bVar3 * 8 + 6] != 0) {
        if (5 < (uint)param_6[(uint)bVar3 * 8 + 6] + (uint)*param_4) {
          uVar1 = 0xffffffff;
          goto LAB_0055d46e;
        }
        local_30 = FUN_00508e74(param_1,*param_4 + 0xa233,1,param_6 + (uint)bVar3 * 8 + 5);
        local_30 = local_30 | uVar1;
        *param_4 = *param_4 + 1;
        uVar1 = FUN_00508e74(param_1,*param_4 + 0xa233,param_6[(uint)bVar3 * 8 + 6],
                             *(undefined4 *)(param_6 + (uint)bVar3 * 8 + 8));
        uVar1 = uVar1 | local_30;
        *param_4 = param_6[(uint)bVar3 * 8 + 6] + *param_4;
        local_2c = CONCAT31(local_2c._1_3_,(byte)local_2c & 0xf0 | (byte)local_2c + 1 & 0xf);
      }
    }
    else {
      uVar2 = FUN_00508e74(param_1,(param_2 & 0xff) * 2 + 0xa20e,1,param_6 + (uint)bVar3 * 8 + 5);
      uVar1 = uVar1 | uVar2;
    }
    if (((param_3 & 0xff) != 0) && ((uint)*param_6 == bVar3 + 1)) {
      local_2c = local_2c | 0x80;
    }
    uVar2 = FUN_00508e74(param_1,*param_5 + 0xa206,1,&local_2c);
    uVar1 = uVar2 | uVar1;
    *param_5 = *param_5 + 1;
    bVar3 = bVar3 + 1;
  } while( true );
}

