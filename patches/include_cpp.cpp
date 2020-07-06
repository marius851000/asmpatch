
/* WARNING: Unknown calling convention yet parameter storage is locked */
/* Names_DeinitModule(void) */

void Names_DeinitModule(void) asm ("Names_DeinitModule_Custom");

struct Names {
public:
	void Deinit() asm ("Deinit__5NamesFv");
};

extern char lastNames [48];
extern char firstNames [48];

void Names_DeinitModule(void)
{
  int iVar1;
  int iVar2;

  iVar1 = 5;
  iVar2 = 0x28;
  do {
    ((Names *)(&lastNames + iVar2))->Deinit();
    ((Names *)(&firstNames + iVar2))->Deinit();
    iVar1 = iVar1 + -1;
    iVar2 = iVar2 + -8;
  } while (-1 < iVar1);
  return;
}
