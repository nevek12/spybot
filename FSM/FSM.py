from aiogram.fsm.state import State, StatesGroup

class FSM(StatesGroup):
    write_user = State()
    write_location = State()
    role = State()
    playing = State()
    voiced = State()