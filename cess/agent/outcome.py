from enum import Enum
from collections import defaultdict
from ..util import random_choice
from .state import update_state


def update_dist(state, updates, dist):
    """@Yields to caller a tuple of (outcome-dict, probability) 
    where outcome is dict:value pairs, probblity is a float 0 to 1"""
    if callable(dist) :
        dist = dist(state) #reassign fo

    if None in [state, updates, dist]:
        return ({},1.0) 
 
    # add missing mass if necessary
    # with a "no effect" outcome
    mass = sum(dist)
    if mass < 1:
        updates.append({})
        dist.append(1 - mass)

    for update, prob in zip(updates, dist):
        yield update, prob


def outcome_dist(state, updates, dist):
    """
    @state starting state
    @updates dict of 
    yield all (expected) outcome states, with probabilities"""
    for u, p in update_dist(state, updates, dist):
        yield update_state(state, u, expected=True), p


def resolve_outcomes(state, updates, dist):
    """choose a random outcome, apply to the state,
    and return the new state"""
    update = random_choice((u, p) for u, p in update_dist(state, updates, dist))
    newState = update_state(state, update, expected=False)

    # only when resolving do we apply the special state function
    # note this does NOT re-cast or attenuate values, that is up to you
    print('x')
    if update and '~' in update:
        state.update(update['~'](state))
    return state


def expected_state(state, updates, dist):
    """computes an expected state from a given state
    over a set of possible outcomes"""
    expstate = defaultdict(list)
    for update, prob in update_dist(state, updates, dist):
        outcome_state = update_state(state, update, expected=True)
        for k, v in outcome_state.items():
            try:
                if isinstance(v, Enum):
                    expstate[k].append((v, prob))
                else:
                    expstate[k].append(v * prob)

            # for non-numerical types
            except TypeError:
                expstate[k].append((v, prob))

    for k in expstate.keys():
        try:
            expstate[k] = sum(expstate[k])

        # non-numerical types: most likely value rather than the mean
        except TypeError:
            expstate[k] = max(expstate[k], key=lambda x: x[1])[0]
    return dict(expstate)
