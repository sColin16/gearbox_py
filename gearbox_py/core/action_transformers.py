from typing import Callable
from gearbox_py.core.environments import Action


class AgentAction:
    """The base class all agent actions are suggested to extend"""


ActionTransformer = Callable[[AgentAction], Action]
