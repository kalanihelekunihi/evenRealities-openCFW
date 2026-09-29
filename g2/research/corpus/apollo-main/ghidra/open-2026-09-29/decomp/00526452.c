
void load_mac_face(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                  byte *param_5)

{
  char cVar1;
  
  cVar1 = IsMacBinary(param_1,param_2,param_3,param_4,param_4);
  if (cVar1 == '\x02') {
    cVar1 = IsMacResource(param_1,param_2,0,param_3,param_4);
  }
  if (((cVar1 == '\x02') || (cVar1 == 'U')) && ((int)((uint)*param_5 << 0x1d) < 0)) {
    load_face_in_embedded_rfork(param_1,param_2,param_3,param_4,param_5);
  }
  return;
}

