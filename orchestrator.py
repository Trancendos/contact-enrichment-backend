from service_registry import ServiceRegistry
from bot_framework import BotManager
from workflow_engine import WorkflowEngine
from adaptive_learning import AdaptiveLearning

class Orchestrator:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.bot_manager = BotManager(self.registry)
        self.workflow_engine = WorkflowEngine(self.registry, self.bot_manager)
        self.adaptive_learning = AdaptiveLearning(self.registry)

    def register_service(self, service):
        self.registry.register(service)

    def create_bot(self, bot_spec):
        return self.bot_manager.create_bot(bot_spec)

    def run_workflow(self, workflow_def, context=None):
        results = self.workflow_engine.run(workflow_def, context or {})
        self.adaptive_learning.submit_feedback("workflow", results, True)
        return results

    def health_check(self):
        return self.registry.health_report()