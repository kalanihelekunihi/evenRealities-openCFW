
float * FUN_1000ea74(float *param_1)

{
  float fVar1;
  float fVar2;
  float in_vr3;
  float in_stack_00000000;
  float in_stack_00000004;
  
  FUN_100113c4(param_1,0,0x30);
  if (param_1 != (float *)0x0) {
    *param_1 = in_vr3;
    *(undefined1 *)(param_1 + 0xb) = 0;
    fVar1 = 0.0;
    *param_1 = in_vr3;
    *param_1 = in_vr3;
    *param_1 = in_vr3;
    *param_1 = (float)(int)in_stack_00000004;
    param_1[4] = in_stack_00000000;
    FUN_100100ac();
    fVar2 = -fVar1 / ((float)(uint)*param_1 * *param_1);
    FUN_100100b4();
    fVar1 = 0.0;
    *param_1 = fVar2;
    FUN_100100ac();
    fVar1 = -fVar1 / ((float)(uint)*param_1 * *param_1);
    FUN_100100b4();
    *param_1 = fVar1;
    if (*(char *)(param_1 + 0xb) == '\0') {
      param_1[6] = 0.0;
      param_1[7] = 0.0;
      param_1[10] = 0.0;
    }
    *(undefined1 *)(param_1 + 0xb) = 1;
  }
  return param_1;
}

