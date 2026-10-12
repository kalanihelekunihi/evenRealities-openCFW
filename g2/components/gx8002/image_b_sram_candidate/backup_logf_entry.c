/* Native 0x100100ac..0x100100b3 is a hard-float call-through to 0x10010768. */
extern float gx8002_image_b_logf_10010768(float);
float gx8002_image_b_logf_entry_100100ac(float x)
{
    return gx8002_image_b_logf_10010768(x);
}
