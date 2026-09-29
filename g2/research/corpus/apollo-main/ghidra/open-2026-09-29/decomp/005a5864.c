
undefined4 atImuEulerHandler(void)

{
  float *pfVar1;
  undefined8 uVar2;
  
  uVar2 = semantic_get_magnetic_vector();
  pfVar1 = (float *)uVar2;
  at_core_output(PTR_s_AT_IMU_EULER_OK_roll___2f_pitch__005a58a4,(int)((ulonglong)uVar2 >> 0x20),
                 SUB84((double)*pfVar1,0),(int)((ulonglong)(double)*pfVar1 >> 0x20),
                 (double)pfVar1[1],(double)pfVar1[2]);
  return 1;
}

