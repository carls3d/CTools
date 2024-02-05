# This is an example showing how the AccumulateField node in Geometry Nodes work

# Example:
# Consider an analogy of a "Player" in a "Game" where the "Player" has a "Score" and is part of a "Team"
# In this context: 
#   Each "Team" is a "Field"
#   The "Player" "Score" is the "Value" of each "Element" in the "Field"
#   "Team"      -> "Player"     -> "Score"
#   "Field"     -> "Element"    -> "Value"

# GroupID -> Group of Fields -> Group of "Teams"        Each "ID" is a "Team"
# Value == ElementValue == "Players""Score"             Each "Value" is a "Players""Score" in this example

# GroupID = What "Team" a "Player" is on -> The teams are separate "Fields"
# Value = The "Score" of the "Player"
# GroupID = [
#     1, 1, 1,   Team "1"
#     3, 3, 3    Team "3"
# ]
# Value = [
#     1, 1, 1,   Team "1"
#     4, 0, 1    Team "3"
# ]

# The accumulative total, starting at the first value
# Leading = [ 
#     1, 2, 3,   Team "1"   # 1, 1 + 1, 1 + 1 + 1
#     4, 4, 5    Team "3"   # 4, 4 + 0, 4 + 0 + 1
# ]
# The accumulative total, starting at zero
# Trailing = [ 
#     0, 1, 2,   Team "1"   # 0, 0 + 1, 0 + 1 + 1
#     0, 4, 4    Team "3"   # 0, 0 + 4, 0 + 4 + 0
# ]
# The accumulative total "Score" for each "Team", represented by every "Player"
# Total = [
#     3, 3, 3,   Team "1"    # 0 + 2 + 1 = 3
#     5, 5, 5    Team "3"    # 4 + 0 + 1 = 5
# ]

class AccumulateField:
    """
    Accumulates values either within groups defined by GroupID or sequentially.

    ---
    ## Attributes
    Value : int, float, list
        The values to accumulate
    GroupID : list, int, range, optional
        Optional group identifiers
    
    ---
    ## Methods
    leading():
        Computes the leading accumulation for each group.
    trailing():
        Computes the trailing values for each group.
    total():
        Computes the total accumulation for each group.

    ---
    ## Examples
    >>> Value = [1, 2, 3, 4, 5, 6]
    >>> GroupID = [1, 1, 1, 2, 2, 2]
    >>> acc = AccumulateField(Value, GroupID)
    >>> acc.leading()
    [1, 3, 6, 4, 9, 15]
    
    ---
    #
    >>> Value = [1, 2, 3, 4, 5, 6]
    >>> GroupID = None
    >>> acc = AccumulateField(Value)
    >>> acc.leading()
    [1, 3, 6, 10, 15, 21]
    
    ---
    #
    >>> Value = 5
    >>> GroupID = [1, 1, 1, 2, 2, 2]
    >>> acc = AccumulateField(Value, GroupID)
    >>> acc.leading()
    [5, 10, 15, 5, 10, 15]
    """
    def __init__(self, Value: int | float | list, GroupID: list | int | range = None):
        if not (isinstance(Value, list) or isinstance(GroupID, list)):
            raise TypeError("Either Value or GroupID must be a list")
        
        self.Value = Value if isinstance(Value, list) else [Value] * len(GroupID)
        self.GroupID = (
            GroupID if isinstance(GroupID, list) else 
            [1] * (len(GroupID) if isinstance(GroupID, range) else GroupID or len(Value))
        )
        
        self.group_totals = {}
        self.leading_values = []
        self.trailing_values = []
        self.total_values = {}

    def leading(self):
        if self.leading_values:
            return self.leading_values
        for value, group_index in zip(self.Value, self.GroupID):
            self.group_totals[group_index] = self.group_totals.get(group_index, 0) + value
            self.leading_values.append(self.group_totals[group_index])
            self.total_values[group_index] = self.group_totals[group_index]
        return self.leading_values

    def trailing(self):
        if not self.leading_values: self.leading()
        self.trailing_values = [lead - val for lead, val in zip(self.leading_values, self.Value)]
        return self.trailing_values

    def total(self):
        if not self.total_values: self.leading()
        return [self.total_values[g] for g in self.GroupID]

    def __repr__(self) -> str:
        return f"\nLeading:\n{self.leading()}\n\nTrailing:\n{self.trailing()}\n\nTotal:\n{self.total()}\n"

Scores = [1, 1, 1, 
          4, 0, 1]
Teams = [1, 1, 1,
         3, 3, 3]
TeamsExample = AccumulateField(Scores, Teams)
print("---- Teams Example ----")
print(TeamsExample)
print()

def group_reindex(GroupID:list) -> list:
    """Re-indexing elements based on their group accumulation"""
    af1 = AccumulateField(1, GroupID)
    af1_trailing = af1.trailing()
    af1_total = af1.total()
    
    af2 = AccumulateField(af1_total, af1_trailing)
    af2_trailing = af2.trailing()
    return [a+b for a,b in zip(af1_trailing, af2_trailing)]

def Example1():
    print("---- Test 1 ----")
    # Example: Elements with the same ID are re-indexed sequentially, following the previous group's total
    # "10" Original Index: 0, 3, 6, 9, 12   ->  Re-Index:   0, 1, 2, 3, 4
    # "18" Original Index: 1, 4, 7, 10, 13  ->  Re-Index:   5, 6, 7, 8, 9
    # "82" Original Index: 2, 5, 8, 11, 14  ->  Re-Index:   10, 11, 12, 13, 14
    isl_ind = [10, 18, 82, 10, 18, 82, 10, 18, 82, 10, 18, 82, 10, 18, 82]
    indices = [i for i in range(len(isl_ind))]
    x = group_reindex(isl_ind)
    print(f"Re-Index:\n{x}")
    print(indices)
    print(group_reindex(isl_ind))
    print()

def Example2():
    from math import pi
    print("---- Test 2 ----")
    indices = range(15)
    print(pi)
    a = 0.5
    b = 2 * pi
    acc1 = AccumulateField(a, [1 for i in indices])
    print(acc1)
    x_lead = [i+b for i in acc1.leading()]
    # print(x_lead)
    acc2 = AccumulateField(x_lead, [1 for i in indices])
    # print(acc2)

def Example3():
    print("---- Test 3 ----")
    val = 3
    grp = [1, 1, 1, 2, 2, 2]
    acc = AccumulateField(val, grp)
    print(acc)
    
    
Example1()
Example2()
Example3()