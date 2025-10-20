class WorkflowEngine:
    def __init__(self, registry, bot_manager):
        self.registry = registry
        self.bot_manager = bot_manager

    def parse(self, workflow_def):
        assert 'steps' in workflow_def, "Workflow must have steps"
        return workflow_def['steps']

    def run(self, workflow_def, context):
        steps = self.parse(workflow_def)
        results = []
        for step in steps:
            if step.get("approval_required"):
                approved = self.wait_for_approval(step)
                if not approved:
                    results.append({step['type']: "Rejected"})
                    continue
            if step['type'] == 'bot':
                bot_id = step['bot_id']
                task = step['task']
                result = self.bot_manager.assign_task(bot_id, task, context)
                results.append({bot_id: result})
            elif step['type'] == 'service':
                service = self.registry.get_service(step['service_name'])
                if service:
                    result = service.endpoint(context)
                    results.append({service.name: result})
                else:
                    results.append({step['service_name']: "Service not found"})
        return results

    def wait_for_approval(self, step):
        print(f"Approval needed for {step['type']}")
        # Replace this stub with dashboard/UI logic if needed
        return True
