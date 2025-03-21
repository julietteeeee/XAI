import re

def format_text(text):
    """ Converts camelCase and snake_case to readable text. """
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Convert camelCase
    text = text.replace("_", " ")  # Convert snake_case
    return text.lower()

def generate_natural_language_explanation(goal, preferences, norm, beliefs, executed_actions, formal_explanation, action_to_explain):
    """
    Generates a human-friendly, easy-to-understand explanation of the AI's decision-making process.
    """
    explanation = []

    # Step 1: Provide Context
    explanation.append(f"The AI agent was instructed to achieve the goal: {format_text(goal[0]).capitalize()}.")
    
    # Convert beliefs into natural language
    belief_statements = []
    for belief in beliefs:
        formatted_belief = format_text(belief)
        if "available" in formatted_belief:
            formatted_belief = "there is a " + formatted_belief.replace("available", "available")
        elif "own" in formatted_belief:
            formatted_belief = "owns a " + formatted_belief.replace("own", "")
        elif "have" in formatted_belief:
            formatted_belief = "there is a " + formatted_belief.replace("have", "")
        belief_statements.append(formatted_belief.strip())
    explanation.append(f"The agent knows that {', '.join(belief_statements)}.")
    
    # Convert norms innto more readable form
    if norm:
        norm_type = "prohibited" if norm["type"] == "P" else "required"
        norm_actions = ', '.join([format_text(action) for action in norm['actions']])
        explanation.append(f"According to the given norms, the action(s) {norm_actions} are {norm_type}.")

    # Step 2: Explain the Decision-Making Process
    formatted_actions = [format_text(action) for action in executed_actions]
    explanation.append(f"To achieve the goal, the agent completed the following actions: {', '.join(formatted_actions)}.")

    for factor in formal_explanation:
        factor_type = factor[0]
        if factor_type == 'P':  # Precondition
            explanation.append(f"The action '{format_text(factor[1])}' was possible because {', '.join([format_text(cond) for cond in factor[2]])} were met.")
        elif factor_type == 'C':  # Choice made at an OR node
            explanation.append(f"The agent chose '{format_text(factor[1])}' because the conditions {', '.join([format_text(cond) for cond in factor[2]])} were satisfied.")
        elif factor_type == 'V':  # Value-based comparison
            explanation.append(f"'{format_text(factor[1])}' was chosen over '{format_text(factor[4])}' because it had lower costs: {factor[2]} vs {factor[5]}.")
        elif factor_type == 'N':  # Norm violation avoidance
            norm_text = factor[2]
    
            # Convert norm notation to human-friendly English
            if norm_text.startswith("P(") and norm_text.endswith(")"):  # Prohibition
                norm_action = format_text(norm_text[2:-1])  # Extract action name
                norm_text = f"it is prohibited to {norm_action}"
            elif norm_text.startswith("O(") and norm_text.endswith(")"):  # Obligation
                norm_action = format_text(norm_text[2:-1])  # Extract action name
                norm_text = f"it is required to {norm_action}"
    
            explanation.append(f"'{format_text(factor[1])}' was not chosen because {norm_text}.")
        
        elif factor_type == 'F':  # Failed condition
            explanation.append(f"'{format_text(factor[1])}' could not be chosen because {', '.join([format_text(cond) for cond in factor[2]])} were not met.")
        elif factor_type == 'L':  # Link dependency
            explanation.append(f"'{format_text(factor[1])}' was necessary because it enabled '{format_text(factor[3])}'.")
        elif factor_type == 'D':  # Goal node
            explanation.append(f"The action '{format_text(action_to_explain)}' was necessary to fulfill the goal '{format_text(factor[1])}'.")
        elif factor_type == 'U':  # User preference
            preference_order = ", ".join([preferences[0][i] for i in preferences[1]])
            explanation.append(f"The decision was made considering the user’s preference order: {preference_order}.")

    # Step 3: Conclusion
    explanation.append(f"Therefore, the agent decided to perform '{format_text(action_to_explain)}' because it best aligned with the given conditions, preferences, and constraints.")

    return "\n".join(explanation)

### TEST

goal = ["haveCoffee"]
preferences = [["quality", "price", "time"], [1, 2, 0]]
norm = {"type": "P", "actions": ["payShop"]}
beliefs = ["staffCardAvailable", "ownCard", "colleagueAvailable", "haveMoney"]
executed_actions = ["getCoffee", "getKitchenCoffee", "getStaffCard", "getOwnCard", "gotoKitchen", "getCoffeeKitchen"]
formal_explanation = [
    ['C', 'getKitchenCoffee', ['staffCardAvailable']],
    ['V', 'getKitchenCoffee', [5.0, 0.0, 3.0], '>', 'getAnnOfficeCoffee', [2.0, 0.0, 6.0]],
    ['N', 'getShopCoffee', 'P(payShop)'],
    ['C', 'getOwnCard', ['ownCard']],
    ['V', 'getOwnCard', [0.0, 0.0, 0.0], '>', 'getOthersCard', [0.0, 0.0, 2.0]],
    ['P', 'getOwnCard', ['ownCard']],
    ['P', 'getCoffeeKitchen', ['haveCard', 'atKitchen']],
    ['D', 'getKitchenCoffee'],
    ['D', 'getCoffee'],
    ['U', [["quality", "price", "time"], [1, 2, 0]]]
]
action_to_explain = "getCoffeeKitchen"

# Call the function and print the result
explanation = generate_natural_language_explanation(
    goal, preferences, norm, beliefs, executed_actions, formal_explanation, action_to_explain
)

print(explanation)


"""###TEST2

goal = ["orderFood"]
preferences = [["price", "speed", "quality"], [0, 1, 2]]
norm = {"type": "O", "actions": ["useApp"]}
beliefs = ["havePhone", "haveMoney"]
executed_actions = ["openApp", "chooseMeal", "payOnline", "confirmOrder"]
formal_explanation = [
    ['C', 'openApp', ['havePhone']],
    ['N', 'callRestaurant', 'O(useApp)'],
    ['P', 'payOnline', ['haveMoney']],
    ['D', 'orderFood'],
    ['U', [["price", "speed", "quality"], [0, 1, 2]]]
]
action_to_explain = "payOnline"

# Call the function and print the result
explanation = generate_natural_language_explanation(
    goal, preferences, norm, beliefs, executed_actions, formal_explanation, action_to_explain
)

print(explanation)"""
