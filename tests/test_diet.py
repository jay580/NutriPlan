from backend.services.nutrition_calculator import calculate_tdee, adjust_targets_for_goal

def test_calculate_tdee():
    # Male, 25 years old, 80kg, 180cm, moderate activity
    # BMR = 10 * 80 + 6.25 * 180 - 5 * 25 + 5 = 800 + 1125 - 125 + 5 = 1805
    # TDEE = 1805 * 1.55 = 2797.75
    tdee = calculate_tdee(25, "male", 80.0, 180.0, "moderate")
    assert abs(tdee - 2797.75) < 0.1

    # Female, 30 years old, 60kg, 165cm, sedentary activity
    # BMR = 10 * 60 + 6.25 * 165 - 5 * 30 - 161 = 600 + 1031.25 - 150 - 161 = 1320.25
    # TDEE = 1320.25 * 1.2 = 1584.3
    tdee_f = calculate_tdee(30, "female", 60.0, 165.0, "sedentary")
    assert abs(tdee_f - 1584.3) < 0.1

def test_adjust_targets_for_goal():
    # Maintain weight
    cal, prot = adjust_targets_for_goal(2500.0, 70.0, "maintain")
    assert cal == 2500
    assert prot == int(round(70.0 * 1.8))

    # Weight loss
    cal, prot = adjust_targets_for_goal(2500.0, 70.0, "lose")
    assert cal == 2000
    assert prot == int(round(70.0 * 2.0))

    # Weight gain
    cal, prot = adjust_targets_for_goal(2500.0, 70.0, "gain")
    assert cal == 3000
    assert prot == int(round(70.0 * 2.0))

