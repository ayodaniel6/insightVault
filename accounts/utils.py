def calculate_profile_completeness(user):
    score = 0
    if user.first_name:
        score += 20
    if user.last_name:
        score += 20
    if user.email:
        score += 20
    if user.bio:
        score += 20
    if user.avatar:
        score += 20
    return score
