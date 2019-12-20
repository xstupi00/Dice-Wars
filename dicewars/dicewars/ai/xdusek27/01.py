import numpy
import logging
import random

from dicewars.ai.utils import possible_attacks
from dicewars.client.ai_driver import BattleCommand, EndTurnCommand


class AI:
    def __init__(self, player_name, board, players_order):
        self.player_name = player_name
        self.logger = logging.getLogger('AI')

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):

        attacks = list(possible_attacks(board, self.player_name))

        if attacks:
            self.logger.debug("I can attack")

            while attacks:
                if numpy.random.choice([True, False], p=[0.75, 0.25]):
                    self.logger.debug("I decided to attack")
                    source, target = random.choice(attacks)
                    self.logger.debug("    - I picked random board")
                    return BattleCommand(source.get_name(), target.get_name())

                else:
                    self.logger.debug("I decided not to attack")
                    break
        else:
            self.logger.debug("I can't attack")

        return EndTurnCommand()
