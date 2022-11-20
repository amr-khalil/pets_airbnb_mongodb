import datetime
from dateutil import parser

from infrastructure.switchlang import switch
import program_hosts as hosts
import services.data_service as svc
from program_hosts import success_msg, error_msg
import infrastructure.state as state


def run():
    print(' ****************** Welcome guest **************** ')
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        with switch(action) as s:
            s.case('c', hosts.create_account)
            s.case('l', hosts.log_into_account)

            s.case('a', add_a_pet)
            s.case('y', view_your_pets)
            s.case('b', book_a_cage)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')

            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], hosts.exit_app)

            s.default(hosts.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a cage')
    print('[A]dd a pet')
    print('View [y]our pets')
    print('[V]iew your bookings')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_pet():
    print(' ****************** Add a pet **************** ')
    if not state.active_account:
        error_msg("You must log in first to add a pet")
        return

    name = input("What is your pet's name? ")
    if not name:
        error_msg('cancelled')
        return

    length = float(input('How long is your pet (in meters)? '))
    species = input("Species? ")
    is_dangerous = input("Is your pet venomous [y]es, [n]o? ").lower().startswith('y')

    pet = svc.add_pet(state.active_account, name, length, species, is_dangerous)
    state.reload_account()
    success_msg('Created {} with id {}'.format(pet.name, pet.id))


def view_your_pets():
    print(' ****************** Your pets **************** ')
    if not state.active_account:
        error_msg("You must log in first to view your pets")
        return

    pets = svc.get_pets_for_user(state.active_account.id)
    print("You have {} pets.".format(len(pets)))
    for s in pets:
        print(" * {} is a {} that is {}m long and is {}venomous.".format(
            s.name,
            s.species,
            s.length,
            '' if s.is_dangerous else 'not '
        ))


def book_a_cage():
    print(' ****************** Book a cage **************** ')
    if not state.active_account:
        error_msg("You must log in first to book a cage")
        return

    pets = svc.get_pets_for_user(state.active_account.id)
    if not pets:
        error_msg('You must first [a]dd a pet before you can book a cage.')
        return

    print("Let's start by finding available cages.")
    start_text = input("Check-in date [yyyy-mm-dd]: ")
    if not start_text:
        error_msg('cancelled')
        return

    checkin = parser.parse(
        start_text
    )
    checkout = parser.parse(
        input("Check-out date [yyyy-mm-dd]: ")
    )
    if checkin >= checkout:
        error_msg('Check in must be before check out')
        return

    print()
    for idx, s in enumerate(pets):
        print('{}. {} (length: {}, venomous: {})'.format(
            idx + 1,
            s.name,
            s.length,
            'yes' if s.is_dangerous else 'no'
        ))

    pet = pets[int(input('Which pet do you want to book (number)')) - 1]

    cages = svc.get_available_cages(checkin, checkout, pet)

    print("There are {} cages available in that time.".format(len(cages)))
    for idx, c in enumerate(cages):
        print(" {}. {} with {}m carpeted: {}, has toys: {}.".format(
            idx + 1,
            c.name,
            c.square_meters,
            'yes' if c.is_carpeted else 'no',
            'yes' if c.has_toys else 'no'))

    if not cages:
        error_msg("Sorry, no cages are available for that date.")
        return

    cage = cages[int(input('Which cage do you want to book (number)')) - 1]
    svc.book_cage(state.active_account, pet, cage, checkin, checkout)

    success_msg('Successfully booked {} for {} at ${}/night.'.format(cage.name, pet.name, cage.price))


def view_bookings():
    print(' ****************** Your bookings **************** ')
    if not state.active_account:
        error_msg("You must log in first to register a cage")
        return

    pets = {s.id: s for s in svc.get_pets_for_user(state.active_account.id)}
    bookings = svc.get_bookings_for_user(state.active_account.email)

    print("You have {} bookings.".format(len(bookings)))
    for b in bookings:
        # noinspection PyUnresolvedReferences
        print(' * Pet: {} is booked at {} from {} for {} days.'.format(
            pets.get(b.guest_pet_id).name,
            b.cage.name,
            datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day),
            (b.check_out_date - b.check_in_date).days
        ))