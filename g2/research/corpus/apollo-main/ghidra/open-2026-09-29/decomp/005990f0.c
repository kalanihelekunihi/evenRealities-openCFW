
void FUN_005990f0(undefined4 param_1,undefined4 param_2,float *param_3,undefined4 param_4,
                 undefined4 param_5,float *param_6)

{
  float fVar1;
  
  do {
    *param_6 = DAT_00599324;
    fVar1 = DAT_00599324 + *param_3 * *(float *)PTR_DAT_005996dc;
    *param_6 = fVar1;
    fVar1 = fVar1 + param_3[1] * *(float *)((int)PTR_DAT_005996dc + 4);
    *param_6 = fVar1;
    fVar1 = fVar1 + param_3[2] * *(float *)((int)PTR_DAT_005996dc + 8);
    *param_6 = fVar1;
    DAT_00599324 = fVar1 + param_3[3] * *(float *)((int)PTR_DAT_005996dc + 0xc);
    PTR_DAT_005996dc = (undefined *)((int)PTR_DAT_005996dc + 0x10);
    param_3 = param_3 + 4;
    loopEnd();
  } while( true );
}

