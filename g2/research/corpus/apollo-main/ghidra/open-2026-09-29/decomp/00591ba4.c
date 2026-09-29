
/* WARNING: Heritage AFTER dead removal. Example location: s1 : 0x00591bd6 */
/* WARNING: Restarted to delay deadcode elimination for space: register */

int service_algo_source_angle(void)

{
  undefined8 in_d0;
  undefined4 in_s3;
  undefined4 in_s5;
  undefined4 in_s7;
  double local_28;
  undefined1 auStack_20 [8];
  undefined1 auStack_18 [8];
  undefined1 auStack_10 [8];
  
  service_algo_cross_correlation
            ((int)DAT_00591ce8,(int)((ulonglong)in_d0 >> 0x20),(int)DAT_00591ce0,in_s3,
             (int)DAT_00591cd8,in_s5,(int)DAT_00591cd0,in_s7,(int)DAT_00591cd0,DAT_00591cf4,
             DAT_00591cf0,800,10,&local_28,auStack_10,auStack_18,auStack_20);
  return (int)(short)(longlong)((local_28 * DAT_00591cf8) / DAT_00591d0c);
}

