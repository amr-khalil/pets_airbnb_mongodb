from typing import List, Optional

import datetime

import bson

from data.bookings import Booking
from data.cages import Cage
from data.owners import Owner
from data.pets import Pet


def create_account(name: str, email: str) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email

    owner.save()

    return owner


def find_account_by_email(email: str) -> Owner:
    owner = Owner.objects(email=email).first()
    return owner


def register_cage(active_account: Owner,
                  name, allow_dangerous, has_toys,
                  carpeted, meters, price) -> Cage:
    cage = Cage()

    cage.name = name
    cage.square_meters = meters
    cage.is_carpeted = carpeted
    cage.has_toys = has_toys
    cage.allow_dangerous_pets = allow_dangerous
    cage.price = price

    cage.save()

    account = find_account_by_email(active_account.email)
    account.cage_ids.append(cage.id)
    account.save()

    return cage


def find_cages_for_user(account: Owner) -> List[Cage]:
    query = Cage.objects(id__in=account.cage_ids)
    cages = list(query)

    return cages


def add_available_date(cage: Cage,
                       start_date: datetime.datetime, days: int) -> Cage:
    booking = Booking()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=days)

    cage = Cage.objects(id=cage.id).first()
    cage.bookings.append(booking)
    cage.save()

    return cage


def add_pet(account, name, length, species, is_dangerous) -> Pet:
    pet = Pet()
    pet.name = name
    pet.length = length
    pet.species = species
    pet.is_dangerous = is_dangerous
    pet.save()

    owner = find_account_by_email(account.email)
    owner.pet_ids.append(pet.id)
    owner.save()

    return pet


def get_pets_for_user(user_id: bson.ObjectId) -> List[Pet]:
    owner = Owner.objects(id=user_id).first()
    pets = Pet.objects(id__in=owner.pet_ids).all()

    return list(pets)


def get_available_cages(checkin: datetime.datetime,
                        checkout: datetime.datetime, pet: Pet) -> List[Cage]:
    min_size = pet.length / 4

    query = Cage.objects() \
        .filter(square_meters__gte=min_size) \
        .filter(bookings__check_in_date__lte=checkin) \
        .filter(bookings__check_out_date__gte=checkout)

    if pet.is_dangerous:
        query = query.filter(allow_dangerous_pets=True)

    cages = query.order_by('price', '-square_meters')

    final_cages = []
    for c in cages:
        for b in c.bookings:
            if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_pet_id is None:
                final_cages.append(c)

    return final_cages


def book_cage(account, pet, cage, checkin, checkout):
    booking: Optional[Booking] = None

    for b in cage.bookings:
        if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_pet_id is None:
            booking = b
            break

    booking.guest_owner_id = account.id
    booking.guest_pet_id = pet.id
    booking.check_in_date = checkin
    booking.check_out_date = checkout
    booking.booked_date = datetime.datetime.now()

    cage.save()


def get_bookings_for_user(email: str) -> List[Booking]:
    account = find_account_by_email(email)

    booked_cages = Cage.objects() \
        .filter(bookings__guest_owner_id=account.id) \
        .only('bookings', 'name')

    def map_cage_to_booking(cage, booking):
        booking.cage = cage
        return booking

    bookings = [
        map_cage_to_booking(cage, booking)
        for cage in booked_cages
        for booking in cage.bookings
        if booking.guest_owner_id == account.id
    ]

    return bookings