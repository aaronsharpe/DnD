"""
Dnd_melee_accack is for performing melee attacks in DnD as well as returning
statistics for given melee attack input parameters
"""

from collections import namedtuple
import numpy as np

AttackResults = namedtuple('AttackResults',
                           'label to_hit_dice hit crit rolled_dmg_dice dmg')
def melee_attack(armor_class, label=None, dmg_die=6, num_dmg_dice=1, hit_mod=0,
                 dmg_mod=0, bonus_crit_dice=0, advantage=False,
                 disadvantage=False, crit_19=False, reroll=False, gwm=False,
                 randint=np.random.randint):
    """
    Check to see if a melee attack against a given armor_class will hit then
    perform the attack

    Arguments:
        armor_class: armor class to check hit against
        dmg_die: the size of the damage die that will be rolled
        num_dmg_dice: the number of hit die that will be rolled for damage
        hit_mod: added modifier when making attacks
        dmg_mod: added modifier to damage
        bonus_crit_die: additional hit dice awarded on a critical hit
        advantage: roll to hit twice and take the max result
        disadvantage: roll to hit twice and take the min result
        crit_19: A to hit roll of 19 counts as a critical
        reroll: When rolling damage, reroll 1's and 2's once
        gwm: incorperates great weapon master feat, -5 to hit and +10 to dmg
    """

    # Roll to_hit dice according to adv/dis/neutral
    if advantage:
        to_hit_dice = randint(1, 21, size=2)
        to_hit = np.max(to_hit_dice)
    elif disadvantage:
        to_hit_dice = randint(1, 21, size=2)
        to_hit = np.min(to_hit_dice)
    else:
        to_hit_dice = randint(1, 21)
        to_hit = to_hit_dice

    # Check if the attack hits
    if to_hit == 20 or (to_hit == 19 and crit_19):
        hit = True
        crit = True
    elif to_hit == 1:
        hit = False
        crit = False
    else:
        hit = to_hit + hit_mod - (5 if gwm else 0) >= armor_class
        crit = False

    rolled_dmg_dice = []

    # If crit/hit, roll dmg dice
    if crit:
        rolled_dmg_dice = np.random.randint(1, dmg_die + 1, size=
                                            2*num_dmg_dice + bonus_crit_dice)
    elif hit:
        rolled_dmg_dice = np.random.randint(1, dmg_die + 1, size=num_dmg_dice)

    # For great weapon fighter, reroll any 1's and 2's
    if hit and reroll:
        for i, die in enumerate(rolled_dmg_dice):
            if die <= 2:
                rolled_dmg_dice[i] = np.random.randint(1, dmg_die + 1)

    dmg = np.sum(rolled_dmg_dice)

    if hit:
        dmg += dmg_mod

    if gwm and hit:
        dmg += 10

    return AttackResults(label, to_hit_dice, hit, crit, rolled_dmg_dice, dmg)


AttackStats = namedtuple('AttackStats',
                         'label, hit_chance crit_chance dmg_mean dmg_per_round')
def melee_stats(iters, armor_classes, label=None, num_attacks=1, dmg_die=6,
                num_dmg_dice=1, dmg_mod=0, bonus_crit_dice=0, advantage=False,
                disadvantage=False, crit_19=False, reroll=False, gwm=False):
    """
    Returns statistics a melee attack against armor_classes

    Arguments:
        iters: numbers of times to try attacking armor_class
        armor_classes: list of armor_classes to calculate stats against
        num_attacks: number of times each attack is performed
    """

    hit_chance_stats = []
    crit_chance_stats = []
    dmg_mean_stats = []
    dmg_per_round_stats = np.empty([len(armor_classes), iters])

    for i, armor_class in enumerate(armor_classes):
        hit_store = np.empty(iters)
        crit_store = np.empty(iters)
        dmg_store = np.empty(iters)

        for j in range(iters):
            attack = melee_attack(armor_class, label=label, dmg_die=dmg_die,
                                  num_dmg_dice=num_dmg_dice, dmg_mod=dmg_mod,
                                  bonus_crit_dice=bonus_crit_dice,
                                  advantage=advantage, disadvantage=disadvantage,
                                  crit_19=crit_19, reroll=reroll, gwm=gwm)

            hit_store[j] = attack.hit
            crit_store[j] = attack.crit
            dmg_store[j] = attack.dmg

        hit_chance = sum(hit_store)/len(hit_store)
        crit_chance = sum(crit_store)/len(crit_store)
        dmg_mean = num_attacks * np.mean(dmg_store)

        # Resample for calculating histograms of n attacks per round
        dmg_per_round = dmg_store.copy()
        for _ in range(num_attacks-1):
            dmg_per_round += np.random.choice(dmg_store, iters)

        hit_chance_stats.append(hit_chance)
        crit_chance_stats.append(crit_chance)
        dmg_mean_stats.append(dmg_mean)
        dmg_per_round_stats[i, :] = dmg_per_round

    return AttackStats(label, hit_chance_stats, crit_chance_stats,
                       dmg_mean_stats, dmg_per_round_stats)
