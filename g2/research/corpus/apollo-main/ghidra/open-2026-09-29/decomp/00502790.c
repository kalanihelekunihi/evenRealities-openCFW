
undefined4 buzzer_pwm_update(uint param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  float fVar1;
  uint in_fpscr;
  float fVar2;
  undefined8 uVar3;
  
  uVar3 = FUN_0047cc60(*DAT_00502ca8 + (param_1 >> 1),
                       DAT_00502ca8[1] + (uint)CARRY4(*DAT_00502ca8,param_1 >> 1),param_1,0);
  fVar1 = (float)FUN_0055b2a4((int)uVar3,(int)((ulonglong)uVar3 >> 0x20));
  fVar2 = (float)VectorUnsignedToFloat((uint)param_2,(byte)(in_fpscr >> 0x16) & 3);
  fVar1 = fVar1 * (1.0 - fVar2 / DAT_005029f8) + 0.5;
  FUN_00471e5e(7,(int)uVar3);
  FUN_00471e78(7,(uint)(0.0 < fVar1) * (int)fVar1);
  return param_4;
}

