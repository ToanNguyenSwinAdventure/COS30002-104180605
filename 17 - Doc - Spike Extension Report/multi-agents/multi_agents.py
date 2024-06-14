from knowledge_base import KnowlegdeBase_Environment
from truth_table import TruthTable
from kb2expression import *
from goap_agent import GOAP_Agent

class MultiAgents():
    def __init__(self):
        self.executing()

    def executing(self):
        while True:
            self.environment = KnowlegdeBase_Environment()
            self.kb = self.environment.environment_kb
            self.ask = self.environment.query
            print(f"\nKnowledge base: {self.kb}")
            print(f"Query: {self.ask}")

            self.truth_table = TruthTable(self.kb, kb2expr(self.ask))
            plan = self.truth_table.get_result()
            if plan == True:
                for plan in self.environment.plans:
                    goap = GOAP_Agent(plan)
                    goap.run_until_all_goals_zero()
                break
            else:
                continue
        

MultiAgents()