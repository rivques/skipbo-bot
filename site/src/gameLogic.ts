// 0 means no card, 1-12 are the cards, 13 is the skipbo card
export type Card = number;

export interface PlayerState {
    /** up to 5 cards */
    hand: Card[];
    /** all the cards in the stock pile. index 0 is the bottom card */
    stock_pile: Card[];
    /** 4 discard piles. index 0 is the bottom card. Max 20. */
    discard_piles: Card[][];
}

export interface SkipBoAction {
    /** 0: stock pile, 1-5: hand, 6-9: discard piles */
    card_source: number;
    /** 0-3: build piles, 4-7: discard piles */
    card_destination: number;
}

export interface SkipBoLastStep {
    action: SkipBoAction;
    taken_by: number;
    was_valid: boolean;
}

export interface SkipBoState {
    player_states: PlayerState[];
    current_player: number;
    /** 4 build piles. index 0 is the bottom card */
    build_piles: Card[][];
    /** the deck of cards. index 0 is the bottom card */
    draw_pile: Card[];
    /** the completed build piles, together. */
    completed_build_piles: Card[];
    /** the number of turns taken so far */
    num_turns: number;
    /** the number of invalid actions taken in a row so far */
    invalid_actions_count: number;
    last_step?: SkipBoLastStep | null;
}

export function isActionValid(
    state: SkipBoState,
    action: SkipBoAction
): boolean {
    // check if the action is valid
    // 0: stock pile, 1-5: hand, 6-9: discard piles
    // 0-3: build piles, 4-7: discard piles
    const card_source = action.card_source
    const card_destination = action.card_destination

    const ps = state.player_states[state.current_player];
    
    let source_value = 0;
    if (card_source === 0) {
        source_value = ps.stock_pile.length > 0 ? ps.stock_pile[ps.stock_pile.length - 1] : 0;
    } else if (card_source >= 1 && card_source <= 5) {
        source_value = ps.hand[card_source - 1] || 0;
    } else if (card_source >= 6 && card_source <= 9) {
        source_value = ps.discard_piles[card_source - 6].length > 0
            ? ps.discard_piles[card_source - 6][ps.discard_piles[card_source - 6].length - 1]
            : 0;
    } else {
        return false; // invalid source
    }

    if (card_destination >= 0 && card_destination <= 3) {
        // build piles
        const dest_value = state.build_piles[card_destination].length

        if (source_value === 13) {
            // skipbo card can be placed on any build pile
            return true;
        }  else {
            return source_value === dest_value + 1;
        }
    } else if (card_destination >= 4 && card_destination <= 7) {
        return card_source >= 1 && card_source <= 5 && source_value != 0;
    } else {
        return false; // invalid destination
    }
}


export function createBaseState(numPlayers: number = 2, stock_pile_size: number = 20): SkipBoState {
    let draw_pile: Card[] = [];
    for (let i = 1; i <= 144; i++) {
        draw_pile.push(i%12+1); // 1-12
    }
    for (let i = 0; i < 18; i++) {
        draw_pile.push(13); // add skipbo cards
    }
    // shuffle the draw pile
    draw_pile = draw_pile.sort(() => Math.random() - 0.5);

    const player_states: PlayerState[] = [];
    for (let i = 0; i < numPlayers; i++) {
        player_states.push({
            hand: draw_pile.slice(-5), // 5 cards in hand
            stock_pile: draw_pile.slice(-stock_pile_size),
            discard_piles: [[], [], [], []],
        });
        draw_pile = draw_pile.slice(0, -stock_pile_size - 5); // remove the hand and stock pile cards from the draw pile
    }

    let state: SkipBoState = {
        player_states,
        current_player: 0,
        build_piles: [[], [], [], []],
        draw_pile,
        completed_build_piles: [],
        num_turns: 0,
        invalid_actions_count: 0,
        last_step: null,
    };

    return state
}

export function stepState(state: SkipBoState, action: SkipBoAction): SkipBoState {
    // TODO
}