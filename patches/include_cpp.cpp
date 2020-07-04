
/* WARNING: Unknown calling convention yet parameter storage is locked */
/* Names_DeinitModule(void) */

struct Names {
public:
	void Deinit(Names *);
};

void Names_DeinitModule(void)

{
  int iVar1;
  int iVar2;

  iVar1 = 5;
  iVar2 = 0x28;
  do {
    Names::Deinit((Names *)(lastNames + iVar2));
    Names::Deinit((Names *)(firstNames + iVar2));
    iVar1 = iVar1 + -1;
    iVar2 = iVar2 + -8;
  } while (-1 < iVar1);
  return;
}
