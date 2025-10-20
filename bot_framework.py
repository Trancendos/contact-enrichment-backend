class Bot:
    def __init__(self, id, skills=None):
        self.id = id
        self.skills = skills or {}

    def perform_task(self, task, context=None):
        skill = self.skills.get(task['type'])
        if skill:
            return skill(context or {})
        else:
            return f"Bot {self.id} cannot perform task type: {task['type']}"

class BotManager:
    def __init__(self, registry):
        self.registry = registry
        self.bots = {}

    def create_bot(self, bot_spec):
        bot_id = bot_spec.get('id', f'bot-{len(self.bots)+1}')
        bot = Bot(bot_id, bot_spec.get('skills'))
        self.bots[bot_id] = bot
        return bot

    def get_bot(self, bot_id):
        return self.bots.get(bot_id)

    def assign_task(self, bot_id, task, context=None):
        bot = self.get_bot(bot_id)
        if bot:
            return bot.perform_task(task, context)
        else:
            return f"No bot found with id: {bot_id}"