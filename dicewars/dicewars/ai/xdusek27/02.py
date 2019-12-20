import logging

from dicewars.ai.utils import possible_attacks, probability_of_successful_attack
from dicewars.client.ai_driver import BattleCommand, EndTurnCommand


class AI:
    def __init__(self, player_name, board, players_order):
        self.player_name = player_name
        self.logger = logging.getLogger('AI')

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):

        attacks = list(possible_attacks(board, self.player_name))

        if attacks:
            self.logger.debug("1) I can attack")

            for source, target in attacks:
                p = probability_of_successful_attack(board, source.get_name(), target.get_name())

                if p > 0.25:
                    self.logger.debug("  2) This attack is profitable")
                    return BattleCommand(source.get_name(), target.get_name())

                else:
                    self.logger.debug("  2) This attack is not profitable")
                    self.logger.debug(p)
                    break
        else:
            self.logger.debug("1) I can't attack")

        return EndTurnCommand()
