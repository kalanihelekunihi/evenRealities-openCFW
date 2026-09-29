
float * FUN_1000ed7c(float *param_1)

{
  float fVar1;
  float fVar2;
  float in_vr0;
  float in_vr2;
  float in_vr3;
  
  fVar2 = in_vr2;
  FUN_100113c4(param_1,0,0x40);
  if (param_1 != (float *)0x0) {
    *param_1 = in_vr2;
    *param_1 = in_vr3;
    fVar1 = 0.0;
    *param_1 = in_vr2;
    *param_1 = in_vr0;
    *param_1 = fVar2;
    *param_1 = in_vr3 * fVar2;
    FUN_100100a4();
    fVar2 = 0.0;
    *param_1 = fVar1;
    FUN_100100ac();
    fVar1 = -fVar2 / (*param_1 * *param_1);
    FUN_10011af4();
    FUN_1000f84c();
    FUN_10012398();
    fVar2 = 0.0;
    *param_1 = fVar1;
    FUN_100100ac();
    fVar2 = -fVar2 / (*param_1 * *param_1);
    FUN_10011af4();
    FUN_1000f84c();
    FUN_10012398();
    *param_1 = fVar2;
  }
  return param_1;
}

