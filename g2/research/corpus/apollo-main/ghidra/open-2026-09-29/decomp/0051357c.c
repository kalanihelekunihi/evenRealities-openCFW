
undefined4 FUN_0051357c(byte *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = FUN_00513748(param_1[2]);
  uVar2 = (~(0xffff << ((*param_1 + 1) - (uint)param_1[1] & 0xff)) & param_2 & 0xffff) <<
          (uint)param_1[1] | ~(0xffff << (uint)param_1[1] ^ 0xffff << (*param_1 + 1 & 0xff)) & uVar1
  ;
  if ((uVar1 & 0xffff) != (uVar2 & 0xffff)) {
    FUN_00513780(param_1[2],uVar2 & 0xffff);
  }
  return param_4;
}

