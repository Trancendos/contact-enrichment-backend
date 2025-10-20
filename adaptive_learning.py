class AdaptiveLearning:
    def __init__(self, registry):
        self.registry = registry
        self.feedback_data = []

    def submit_feedback(self, agent_id, result, success):
        self.feedback_data.append({"agent_id": agent_id, "result": result, "success": success})

    def retrain_agents(self):
        for agent in self.registry.services.values():
            if hasattr(agent, "retrain"):
                agent.retrain(self.feedback_data)