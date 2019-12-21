import logging
import copy
import math
import random

from dicewars.ai.utils import possible_attacks, probability_of_successful_attack, probability_of_holding_area
from dicewars.client.ai_driver import BattleCommand, EndTurnCommand


class AI:
    """ Expected Mini-Max
    """

    def __init__(self, player_name, board, players_order):
        self.player_name = player_name
        self.players_order = players_order
        self.logger = logging.getLogger('AI')

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        EVAL_WEIGHT = 0.24
        SUCC_WEIGHT = 0.60
        HOLD_WEIGHT = 0.08
        LOSE_WEIGHT = 0.08

        PENALTY_EVAL_WEIGHT = 0.75
        PENALTY_HOLD_WEIGHT = 0.25

        ATTACK_TRESHOLD = random.uniform(0.07, 0.08)

        max_attack_coeff = -1000

        best_source = 0
        best_target = 0

        for source, target in possible_attacks(board, self.player_name):
            win_board = copy.deepcopy(board)

            win_board.areas[str(target.get_name())].set_owner(self.player_name)
            win_board.areas[str(target.get_name())].set_dice(win_board.areas[str(source.get_name())].get_dice() - 1)
            win_board.areas[str(source.get_name())].set_dice(1)

            lose_board = copy.deepcopy(board)
            lose_board.areas[str(source.get_name())].set_dice(1)

            successful_attack_probability = probability_of_successful_attack(
                board, source.get_name(), target.get_name()
            )
            holding_attack_area_probability = probability_of_holding_area(
                board, target.get_name(), win_board.areas[str(target.get_name())].get_dice(), self.player_name
            )

            holding_source_probability = probability_of_holding_area(
                board, source.get_name(), lose_board.areas[str(source.get_name())].get_dice(), self.player_name
            )

            win_board_evaluation = self.evaluate(win_board, self.player_name)
            lose_board_evaluation = self.evaluate(lose_board, self.player_name)

            # more is better
            lose_penalty = (PENALTY_EVAL_WEIGHT * lose_board_evaluation +
                            PENALTY_HOLD_WEIGHT * holding_source_probability) / 2

            # more is better
            attack_coeff = (EVAL_WEIGHT * win_board_evaluation + SUCC_WEIGHT * successful_attack_probability +
                            HOLD_WEIGHT * holding_attack_area_probability + LOSE_WEIGHT * lose_penalty) / 4

            self.logger.debug("source: " + str(source.get_dice()) + "   target: " + str(target.get_dice()) +
                              "  attack_coeff = " + str(attack_coeff) + "   eval = " + str(win_board_evaluation) +
                              "   attack_prob = " + str(successful_attack_probability) + "  hold_prob = " +
                              str(holding_attack_area_probability) + "  lose = " + str(lose_penalty))

            if attack_coeff > max_attack_coeff:
                max_attack_coeff = attack_coeff
                best_source = source
                best_target = target

        if max_attack_coeff > ATTACK_TRESHOLD:
            self.logger.debug("best_source = " + str(best_source.get_name()) + ", " + str(best_source.get_dice()))
            self.logger.debug("best_target = " + str(best_target.get_name()) + ", " + str(best_target.get_dice()))
            self.logger.debug("max_attack_coeff = " + str(max_attack_coeff))
            return BattleCommand(best_source.get_name(), best_target.get_name())

        return EndTurnCommand()

    def evaluate(self, board, player_name):
        """ Evaluate the state of the game from the player perspective
        """
        SCORE_WEIGHT = 9 / 20
        DICES_WEIGHT = 1 / 20

        max_score = len(board.areas)
        total_dices = sum([board.get_player_dice(player) for player in self.players_order])
        player_dices = board.get_player_dice(player_name)
        player_score = self.get_score_by_player(board, self.player_name)

        enemies = {}
        for enemy in self.players_order:
            if enemy != player_name:
                score = self.get_score_by_player(board, enemy)
                dices = board.get_player_dice(enemy)
                enemies[enemy] = {"score": score, "dices": dices}

        enemies_score = sum(enemy["score"] for enemy in enemies.values())
        enemies_dices = sum(enemy["dices"] for enemy in enemies.values())

        evaluation = (SCORE_WEIGHT * math.sqrt((player_score / max_score) / max_score) +
                      DICES_WEIGHT * math.sqrt((player_dices / total_dices) / 8 * max_score) +
                      SCORE_WEIGHT * (1 - math.sqrt((enemies_score / max_score) / max_score)) +
                      DICES_WEIGHT * (1 - math.sqrt((enemies_dices / total_dices) / 8 * max_score))) / 4

        return evaluation

    def get_score_by_player(self, board, player_name, skip_area=None):
        """Get score of the player in the board
        """
        players_regions = board.get_players_regions(player_name, skip_area=skip_area)
        max_region_size = max(len(region) for region in players_regions)

        return max_region_size
