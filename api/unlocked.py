def count_unlocked_achievements(achievements: list) -> int:
    # Set counter for unlocker achievements 'unlocked' to 0
    unlocked = 0

    # count achievements stored in "achieved" within achievements array
    for x in achievements:
        if x["achieved"] == 1:
            unlocked = unlocked + 1

    return unlocked


def list_unlocked_achievements(achievements: list) -> list:
    unlocked_achievements = []

    for x in achievements:
        if x["achieved"] == 1:
            unlocked_achievements.append(x)

    return unlocked_achievements
