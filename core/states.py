from aiogram.dispatcher.filters.state import StatesGroup, State


class TurnOnOffStatesGroup(StatesGroup):
    on = State()

