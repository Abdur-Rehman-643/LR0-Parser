from collections import defaultdict, deque

class LRParser:
    def __init__(self, grammar, terminals, non_terminals, start_symbol):
        self.grammar = grammar  # Augmented grammar with S' -> S
        self.terminals = terminals + ['$']  # Include end marker
        self.non_terminals = non_terminals
        self.start_symbol = start_symbol
        self.action_table = defaultdict(dict)
        self.goto_table = defaultdict(dict)
        self.states = []
        self.state_count = 0

    def closure(self, items):
        """
        Compute the closure of a set of LR(0) items.
        """
        closure_set = set()
        for lhs, rhs, dot_pos in items:
            closure_set.add((lhs, tuple(rhs), dot_pos))

        added = True
        while added:
            added = False
            new_items = set()
            for lhs, rhs, dot_pos in closure_set:
                if dot_pos < len(rhs):
                    next_symbol = rhs[dot_pos]
                    if next_symbol in self.non_terminals:
                        for production in self.grammar.get(next_symbol, []):
                            new_item = (next_symbol, tuple(production), 0)
                            if new_item not in closure_set:
                                new_items.add(new_item)
                                added = True
            closure_set.update(new_items)
        return closure_set

    def goto(self, items, symbol):
        """
        Compute the goto set for a set of LR(0) items and a grammar symbol.
        """
        goto_set = set()
        for lhs, rhs, dot_pos in items:
            if dot_pos < len(rhs) and rhs[dot_pos] == symbol:
                goto_set.add((lhs, tuple(rhs), dot_pos + 1))
        return self.closure(goto_set)

    def items(self):
        """
        Construct the canonical LR(0) collection of item sets.
        """
        initial_item = (self.start_symbol, tuple(self.grammar[self.start_symbol][0]), 0)
        initial_state = self.closure([initial_item])
        self.states.append(initial_state)

        states_queue = deque([initial_state])
        state_mapping = {frozenset(initial_state): 0}

        while states_queue:
            state = states_queue.popleft()
            state_index = state_mapping[frozenset(state)]

            for symbol in self.terminals + self.non_terminals:
                next_state = self.goto(state, symbol)
                if next_state:
                    next_state_frozen = frozenset(next_state)
                    if next_state_frozen not in state_mapping:
                        self.state_count += 1
                        state_mapping[next_state_frozen] = self.state_count
                        states_queue.append(next_state)
                        self.states.append(next_state)
                    next_state_index = state_mapping[next_state_frozen]
                    if symbol in self.terminals:
                        self.action_table[state_index][symbol] = ('shift', next_state_index)
                    else:
                        self.goto_table[state_index][symbol] = next_state_index

        # Add reduce and accept actions
        for i, state in enumerate(self.states):
            for lhs, rhs, dot_pos in state:
                if dot_pos == len(rhs):  # This is a complete production
                    if lhs == self.start_symbol:
                        self.action_table[i]['$'] = ('accept',)
                    else:
                        production_index = self.get_production_index(lhs, rhs)
                        for terminal in self.follow(lhs):
                            self.action_table[i][terminal] = ('reduce', lhs, rhs)

    def get_production_index(self, lhs, rhs):
        """
        Helper function to get the index of the production A -> β in the grammar.
        """
        for index, production in enumerate(self.grammar[lhs]):
            if tuple(production) == rhs:
                return index
        return -1

    def follow(self, non_terminal):
        """
        Compute the FOLLOW set of a non-terminal.
        """
        follow_set = set()
        if non_terminal == self.start_symbol:
            follow_set.add('$')
        for lhs, productions in self.grammar.items():
            for production in productions:
                for i, symbol in enumerate(production):
                    if symbol == non_terminal:
                        if i + 1 < len(production):
                            next_symbol = production[i + 1]
                            if next_symbol in self.terminals:
                                follow_set.add(next_symbol)
                            else:
                                follow_set.update(self.first(next_symbol))
                        else:
                            follow_set.update(self.follow(lhs))
        return follow_set

    def first(self, non_terminal):
        """
        Compute the FIRST set of a non-terminal.
        """
        first_set = set()
        for production in self.grammar[non_terminal]:
            if production[0] in self.terminals:
                first_set.add(production[0])
            else:
                first_set.update(self.first(production[0]))
        return first_set

    def format_stack(self, stack):
        """
        Helper function to format the stack for output.
        """
        return ''.join(map(str, stack))

    def format_input(self, input_string, index):
        """
        Helper function to format the input string for output.
        """
        return ''.join(input_string[index:])

    def print_closure_sets(self):
        """
        Print closure sets for all the states.
        """
        print("Closure Sets:")
        for idx, state in enumerate(self.states):
            print(f"I{idx}:")
            for lhs, rhs, dot_pos in state:
                rhs_with_dot = list(rhs)
                rhs_with_dot.insert(dot_pos, ".")
                print(f"  {lhs} -> {' '.join(rhs_with_dot)}")
            print()

    def print_action_goto_tables(self):
        """
        Print the action and goto tables.
        """
        print("\nAction Table:")
        headers = ["State"] + self.terminals
        print(f"{'State':<10} {' '.join(f'{term:<10}' for term in self.terminals)}")
        for state in sorted(self.action_table.keys()):
            actions = [self.action_table[state].get(term, ' ') for term in self.terminals]
            action_str = ' '.join(f"{action[0]}{action[1] if len(action) > 1 else '':<9}" for action in actions)
            print(f"{state:<10} {action_str}")

        print("\nGoto Table:")
        headers = ["State"] + self.non_terminals
        print(f"{'State':<10} {' '.join(f'{nt:<10}' for nt in self.non_terminals)}")
        for state in sorted(self.goto_table.keys()):
            gotos = [self.goto_table[state].get(nt, ' ') for nt in self.non_terminals]
            goto_str = ' '.join(f"{goto:<10}" for goto in gotos)
            print(f"{state:<10} {goto_str}")

    def parse(self, input_string):
        """
        Perform LR parsing on the input string with formatted output.
        """
        input_string = list(input_string) + ['$']
        stack = [0]  # Initialize stack with state 0
        index = 0

        print(f"{'Stack':<12}{'Input':<12}{'Action':<20}{'Output'}")

        while True:
            state = stack[-1]
            current_symbol = input_string[index]

            if current_symbol not in self.action_table[state]:
                raise SyntaxError(f"Syntax error at position {index}: {current_symbol}")

            action = self.action_table[state][current_symbol]

            # Print current stack, input, and action
            print(f"{self.format_stack(stack):<12}{self.format_input(input_string, index):<12}", end="")

            if action[0] == 'shift':
                stack.append(current_symbol)
                stack.append(action[1])
                print(f"shift {action[1]:<17}")
                index += 1

            elif action[0] == 'reduce':
                lhs, rhs = action[1], action[2]
                for _ in range(2 * len(rhs)):
                    stack.pop()  # Pop symbols and states
                stack.append(lhs)
                goto_state = self.goto_table[stack[-2]][lhs]
                stack.append(goto_state)

                # Print the reduce output
                print(f"reduce by {lhs}→{' '.join(rhs):<10}", end="")
                print(f"{lhs}→{' '.join(rhs)}")

            elif action[0] == 'accept':
                print("accept")
                return True
            else:
                raise SyntaxError(f"Unexpected action: {action}")

if __name__ == "__main__":
    grammar = {
        "S'": [["S"]],
        'S': [['E']],
        'E': [['E', '+', 'T'], ['T']],
        'T': [['T', '*', 'F'], ['F']],
        'F': [['(', 'E', ')'], ['id']]
    }

    terminals = ['+', '*', '(', ')', 'id']
    non_terminals = ['S', 'E', 'T', 'F']
    start_symbol = "S'"

    parser = LRParser(grammar, terminals, non_terminals, start_symbol)
    parser.items()

    # Print closure sets
    parser.print_closure_sets()

    # Print action and goto tables
    parser.print_action_goto_tables()

    # Parse the input string with formatted output
    parser.parse(['id', '*', 'id', '+', 'id'])
