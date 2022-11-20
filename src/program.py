from colorama import Fore
import program_guests
import program_hosts
import data.mongo_setup as mongo_setup

def main():
    # TODO: Setup mongoengine global values
    mongo_setup.global_init()
    print_header()

    try:
        while True:
            if find_user_intent() == 'book':
                program_guests.run()
            else:
                program_hosts.run()
    except KeyboardInterrupt:
        return


def print_header():
    pet = \
    """
       __,-----._                       ,-. 
     ,'   ,-.    \`---.          ,-----<._/ 
    (,.-. o:.`    )),"\\-._    ,'         `. 
   ('"-` .\       \`:_ )\  `-;'-._          \ 
  ,,-.    \` ;  :  \( `-'     ) -._     :   `: 
 (    \ `._\\ ` ;             ;    `    :    ) 
  \`.  `-.    __   ,         /  \        ;, ( 
   `.`-.___--'  `-          /    ;     | :   | 
     `-' `-.`--._          '           ;     | 
           (`--._`.                ;   /\    | 
            \     '                \  ,  )   : 
            |  `--::----            \'   ;  ;| 
            \    .__,-      (        )   :  :| 
             \    : `------; \      |    |   ; 
              \   :       / , )     |    |  ( 
-Pets BnB-     \   \      `-^-|     |   / , ,\ 
                )  )          | -^- ;   `-^-^' 
             _,' _ ;          |    | 
            / , , ,'         /---. : 
            `-^-^'          (  :  :,' 
                             `-^--' """

    print(Fore.WHITE + '****************  PETS BnB  ****************')
    print(Fore.GREEN + pet)
    print(Fore.WHITE + '*********************************************')
    print()
    print("Welcome to Pet BnB!")
    print("Why are you here?")
    print()


def find_user_intent():
    print("[g] Book a cage for your pet")
    print("[h] Offer extra cage space")
    print()
    choice = input("Are you a [g]uest or [h]ost? ")
    if choice == 'h':
        return 'offer'

    return 'book'


if __name__ == '__main__':
    main()
