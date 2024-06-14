import random

class KnowlegdeBase_Environment():
    """
    This class indicated an environment with the knowledge base of multiples clauses
    """
    def __init__(self):
        """
        Initialize the environment Predicates with its actions and effect of actions.

        The environment is an example for the research so only the clauses with single predicate's detail identified 
        """
        # self.educated = "educated"
        # self.partner_educated = "partner_educated"
        """
        Actions identified in this 'educated' can be understood as 
        The expected education is 200
        So when going to university, education level of university is 200
        This will fulfill your requirements
        If your expected education is 400,
        You might need 2 degrees or 1 degree and 4 long_course(s) to fulfill this
        """
        self.educated = {"goal": "educated", "status": 500, "actions": {"university": {"educated":-200}, "short_course": {"educated":-30}, "long_course":{"educated":-50}}}
        self.partner_educated = {"goal": "partner_educated", "status": 140, "actions": {"university":{"partner_educated":-100}, "library": {"partner_educated":-70}, "street": {"partner_educated":-10}}}
        self.good_work = "good_work"
        self.good_personality = "good_personality"
        self.good_children = "good_children"
        self.partner_personality = "partner_personality"
        self.good_partner = "good_partner"
        self.financial_plan = "financial_plan"
        self.wealthy = "wealthy"
        self.happy_family = "happy_family"
        self.happy_life = "happy_life" 

        #Single predicate to be a plan for GOAP is assumed by educated, partner_educated 
        # & partner_personality is indicated randomly in effect_of_environment()
        self.plans = [self.educated, self.partner_educated]

        self.environment_effect = [self.educated['goal'], self.partner_educated['goal'], self.partner_personality]
        self.environment_kb = self.generate_new_kb(self.environment_effect)

        query = f"{self.happy_life}"
        self.query = [query.title()]



    def original_kb(self):
        good_work = f"{self.educated['goal']} => {self.good_work}"
        good_personality = f"{self.educated['goal']} => {self.good_personality}"
        good_children = f"{self.educated['goal']} & {self.good_personality} => {self.good_children}"
        good_partner = f"{self.partner_personality} & {self.partner_educated['goal']} => {self.good_partner}"
        happy_family = f"{self.good_partner} & {self.good_children} => {self.happy_family}"
        financial_plan = f"{self.educated['goal']} => {self.financial_plan}"
        wealthy = f"{self.good_work} & {self.financial_plan} => {self.wealthy}"
        happy_life = f"{self.good_personality} & {self.happy_family} & {self.wealthy} => {self.happy_life}"
        original_kb = ([
            good_work,
            good_personality,
            good_children,
            good_partner,
            happy_family,
            financial_plan,
            wealthy,
            happy_life
            # ,
            # self.educated['goal'],
            # self.partner_educated['goal'],
            # self.partner_personality
        ])
        # original_kb = [kb.strip().title() for kb in original_kb]
        return original_kb
    
    def generate_new_kb(self, effect):
        knowledge_base = self.original_kb()
        effect_kb = self.effect_of_environment(effect)
        for effect in effect_kb:
            knowledge_base.append(effect)
        knowledge_base = [kb.strip().title() for kb in knowledge_base]
        return knowledge_base
   


    def effect_of_environment(self, new_kb):
        effect_kb = []
        for effect in new_kb:
            probability = random.randint(0, 1)
            if probability == 1:
                effect_kb.append(effect)
            else:
                effect = f"~{effect}"
                effect_kb.append(effect)

        return effect_kb







# KnowlegdeBase_Environment()   

    # def generate_kb(self):
    #     good_work = f"educated => good_work"
    #     good_personality = f"educated => good_personality"
    #     good_children = f"educated & good_personality => good_children"
    #     good_partner = f"partner_smart & partner_educated => good_partner"
    #     happy_family = f"good_partner & good_children => happy_family"
    #     financial_plan = f"educated => financial_plan"
    #     wealthy = f"good_work & finalcial_plan => wealthy"
    #     happy_life = f"good_personality & happy_family & wealthy => happy_life"

