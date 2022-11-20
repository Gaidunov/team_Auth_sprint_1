from user_agents import parse


def get_device_from_user_agent(
    user_agent: str,
) -> str:
    user_agent = parse(user_agent)

    if user_agent.is_mobile:
        return 'mobile'

    if user_agent.is_tablet:
        return 'tablet'

    if user_agent.is_pc:
        return 'pc'

    if user_agent.is_bot:
        return 'bot'

    return 'unknown'
