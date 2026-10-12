float negative_sum(float d,float b,float c,float a) { volatile float p=d*b; return -(p+c*a); }
float reverse_difference(float d,float b,float c,float a) { volatile float p=d*b; return c*a-p; }
float ordinary_difference(float d,float b,float c,float a) { volatile float p=d*b; return p-c*a; }
