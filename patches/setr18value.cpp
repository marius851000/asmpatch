void setspyrorotspeedtor18() asm ("setspyrorotspeedtor18");

register float *r18 asm ("r18");

float spyrorotspeed = 100.0f;
void setspyrorotspeedtor18() {
	r18 = &spyrorotspeed;
}
