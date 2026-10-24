def required_invites(bot_number: int) -> int:
    if bot_number <= 3:
        return 0
    return (bot_number - 3) * 2


def can_create_bot(bot_number: int, valid_invites: int) -> bool:
    return valid_invites >= required_invites(bot_number)