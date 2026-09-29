
undefined4 buzzer_pwm_config(int param_1,ushort param_2,uint param_3,uint param_4)

{
  uint *puVar1;
  undefined4 uVar2;
  float fVar3;
  int iVar4;
  uint in_fpscr;
  float fVar5;
  undefined8 uVar6;
  ushort local_30;
  undefined1 local_2e;
  undefined4 local_20;
  int local_1c;
  uint uStack_18;
  
  uStack_18 = param_4;
  FUN_00471cae(&local_30);
  local_2e = 4;
  local_30 = param_2;
  FUN_00471c9a(param_1,&local_30);
  FUN_00471e20(0x91,param_1 << 1);
  puVar1 = DAT_00502ca8;
  iVar4 = 4 << ((local_30 & 0x7f) << 1);
  uVar6 = FUN_0047cc60(DAT_00502cac,0,iVar4,iVar4 >> 0x1f);
  *(undefined8 *)puVar1 = uVar6;
  uVar6 = FUN_0047cc60(*puVar1 + (param_3 >> 1),puVar1[1] + (uint)CARRY4(*puVar1,param_3 >> 1),
                       param_3,0);
  uVar2 = (undefined4)uVar6;
  local_20 = uVar2;
  FUN_00471e5e(param_1,uVar2);
  fVar3 = (float)FUN_0055b2a4(uVar2,(int)((ulonglong)uVar6 >> 0x20));
  fVar5 = (float)VectorUnsignedToFloat(param_4 & 0xff,(byte)(in_fpscr >> 0x16) & 3);
  fVar3 = fVar3 * (1.0 - fVar5 / DAT_005029f8) + 0.5;
  local_1c = (uint)(0.0 < fVar3) * (int)fVar3;
  FUN_00471e78(param_1,local_1c);
  return 0;
}

