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
        return self.get_command(board)

    def get_command(self, board):

        ATTACK_HOLD_THRESHOLD = random.uniform(0.175, 0.2)

        ATTACK_WEIGHT = 0.85
        HOLD_WEIGHT = 0.15

        ATTACK_HOLD_WEIGHT = 0.5
        DIFF_WIN_WEIGHT = 0.25
        DIFF_LOSE_WEIGHT = 0.125
        LOSE_HOLD_WEIGHT = 0.125

        attack_hold_prob = []
        diff_eval_win = []
        diff_eval_lose = []
        lose_hold_prob = []

        current_eval = self.evaluate(board, self.player_name)

        for source, target in possible_attacks(board, self.player_name):

            win_board = copy.deepcopy(board)
            lose_board = copy.deepcopy(board)

            target_name_str = str(target.get_name())
            target_name_int = target.get_name()
            source_name_str = str(source.get_name())
            source_name_int = source.get_name()

            win_board.areas[target_name_str].set_owner(self.player_name)
            win_board.areas[target_name_str].set_dice(win_board.areas[source_name_str].get_dice() - 1)
            win_board.areas[source_name_str].set_dice(1)
            lose_board.areas[source_name_str].set_dice(1)

            # 1) attack_hold_prob

            attack_prob = probability_of_successful_attack(board, source_name_int, target_name_int)
            hold_prob = probability_of_holding_area(
                board, target_name_int, win_board.areas[target_name_str].get_dice(), self.player_name
            )
            attack_hold_coeff = (ATTACK_WEIGHT * attack_prob + HOLD_WEIGHT * hold_prob) / 2

            if attack_hold_coeff > ATTACK_HOLD_THRESHOLD:
                attack_hold_prob.append((source_name_int, target_name_int, attack_hold_coeff))

                # 2) diff_eval_win

                win_eval = self.evaluate(win_board, self.player_name)
                diff_eval_win_coeff = win_eval - current_eval
                diff_eval_win.append((source_name_int, target_name_int, diff_eval_win_coeff))

                # 3) diff_eval_lose

                lose_eval = self.evaluate(lose_board, self.player_name)
                diff_eval_lose_coeff = lose_eval - current_eval
                diff_eval_lose.append((source_name_int, target_name_int, diff_eval_lose_coeff))

                # 4) lose_hold_prob

                lose_hold_prob_coeff = probability_of_holding_area(
                    board, source_name_int, lose_board.areas[source_name_str].get_dice(), self.player_name
                )
                lose_hold_prob.append((source_name_int, target_name_int, lose_hold_prob_coeff))

                self.logger.debug("(" + str(source.get_dice()) + ", " + str(target.get_dice()) + ", " + str(attack_hold_coeff) +
                                  ", " + str(diff_eval_win_coeff) + ", " + str(diff_eval_lose_coeff) + ", " +
                                  str(lose_hold_prob_coeff) + ")")

        # Sorting lists

        attack_hold_prob.sort(key=lambda tup: tup[2])
        diff_eval_win.sort(key=lambda tup: tup[2])
        diff_eval_lose.sort(key=lambda tup: tup[2])
        lose_hold_prob.sort(key=lambda tup: tup[2])

        # List with possible actions

        possible_actions = []

        for source, target, attack_hold_coeff in attack_hold_prob:
            diff_win_coeff = [tup for tup in diff_eval_win if tup[0] == source and tup[1] == target][0][2]
            diff_lose_coeff = [tup for tup in diff_eval_lose if tup[0] == source and tup[1] == target][0][2]
            lose_hold_coeff = [tup for tup in lose_hold_prob if tup[0] == source and tup[1] == target][0][2]
            action_coeff = (ATTACK_HOLD_WEIGHT * attack_hold_coeff + DIFF_WIN_WEIGHT * diff_win_coeff +
                            DIFF_LOSE_WEIGHT * diff_lose_coeff + LOSE_HOLD_WEIGHT * lose_hold_coeff) / 4
            possible_actions.append((source, target, action_coeff))

        possible_actions.sort(key=lambda tup: tup[2])

        if possible_actions:
            return BattleCommand(possible_actions[0][0], possible_actions[0][1])
        else:
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

        # me:    y = sqrt(x/n)
        # enemy: y = 1 - sqrt(x/n)
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
